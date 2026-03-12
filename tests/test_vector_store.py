import numpy as np
from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.models import VectorDocument
from mosqlimate_assistant.vector_store import InMemoryVectorStore


class DummyEmbeddingProvider(BaseEmbeddingProvider):
    def embed_query(self, text: str):
        if "doc1" in text:
            return [1.0, 0.0]
        if "doc2" in text:
            return [0.0, 1.0]
        return [0.5, 0.5]


def test_add_documents_and_search():
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(embedding_provider=provider)

    doc1 = VectorDocument(id="1", content="doc1", collections=["col1"])
    doc2 = VectorDocument(id="2", content="doc2")

    store.add_documents([doc1, doc2])

    assert len(store.documents) == 2

    # search
    results = store.similarity_search("doc1", k=1)
    assert len(results) == 1
    # since embedding doc1 gives [1.0, 0.0], the dot product is high for doc1
    assert results[0].document.id == "1"


def test_get_all_documents():
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(provider)
    doc = VectorDocument(id="1", content="doc1")
    store.add_documents([doc])

    all_docs = store.get_all_documents()
    assert len(all_docs) == 1
    assert all_docs[0].document.id == "1"


def test_get_documents_by_collection():
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(provider)
    store.add_documents(
        [
            VectorDocument(id="1", content="doc1", collections=["A"]),
            VectorDocument(id="2", content="doc2", collections=["B"]),
        ]
    )
    docs_a = store.get_documents_by_collection("A")
    assert len(docs_a) == 1
    assert docs_a[0].id == "1"
