from mosqlimate_assistant.models import (
    ChatMessage,
    ProviderResponse,
    ProviderType,
    SourceDocument,
    VectorDocument,
    VectorSearchResult,
)


def test_provider_type():
    assert ProviderType.OPENAI == "openai"
    assert ProviderType.GEMINI == "gemini"
    assert ProviderType.OLLAMA == "ollama"


def test_chat_message():
    msg = ChatMessage(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"


def test_provider_response():
    resp = ProviderResponse(content="test", raw_response={"text": "test"})
    assert resp.content == "test"
    assert resp.raw_response == {"text": "test"}
    assert resp.tool_calls is None


def test_vector_document():
    doc = VectorDocument(id="1", content="test")
    assert doc.id == "1"
    assert doc.content == "test"
    assert doc.metadata == {}
    assert doc.collections == []


def test_vector_search_result():
    doc = VectorDocument(id="1", content="test")
    res = VectorSearchResult(document=doc, score=0.9)
    assert res.score == 0.9
    assert res.document.id == "1"


def test_source_document():
    doc = SourceDocument(
        content="test", source_type="csv", source_identifier="file.csv"
    )
    assert doc.content == "test"
    assert doc.source_type == "csv"
    assert doc.source_identifier == "file.csv"
    assert doc.metadata == {}
