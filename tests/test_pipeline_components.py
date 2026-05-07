from mosqlimate_assistant.agent import ChatMessageAdapter
from mosqlimate_assistant.document_consumer import (
    BaseDocumentConsumer,
    ChunkingConfig,
    DocumentManager,
    VectorDocumentFactory,
)
from mosqlimate_assistant.knowledge_base import LangChainDocumentFactory
from mosqlimate_assistant.models import ChatMessage, SourceDocument


class _FakeConsumer(BaseDocumentConsumer):
    def __init__(self, docs):
        self.docs = docs

    def fetch_documents(self):
        return self.docs


class _FakeSink:
    def __init__(self):
        self.documents = []

    def add_documents(self, documents):
        self.documents.extend(documents)


def test_vector_document_factory_builds_metadata_chunk():
    factory = VectorDocumentFactory(
        ChunkingConfig(
            indexing_strategy="content", chunk_size=80, chunk_overlap=10
        )
    )
    source = SourceDocument(
        content="Texto de exemplo. " * 20,
        source_type="file",
        source_identifier="demo.md",
        metadata={"name": "Demo", "keywords": "teste, demo"},
    )

    vector_doc = factory.build(source, collections=["docs"], id_key="name")

    assert vector_doc.id == "Demo"
    assert vector_doc.collections == ["docs"]
    assert vector_doc.chunks[0].startswith("# Demo")
    assert "Keywords: teste, demo" in vector_doc.chunks[0]
    assert len(vector_doc.chunks) > 1


def test_langchain_document_factory_preserves_chunk_metadata():
    source = SourceDocument(
        content="Texto de exemplo. " * 10,
        source_type="file",
        source_identifier="demo.md",
        metadata={"name": "Demo"},
    )
    vector_doc = VectorDocumentFactory().build(
        source,
        collections=["docs"],
        id_key="name",
    )

    docs = LangChainDocumentFactory().from_vector_documents(
        [vector_doc],
        domain="docs",
    )

    assert len(docs) == len(vector_doc.chunks)
    assert docs[0].metadata["chunk_kind"] == "metadata"
    assert docs[0].metadata["chunk_index"] == 0
    assert docs[0].metadata["domain"] == "docs"
    assert docs[1].metadata["chunk_kind"] == "content"
    assert docs[1].metadata["source_id"] == "Demo"


def test_chat_message_adapter_converts_history_and_content():
    messages = ChatMessageAdapter.history_to_messages(
        [
            ChatMessage(role="system", content="s"),
            ChatMessage(role="user", content="u"),
            ChatMessage(role="assistant", content="a"),
        ]
    )

    assert len(messages) == 3
    assert ChatMessageAdapter.stringify_content("texto") == "texto"
    assert (
        ChatMessageAdapter.stringify_content(
            [{"type": "text", "text": "linha 1"}, {"foo": "bar"}]
        )
        == "linha 1\n{'foo': 'bar'}"
    )


def test_document_manager_exposes_independent_pipeline_steps():
    source = SourceDocument(
        content="Texto de exemplo. " * 5,
        source_type="file",
        source_identifier="demo.md",
        metadata={"name": "Demo"},
    )
    sink = _FakeSink()
    manager = DocumentManager(sink)
    manager.add_consumer(_FakeConsumer([source]))

    fetched = manager.fetch_documents()
    built = manager.build_vector_documents(
        fetched,
        collections=["docs"],
        id_key="name",
    )
    manager.index_documents(built)

    assert len(fetched) == 1
    assert len(built) == 1
    assert built[0].id == "Demo"
    assert sink.documents[0].id == "Demo"
