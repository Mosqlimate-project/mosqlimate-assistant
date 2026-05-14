from pathlib import Path

from langchain_core.documents import Document

from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.knowledge_base import (
    DocumentBlockConfig,
    DocumentSourceConfig,
    MosqlimateKnowledgeBase,
    SourceDocumentPipeline,
)
from mosqlimate_assistant.models import VectorDocument


class DummyEmbeddingProvider(BaseEmbeddingProvider):
    def embed_query(self, text: str):
        if "doc1" in text:
            return [1.0, 0.0]
        if "doc2" in text:
            return [0.0, 1.0]
        return [0.5, 0.5]


def _make_blocks():
    return [
        DocumentBlockConfig(
            key="datastore",
            description="Datastore docs",
            domain="docs",
            names=frozenset({"datastore_infodengue"}),
        ),
        DocumentBlockConfig(
            key="mosqlient",
            description="mosqlient docs",
            domain="code",
        ),
    ]


def test_search_block_filters_by_metadata(tmp_path: Path):
    provider = DummyEmbeddingProvider()
    docs = [
        Document(
            page_content="doc1 datastore content",
            metadata={"domain": "docs", "name": "datastore_infodengue"},
        ),
        Document(
            page_content="doc2 code content",
            metadata={"domain": "code", "name": "Overview"},
        ),
    ]
    kb = MosqlimateKnowledgeBase.from_langchain_documents(
        documents=docs,
        embedding_provider=provider,
        blocks=_make_blocks(),
        storage_path=tmp_path / "kb",
    )

    results = kb.search_block("datastore", "doc1", k=1)

    assert len(results) == 1
    assert results[0].metadata["name"] == "datastore_infodengue"


def test_faiss_persistence_roundtrip(tmp_path: Path):
    provider = DummyEmbeddingProvider()
    storage_path = tmp_path / "kb"
    docs = [
        Document(
            page_content="doc2 mosqlient content",
            metadata={"domain": "code", "name": "Overview"},
        )
    ]
    created = MosqlimateKnowledgeBase.from_langchain_documents(
        documents=docs,
        embedding_provider=provider,
        blocks=_make_blocks(),
        storage_path=storage_path,
    )

    loaded = MosqlimateKnowledgeBase.load_or_build(
        storage_path=storage_path,
        embedding_provider=provider,
        blocks=_make_blocks(),
        source_configs=[],
    )

    assert created.storage_path == loaded.storage_path
    results = loaded.search_block("mosqlient", "doc2", k=1)
    assert len(results) == 1
    assert results[0].metadata["domain"] == "code"


def test_load_or_build_rebuilds_when_storage_is_incomplete(tmp_path: Path):
    provider = DummyEmbeddingProvider()
    storage_path = tmp_path / "kb"
    storage_path.mkdir()
    (storage_path / "index.faiss").write_text("partial", encoding="utf-8")
    docs = [
        Document(
            page_content="doc2 mosqlient content",
            metadata={"domain": "code", "name": "Overview"},
        )
    ]
    rebuilt = MosqlimateKnowledgeBase.from_langchain_documents(
        documents=docs,
        embedding_provider=provider,
        blocks=_make_blocks(),
        storage_path=storage_path,
    )

    loaded = MosqlimateKnowledgeBase.load_or_build(
        storage_path=storage_path,
        embedding_provider=provider,
        blocks=_make_blocks(),
        source_configs=[],
    )

    assert rebuilt.storage_path == loaded.storage_path
    assert (storage_path / "index.faiss").exists()
    assert (storage_path / "index.pkl").exists()


def test_load_or_build_fails_clearly_when_no_documents_are_available(
    tmp_path: Path,
):
    provider = DummyEmbeddingProvider()

    try:
        MosqlimateKnowledgeBase.load_or_build(
            storage_path=tmp_path / "kb-empty",
            embedding_provider=provider,
            blocks=_make_blocks(),
            source_configs=[],
        )
    except ValueError as exc:
        assert "No documents were collected" in str(exc)
    else:
        raise AssertionError(
            "Expected a clear failure for an empty knowledge base"
        )


def test_format_block_context_prefers_live_source_documents(
    tmp_path: Path,
    monkeypatch,
):
    provider = DummyEmbeddingProvider()
    csv_path = tmp_path / "imdc.csv"
    csv_path.write_text("name,markdown_link\n", encoding="utf-8")
    block = DocumentBlockConfig(
        key="imdc_overview",
        description="IMDC overview docs",
        domain="imdc",
        url_fragments=frozenset({"/content/sprint/2025/index.md"}),
    )
    stale_docs = [
        Document(
            page_content="stale cached content",
            metadata={
                "domain": "imdc",
                "name": "stale-imdc",
                "markdown_link": "https://example.org/stale.md",
            },
        )
    ]
    kb = MosqlimateKnowledgeBase.from_langchain_documents(
        documents=stale_docs,
        embedding_provider=provider,
        blocks=[block],
        storage_path=tmp_path / "kb-live",
        source_configs=[
            DocumentSourceConfig(domain="imdc", csv_path=csv_path)
        ],
        prefer_live_block_search=True,
    )

    calls = {"count": 0}

    def fake_collect(self: SourceDocumentPipeline):
        calls["count"] += 1
        assert self.source_config.domain == "imdc"
        return [
            VectorDocument(
                id="sprint-2025",
                content="Current IMDC sprint overview",
                metadata={
                    "name": "sprint-2025",
                    "markdown_link": "https://raw.example/content/sprint/2025/index.md",
                    "url_link": "https://sprint.mosqlimate.org/sprint/2025/",
                },
                collections=["imdc"],
                chunks=[
                    "# sprint-2025",
                    "Current IMDC sprint overview",
                ],
            )
        ]

    monkeypatch.setattr(
        SourceDocumentPipeline,
        "collect_vector_documents",
        fake_collect,
    )

    context = kb.format_block_context("imdc_overview", "current sprint")

    assert "Current IMDC sprint overview" in context
    assert "stale cached content" not in context
    assert (
        "Reference: [sprint-2025](https://sprint.mosqlimate.org/sprint/2025/)"
        in context
    )
    assert calls["count"] == 1
