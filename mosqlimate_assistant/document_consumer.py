"""Document ingestion, content processing, and text chunking pipeline.

Handles fetching documents from external sources (URLs, CSV link lists,
and local files), processing their content (Jupyter notebooks, mkdocs
includes/mkdocstrings references), splitting text into overlapping chunks
for granular embedding, and indexing them into a vector store via the
``DocumentManager``.

Consumer hierarchy:
    BaseDocumentConsumer → URLDocumentConsumer
                         → CSVLinkConsumer
                         → FileDocumentConsumer

The ``DocumentManager`` orchestrates consumers, generates deterministic
document IDs, enriches content with metadata, applies recursive text
chunking, and delegates storage to the configured ``BaseVectorStore``.

HTTP responses are cached using ``requests-cache`` (SQLite backend)
with settings from ``mosqlimate_assistant.settings``.
"""

import hashlib
import json
import logging
import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from pathlib import Path
from typing import List, Literal, Optional, Union

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
    """Retrieve or configure a cached HTTP session.

    Returns:
        Union[requests.Session, requests_cache.CachedSession]: Configured HTTP session.

    """
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


def _process_notebook(raw_json: str) -> str:
    try:
        notebook = json.loads(raw_json)
    except json.JSONDecodeError:
        return raw_json

    lang = (
        notebook.get("metadata", {})
        .get("kernelspec", {})
        .get("language", "python")
    )

    parts: List[str] = []
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
    """Resolve mkdocs --8<-- 'file' inclusions.

    Args:
        content (str): Raw document content.
        base_url (str): Base URL to fetch the included files from.
        session (Union[requests.Session, requests_cache.CachedSession]): HTTP session to use.

    Returns:
        str: Content with inclusions resolved.

    """
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
    """Resolve mkdocstrings ::: module.path references.

    Args:
        content (str): Raw document content.
        base_url (str): Base URL to fetch the module files from.
        session (Union[requests.Session, requests_cache.CachedSession]): HTTP session to use.

    Returns:
        str: Content with module references resolved.

    """
    pattern = r"::: ([\w._]+)(?:\n[ \t]+.*)*"
    for match in re.finditer(pattern, content):
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
    """Extract the base URL of a GitHub repository from its full URL.

    Args:
        url (str): Full GitHub raw content URL.

    Returns:
        str: The base URL pointing to the repository root.

    """
    parts = url.split("/")
    # https://raw.githubusercontent.com/ORG/REPO/BRANCH/...
    if len(parts) >= 7 and "githubusercontent.com" in parts[2]:
        return "/".join(parts[:6]) + "/"
    return url.rsplit("/", 1)[0] + "/"


def _process_content(
    raw_content: str,
    url: str,
    session: Union[requests.Session, requests_cache.CachedSession],
) -> str:
    """Process raw content according to its file type.

    Args:
        raw_content (str): Raw file content fetched from the source.
        url (str): URL of the original file.
        session (Union[requests.Session, requests_cache.CachedSession]): HTTP session to use for further resolving.

    Returns:
        str: Processed text content.

    """
    if url.endswith(".ipynb"):
        return _process_notebook(raw_content)

    base_url = _get_base_url(url)
    content = _resolve_includes(raw_content, base_url, session)
    content = _resolve_mkdocstrings(content, base_url, session)
    return content


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

        unresolved = len(re.findall(r"::: ([\w._]+)", content)) + len(
            re.findall(r'--8<-- "([^"]+)"', content)
        )
        if unresolved > 0:
            raise ValueError(f"Failed to fully render {unresolved} templates")

        return SourceDocument(
            content=content,
            source_type=source_type,
            source_identifier=url,
            metadata=metadata,
        )
    except Exception as e:
        logging.warning("Error fetching %s: %s", url, e)
        return None


class BaseDocumentConsumer(ABC):
    """Abstract base class for document consumers."""

    @abstractmethod
    def fetch_documents(self) -> List[SourceDocument]:
        """Fetch and return a list of SourceDocuments from the underlying source.

        Returns:
            List[SourceDocument]: A list of fetched documents.

        """
        pass


class URLDocumentConsumer(BaseDocumentConsumer):
    """Fetches documents from a predefined list of HTTP URLs.

    Attributes:
        urls (List[str]): List of target URLs.
        session (Optional[requests.Session]): Optional HTTP session.

    """

    def __init__(
        self, urls: List[str], cache_session: Optional[requests.Session] = None
    ):
        """Initialize the URLDocumentConsumer.

        Args:
            urls (List[str]): URLs to fetch documents from.
            cache_session (Optional[requests.Session], optional): Optional HTTP session. Defaults to None.

        """
        self.urls = urls
        self.session = cache_session or get_cached_session()

    def fetch_documents(self) -> List[SourceDocument]:
        """Fetch content from all configured URLs concurrently.

        Returns:
            List[SourceDocument]: Documents successfully retrieved and processed.

        """
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
    """Fetches documents using URLs provided in a CSV file.

    Attributes:
        csv_path (str): File path to the source CSV.
        link_column (str): Name of the column containing the URLs to fetch.
        session (Optional[requests.Session]): Optional HTTP session.

    """

    def __init__(
        self,
        csv_path: str,
        link_column: str = "markdown_link",
        cache_session: Optional[requests.Session] = None,
    ):
        """Initialize the CSVLinkConsumer.

        Args:
            csv_path (str): File path to the source CSV.
            link_column (str, optional): Name of the column containing the URLs to fetch. Defaults to "markdown_link".
            cache_session (Optional[requests.Session], optional): Optional HTTP session. Defaults to None.

        """
        self.csv_path = csv_path
        self.link_column = link_column
        self.session = cache_session or get_cached_session()

    def fetch_documents(self) -> List[SourceDocument]:
        """Read the CSV, extract metadata, and fetch documents concurrently.

        Returns:
            List[SourceDocument]: Documents successfully retrieved and processed.

        """
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

            row_metadata = {
                k: (v if pd.notnull(v) else None) for k, v in row.items()
            }

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
    """Reads documents directly from local filesystem paths.

    Attributes:
        file_paths (List[str]): List of absolute or relative local file paths.

    """

    def __init__(self, file_paths: List[str]):
        """Initialize the FileDocumentConsumer.

        Args:
            file_paths (List[str]): List of absolute or relative local file paths.

        """
        self.file_paths = file_paths

    def fetch_documents(self) -> List[SourceDocument]:
        """Read all local files and wrap their contents into SourceDocument instances.

        Returns:
            List[SourceDocument]: Documents read from the provided paths.

        """
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


def _find_best_separator(text: str, separators: List[str]) -> str:
    """Find the coarsest separator that exists in the text.
    Args:
        text: The text to search for separators.
        separators: Ordered list from coarsest to finest.
    Returns:
        The best separator found, or empty string as last resort.
    """
    for sep in separators:
        if sep and sep in text:
            return sep
    return " "


def _greedy_merge(
    segments: List[str],
    chunk_size: int,
    separator: str,
) -> List[str]:
    """Greedily merge adjacent segments into chunks up to chunk_size.
    Args:
        segments: Non-empty text segments to merge.
        chunk_size: Maximum character length per chunk.
        separator: Separator to join segments.
    Returns:
        List of merged chunks.
    """
    if not segments:
        return []
    chunks: List[str] = []
    current = segments[0]
    for seg in segments[1:]:
        combined = current + separator + seg
        if len(combined) <= chunk_size:
            current = combined
        else:
            chunks.append(current.strip())
            current = seg
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if c]


def _balance_chunks(chunks: List[str], chunk_size: int) -> List[str]:
    """Rebalance chunks by merging undersized ones with their smaller neighbor.
    A chunk is considered undersized if it is shorter than ``chunk_size // 3``.
    When merging, the undersized chunk joins whichever neighbor (left or right)
    is smaller, as long as the result stays within ``chunk_size``.
    Args:
        chunks: List of text chunks to balance.
        chunk_size: Maximum character length per chunk.
    Returns:
        Balanced list of chunks with fewer undersized entries.
    """
    if len(chunks) <= 1:
        return chunks
    min_size = chunk_size // 3
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(chunks):
            if len(chunks[i]) < min_size and len(chunks) > 1:
                # Find the best merge candidate
                left_size = len(chunks[i - 1]) if i > 0 else float("inf")
                right_size = (
                    len(chunks[i + 1]) if i < len(chunks) - 1 else float("inf")
                )
                if left_size <= right_size and i > 0:
                    merged = chunks[i - 1] + "\n" + chunks[i]
                    if len(merged) <= chunk_size:
                        chunks[i - 1] = merged
                        chunks.pop(i)
                        changed = True
                        continue
                if i < len(chunks) - 1:
                    merged = chunks[i] + "\n" + chunks[i + 1]
                    if len(merged) <= chunk_size:
                        chunks[i] = merged
                        chunks.pop(i + 1)
                        changed = True
                        continue
            i += 1
    return chunks


def _apply_overlap(
    chunks: List[str], overlap: int, min_chunk_size: int = 0
) -> List[str]:
    """Add overlap by prepending tail characters from the previous chunk.
    Args:
        chunks: Ordered list of text chunks.
        overlap: Default number of characters to carry over.
        min_chunk_size: Threshold to trigger recursive overlap increase.
    Returns:
        Chunks with overlap applied (first chunk unchanged).
    """
    if overlap <= 0 or len(chunks) <= 1:
        return chunks
    result = [chunks[0]]
    for i in range(1, len(chunks)):
        chunk = chunks[i]
        prev = chunks[i - 1]

        # Use recursive overlap increase to ensure the chunk reaches min_chunk_size
        # while keeping the split as clean as possible.
        current_overlap = overlap
        while (
            min_chunk_size > 0
            and (len(chunk) + current_overlap) < min_chunk_size
            and current_overlap < len(prev)
        ):
            current_overlap += overlap

        # Ensure we don't exceed prev length
        current_overlap = min(current_overlap, len(prev))

        tail = prev[-current_overlap:]
        # Find a clean break point (space or newline)
        # Search from the beginning of the tail to find the FIRST break
        # that allows a clean overlap start.
        break_idx = -1
        for j, ch in enumerate(tail):
            if ch in (" ", "\n"):
                break_idx = j + 1
                break

        # If we found a break, use from there. If not, use the whole tail.
        clean_tail = tail[break_idx:] if break_idx != -1 else tail

        if clean_tail:
            result.append(clean_tail.strip() + "\n" + chunk)
        else:
            result.append(chunk)
    return result


def balanced_chunk_split(
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 80,
    separators: Optional[List[str]] = None,
) -> List[str]:
    """Split text into balanced, overlapping chunks.
    Produces fewer, larger chunks compared to naive recursive splitting.
    The algorithm:
        1. If text fits in one chunk, return it.
        2. Split by the coarsest applicable separator.
        3. Greedily merge adjacent segments up to ``chunk_size``.
        4. Rebalance: merge undersized chunks (< chunk_size / 3) with neighbors.
        5. If any chunk is still oversized, recursively split with finer separators.
        6. Apply overlap between consecutive chunks.
    Args:
        text: The input text to split.
        chunk_size: Maximum number of characters per chunk. Defaults to 1200.
        chunk_overlap: Number of overlapping characters for context. Defaults to 80.
        separators: Separator hierarchy from coarsest to finest. Defaults to
            ``["\\n\\n", "# ", "## ", "### ", "```", "\\n", ". ", ", ", " "]``.
    Returns:
        List of balanced text chunks. Empty list for empty input.
    """
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
    if separators is None:
        separators = [
            "\n\n",
            "# ",
            "## ",
            "### ",
            "```",
            "\n",
            ". ",
            ", ",
            " ",
        ]
    sep = _find_best_separator(text, separators)
    remaining_seps = (
        separators[separators.index(sep) + 1 :]
        if sep in separators
        else separators[1:]
    )
    raw_segments = [s for s in text.split(sep) if s.strip()]
    if not raw_segments:
        return [text]
    # Greedy merge → balance
    chunks = _greedy_merge(raw_segments, chunk_size, sep)
    chunks = _balance_chunks(chunks, chunk_size)
    # Recursively split any still-oversized chunks with finer separators
    final: List[str] = []
    for chunk in chunks:
        if len(chunk) > chunk_size and remaining_seps:
            sub = balanced_chunk_split(
                chunk,
                chunk_size=chunk_size,
                chunk_overlap=0,  # overlap applied at the end
                separators=remaining_seps,
            )
            final.extend(sub)
        else:
            final.append(chunk)
    # Balance again after recursive splits
    final = _balance_chunks(final, chunk_size)
    # Apply overlap with minimum size requirement (e.g. 2/3 of chunk_size)
    min_size = int(chunk_size * 0.66)
    final = _apply_overlap(final, chunk_overlap, min_chunk_size=min_size)
    return [c for c in final if c.strip()]


# Keep backward-compatible alias
recursive_character_split = balanced_chunk_split


def _enrich_content(metadata: dict, content: str) -> str:
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
    """Orchestrates document scraping, processing, and indexing.

    Attributes:
        vector_store (BaseVectorStore): The underlying vector database to populate.
        consumers (List[BaseDocumentConsumer]): Subscribed document sources.
        indexing_strategy (Literal["content", "keyword"]): Strategy for chunk generation.
        chunk_size (int): Maximum characters per chunk (content strategy).
        chunk_overlap (int): Overlap characters between chunks (content strategy).
    """

    def __init__(
        self,
        vector_store: BaseVectorStore,
        indexing_strategy: Literal["content", "keyword"] = "content",
        chunk_size: int = 1200,
        chunk_overlap: int = 80,
    ):
        """Initialize the DocumentManager.

        Args:
            vector_store (BaseVectorStore): The underlying vector database to populate.
            indexing_strategy (Literal["content", "keyword"], optional): Strategy for
                generating document chunks. "content" recursively splits the enriched
                text; "keyword" uses metadata keywords as a single chunk. Defaults to "content".
            chunk_size (int, optional): Max characters per chunk. Defaults to 1300.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 80.
        """
        self.vector_store = vector_store
        self.consumers: List[BaseDocumentConsumer] = []
        self.indexing_strategy = indexing_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def add_consumer(self, consumer: BaseDocumentConsumer) -> None:
        """Register a new document consumer to the manager.

        Args:
            consumer (BaseDocumentConsumer): Consumer instance to attach.

        """
        self.consumers.append(consumer)

    def fetch_and_index_all(
        self,
        collections: Optional[List[str]] = None,
        id_key: Optional[str] = None,
    ) -> None:
        """Fetch documents from all registered consumers and index them into the vector store.

        Args:
            collections (Optional[List[str]], optional): Collections to assign to the new documents. Defaults to None.
            id_key (Optional[str], optional): Metadata key to use as the document ID. Defaults to None.

        """
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
                    enriched = _enrich_content(
                        source_doc.metadata, source_doc.content
                    )

                    # New chunking logic:
                    # chunk[0] = Metadata (Title + Keywords)
                    # chunks[1:] = Content split
                    metadata_parts = []
                    if source_doc.metadata.get("name"):
                        metadata_parts.append(
                            f"# {source_doc.metadata.get('name')}"
                        )
                    if source_doc.metadata.get("keywords"):
                        metadata_parts.append(
                            f"Keywords: {source_doc.metadata.get('keywords')}"
                        )

                    meta_chunk = (
                        "\n\n".join(metadata_parts)
                        if metadata_parts
                        else "# Document"
                    )

                    if self.indexing_strategy == "keyword":
                        chunks = [meta_chunk]
                    else:
                        content_chunks = recursive_character_split(
                            source_doc.content,
                            chunk_size=self.chunk_size,
                            chunk_overlap=self.chunk_overlap,
                        )
                        chunks = [meta_chunk] + content_chunks

                    vector_doc = VectorDocument(
                        id=doc_id,
                        content=enriched,
                        metadata=source_doc.metadata,
                        collections=collections or [],
                        chunks=chunks,
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
        """Proxy a semantic similarity search to the underlying vector store.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top results to return. Defaults to 3.
            collections (Optional[List[str]], optional): Collections to restrict the search to. Defaults to None.

        Returns:
            List[VectorSearchResult]: Documents matching the query.

        """
        return self.vector_store.similarity_search(
            query, k=k, collections=collections
        )
