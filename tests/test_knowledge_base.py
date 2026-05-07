from pathlib import Path

from langchain_core.documents import Document

from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.knowledge_base import (
    DocumentBlockConfig,
    MosqlimateKnowledgeBase,
)


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
