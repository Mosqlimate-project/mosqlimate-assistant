from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.models import VectorDocument
from mosqlimate_assistant.vector_store import InMemoryVectorStore


class DummyEmbeddingProvider(BaseEmbeddingProvider):
    """Returns deterministic 2D embeddings based on text content."""

    def embed_query(self, text: str):
        if "doc1" in text:
            return [1.0, 0.0]
        if "doc2" in text:
            return [0.0, 1.0]
        if "chunk_a" in text:
            return [0.9, 0.1]
        if "chunk_b" in text:
            return [0.1, 0.9]
        if "chunk_c" in text:
            return [0.7, 0.3]
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


def test_chunk_based_max_pooling():
    """Documents with chunks: the best chunk score represents the document."""
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(embedding_provider=provider)
    # Doc A has chunks: chunk_a (0.9, 0.1) and chunk_b (0.1, 0.9)
    doc_a = VectorDocument(
        id="A",
        content="doc with chunks",
        chunks=["chunk_a text", "chunk_b text"],
    )
    # Doc B has a single chunk: chunk_c (0.7, 0.3)
    doc_b = VectorDocument(
        id="B",
        content="another doc",
        chunks=["chunk_c text"],
    )
    store.add_documents([doc_a, doc_b])
    # Embedding matrix should have 3 rows (2 chunks + 1 chunk)
    assert store.embeddings.shape[0] == 3
    assert len(store.chunk_to_doc_idx) == 3
    # Query aligned with chunk_a direction [1.0, 0.0]
    # Doc A max: max(dot([0.9,0.1],[1,0]), dot([0.1,0.9],[1,0])) = max(0.9, 0.1) = 0.9
    # Doc B: dot([0.7,0.3],[1,0]) = 0.7
    results = store.similarity_search("doc1", k=2)
    assert results[0].document.id == "A"
    assert results[0].score > results[1].score
    # Query aligned with chunk_b direction [0.0, 1.0]
    # Doc A max: max(0.1, 0.9) = 0.9
    # Doc B: 0.3
    results = store.similarity_search("doc2", k=2)
    assert results[0].document.id == "A"


def test_fallback_to_content_when_no_chunks():
    """When chunks is empty, the full content is embedded as a single chunk."""
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(embedding_provider=provider)
    doc = VectorDocument(id="1", content="doc1")  # no chunks
    store.add_documents([doc])
    assert store.embeddings.shape[0] == 1
    assert store.chunk_to_doc_idx == [0]
    results = store.similarity_search("doc1", k=1)
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


def test_save_and_load(tmp_path):
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(provider)
    doc = VectorDocument(
        id="1",
        content="doc1",
        chunks=["chunk_a text", "chunk_b text"],
    )
    store.add_documents([doc])
    path = str(tmp_path / "test_store.pkl")
    store.save(path)
    loaded_store = InMemoryVectorStore(provider)
    loaded_store.load(path)
    assert len(loaded_store.documents) == 1
    assert loaded_store.documents[0].chunks == ["chunk_a text", "chunk_b text"]
    assert loaded_store.chunk_to_doc_idx == [0, 0]
    assert loaded_store.embeddings.shape[0] == 2


def test_collection_filter_with_chunks():
    provider = DummyEmbeddingProvider()
    store = InMemoryVectorStore(provider)
    doc1 = VectorDocument(
        id="1",
        content="doc1",
        chunks=["chunk_a stuff"],
        collections=["group_x"],
    )
    doc2 = VectorDocument(
        id="2",
        content="doc2",
        chunks=["chunk_b stuff"],
        collections=["group_y"],
    )
    store.add_documents([doc1, doc2])
    results = store.similarity_search("doc1", k=2, collections=["group_x"])
    assert len(results) == 1
    assert results[0].document.id == "1"
