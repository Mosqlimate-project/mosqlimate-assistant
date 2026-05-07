from mosqlimate_assistant.models import (
    ChatMessage,
    ProviderType,
    SourceDocument,
    VectorDocument,
)


def test_provider_type():
    assert ProviderType.OPENAI == "openai"
    assert ProviderType.GEMINI == "gemini"
    assert ProviderType.OLLAMA == "ollama"
    assert ProviderType.DEEPSEEK == "deepseek"


def test_chat_message():
    msg = ChatMessage(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"


def test_vector_document():
    doc = VectorDocument(id="1", content="test")
    assert doc.id == "1"
    assert doc.content == "test"
    assert doc.metadata == {}
    assert doc.collections == []


def test_source_document():
    doc = SourceDocument(
        content="test", source_type="csv", source_identifier="file.csv"
    )
    assert doc.content == "test"
    assert doc.source_type == "csv"
    assert doc.source_identifier == "file.csv"
    assert doc.metadata == {}
