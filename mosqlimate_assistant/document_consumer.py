import hashlib
import json
import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
import requests
import requests_cache

from mosqlimate_assistant.models import SourceDocument, VectorDocument
from mosqlimate_assistant.settings import (
    HTTP_CACHE_DIR,
    HTTP_CACHE_ENABLED,
    HTTP_CACHE_TTL_SECONDS,
)
from mosqlimate_assistant.vector_store import BaseVectorStore

_cached_session: Optional[
    Union[requests.Session, requests_cache.CachedSession]
] = None


def get_cached_session() -> (
    Union[requests.Session, requests_cache.CachedSession]
):
    global _cached_session

    if _cached_session is None:
        if HTTP_CACHE_ENABLED:
            Path(HTTP_CACHE_DIR).mkdir(parents=True, exist_ok=True)

            _cached_session = requests_cache.CachedSession(
                cache_name=str(Path(HTTP_CACHE_DIR) / "http_cache"),
                backend="sqlite",
                expire_after=timedelta(seconds=HTTP_CACHE_TTL_SECONDS),
                allowable_codes=[200],
                allowable_methods=["GET"],
                stale_if_error=True,
            )
        else:
            _cached_session = requests.Session()

    return _cached_session


# ─── Processamento de conteúdo ───────────────────────────────────


def _process_notebook(raw_json: str) -> str:
    """Converte JSON de Jupyter Notebook em markdown legível."""
    try:
        notebook = json.loads(raw_json)
    except json.JSONDecodeError:
        return raw_json

    lang = (
        notebook.get("metadata", {})
        .get("kernelspec", {})
        .get("language", "python")
    )

    parts: list[str] = []
    for cell in notebook.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            parts.append(source)
        elif cell.get("cell_type") == "code":
            parts.append(f"```{lang}\n{source}\n```")

    return "\n\n".join(parts)


def _resolve_includes(
    content: str,
    base_url: str,
    session: Union[requests.Session, requests_cache.CachedSession],
) -> str:
    """Resolve referências --8<-- 'file' do mkdocs."""
    for match in re.finditer(r'--8<-- "([^"]+)"', content):
        include_path = match.group(1)
        try:
            resp = session.get(base_url + include_path)
            resp.raise_for_status()
            content = content.replace(match.group(0), resp.text)
        except Exception:
            pass
    return content


def _resolve_mkdocstrings(
    content: str,
    base_url: str,
    session: Union[requests.Session, requests_cache.CachedSession],
) -> str:
    """Resolve referências ::: module.path do mkdocstrings."""
    for match in re.finditer(r"::: ([\w._]+)", content):
        module_path = match.group(1)
        py_path = module_path.replace(".", "/") + ".py"
        try:
            resp = session.get(base_url + py_path)
            resp.raise_for_status()
            replacement = (
                f"\n---\n*Conteúdo de `{py_path}`:*\n\n"
                f"```python\n{resp.text}\n```\n"
            )
            content = content.replace(match.group(0), replacement)
        except Exception:
            pass
    return content


def _get_base_url(url: str) -> str:
    """Extrai base URL do repo GitHub a partir da URL completa."""
    parts = url.split("/")
    # https://raw.githubusercontent.com/ORG/REPO/BRANCH/...
    if len(parts) >= 7:
        return "/".join(parts[:7]) + "/"
    return url.rsplit("/", 1)[0] + "/"


def _process_content(
    raw_content: str,
    url: str,
    session: Union[requests.Session, requests_cache.CachedSession],
) -> str:
    """Processa conteúdo bruto de acordo com o tipo de arquivo."""
    if url.endswith(".ipynb"):
        return _process_notebook(raw_content)

    base_url = _get_base_url(url)
    content = _resolve_includes(raw_content, base_url, session)
    content = _resolve_mkdocstrings(content, base_url, session)
    return content


# ─── Fetch ───────────────────────────────────────────────────────


def _fetch_url(
    session: requests.Session,
    url: str,
    source_type: str,
    extra_metadata: Optional[dict] = None,
) -> Optional[SourceDocument]:
    try:
        response = session.get(url)
        response.raise_for_status()

        metadata = extra_metadata or {}
        metadata["url"] = url
        metadata["from_cache"] = getattr(response, "from_cache", False)

        content = _process_content(response.text, url, session)

        return SourceDocument(
            content=content,
            source_type=source_type,
            source_identifier=url,
            metadata=metadata,
        )
    except Exception:
        return None


class BaseDocumentConsumer(ABC):

    @abstractmethod
    def fetch_documents(self) -> List[SourceDocument]:
        pass


class URLDocumentConsumer(BaseDocumentConsumer):

    def __init__(
        self, urls: List[str], cache_session: Optional[requests.Session] = None
    ):
        self.urls = urls
        self.session = cache_session or get_cached_session()

    def fetch_documents(self) -> List[SourceDocument]:
        docs: List[SourceDocument] = []

        with ThreadPoolExecutor(
            max_workers=min(8, len(self.urls) or 1)
        ) as executor:
            futures = {
                executor.submit(_fetch_url, self.session, url, "url"): url
                for url in self.urls
            }
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    docs.append(result)

        return docs


class CSVLinkConsumer(BaseDocumentConsumer):

    def __init__(
        self,
        csv_path: str,
        link_column: str = "markdown_link",
        cache_session: Optional[requests.Session] = None,
    ):
        self.csv_path = csv_path
        self.link_column = link_column
        self.session = cache_session or get_cached_session()

    def fetch_documents(self) -> List[SourceDocument]:
        docs: List[SourceDocument] = []
        try:
            df = pd.read_csv(self.csv_path)
        except Exception:
            return docs

        tasks: List[tuple] = []
        for _, row in df.iterrows():
            url = row.get(self.link_column)
            if not url:
                continue

            row_metadata = row.where(pd.notnull(row), None).to_dict()

            if "web_reference" in row_metadata:
                row_metadata["url_link"] = row_metadata["web_reference"]
            elif "link" in row_metadata:
                row_metadata["url_link"] = row_metadata["link"]

            row_metadata["source_url"] = url
            tasks.append((url, row_metadata))

        if not tasks:
            return docs

        with ThreadPoolExecutor(max_workers=min(8, len(tasks))) as executor:
            futures = {
                executor.submit(
                    _fetch_url, self.session, url, "csv_link", metadata
                ): url
                for url, metadata in tasks
            }
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    docs.append(result)

        return docs


class FileDocumentConsumer(BaseDocumentConsumer):

    def __init__(self, file_paths: List[str]):
        self.file_paths = file_paths

    def fetch_documents(self) -> List[SourceDocument]:
        docs = []
        for file_path in self.file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                docs.append(
                    SourceDocument(
                        content=content,
                        source_type="file",
                        source_identifier=file_path,
                        metadata={"file_path": file_path},
                    )
                )
            except Exception:
                continue

        return docs


def _enrich_content(metadata: dict, content: str) -> str:
    """Prepõe nome e keywords (se existirem) ao conteúdo."""
    parts = []
    name = metadata.get("name")
    if name:
        parts.append(f"# {name}")
    keywords = metadata.get("keywords")
    if keywords:
        parts.append(f"Keywords: {keywords}")
    parts.append(content)
    return "\n\n".join(parts)


class DocumentManager:

    def __init__(self, vector_store: BaseVectorStore):
        self.vector_store = vector_store
        self.consumers: List[BaseDocumentConsumer] = []

    def add_consumer(self, consumer: BaseDocumentConsumer) -> None:
        self.consumers.append(consumer)

    def fetch_and_index_all(
        self,
        collections: Optional[List[str]] = None,
        id_key: Optional[str] = None,
    ) -> None:
        all_docs: List[VectorDocument] = []

        with ThreadPoolExecutor(
            max_workers=min(4, len(self.consumers) or 1)
        ) as executor:
            futures = {
                executor.submit(consumer.fetch_documents): consumer
                for consumer in self.consumers
            }
            for future in as_completed(futures):
                source_docs = future.result()

                for source_doc in source_docs:
                    doc_hash = hashlib.md5(
                        (
                            source_doc.content + source_doc.source_identifier
                        ).encode()
                    ).hexdigest()[:12]

                    fallback_id = f"{source_doc.source_type}_{doc_hash}"
                    doc_id = (
                        source_doc.metadata.get(id_key) or fallback_id
                        if id_key
                        else fallback_id
                    )

                    vector_doc = VectorDocument(
                        id=doc_id,
                        content=_enrich_content(
                            source_doc.metadata, source_doc.content
                        ),
                        metadata=source_doc.metadata,
                        collections=collections or [],
                    )
                    all_docs.append(vector_doc)

        if all_docs:
            self.vector_store.add_documents(all_docs)

    def search(
        self,
        query: str,
        k: int = 3,
        collections: Optional[List[str]] = None,
    ):
        return self.vector_store.similarity_search(
            query, k=k, collections=collections
        )
