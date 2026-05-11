import inspect

import pytest
from langchain_core.messages import AIMessage

from mosqlimate_assistant.agent import LangChainToolAgent
from mosqlimate_assistant.knowledge_base import DocumentBlockConfig
from mosqlimate_assistant.main import assistant_pipeline
from mosqlimate_assistant.models import ChatMessage, ProviderType


class _StubKnowledgeBase:
    def __init__(self):
        self.calls = []
        self._blocks = [
            DocumentBlockConfig(
                key="datastore",
                description="Datastore docs",
                domain="docs",
            ),
            DocumentBlockConfig(
                key="imdc",
                description="IMDC docs",
                domain="imdc",
            ),
        ]

    def available_blocks(self):
        return self._blocks

    def format_block_context(self, block_key: str, query: str) -> str:
        self.calls.append((block_key, query))
        return f"{block_key}:{query}"


class _FakeChatModel:
    def __init__(self, responses):
        self.responses = iter(responses)

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        return next(self.responses)


@pytest.mark.parametrize(
    ("responses", "expected_calls", "expected_blocks", "expected_content"),
    [
        (
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "datastore",
                            "args": {"question": "casos de dengue"},
                            "id": "call-1",
                        }
                    ],
                ),
                AIMessage(content="Resposta final"),
            ],
            [("datastore", "casos de dengue")],
            ["datastore"],
            "Resposta final",
        ),
        (
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "datastore",
                            "args": {"question": "dados"},
                            "id": "call-1",
                        }
                    ],
                ),
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "imdc",
                            "args": {"question": "regras"},
                            "id": "call-2",
                        }
                    ],
                ),
                AIMessage(content="Resposta consolidada"),
            ],
            [("datastore", "dados"), ("imdc", "regras")],
            ["datastore", "imdc"],
            "Resposta consolidada",
        ),
    ],
)
def test_single_agent_executes_expected_tool_sequence(
    responses,
    expected_calls,
    expected_blocks,
    expected_content,
):
    kb = _StubKnowledgeBase()
    model = _FakeChatModel(responses)
    agent = LangChainToolAgent(
        knowledge_base=kb,
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
        chat_model=model,
    )

    result = agent.run(
        "Pergunta cruzada",
        message_history=[
            ChatMessage(role="user", content="contexto anterior")
        ],
    )

    assert kb.calls == expected_calls
    assert result["content"] == expected_content
    assert result["retrieved_blocks"] == expected_blocks


def test_single_agent_supports_batch_block_search_tool():
    kb = _StubKnowledgeBase()
    model = _FakeChatModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "batch_document_search",
                        "args": {
                            "requests": [
                                {
                                    "block_key": "datastore",
                                    "question": "dados epidemiologicos",
                                },
                                {
                                    "block_key": "imdc",
                                    "question": "regras principais",
                                },
                            ]
                        },
                        "id": "call-batch-1",
                    }
                ],
            ),
            AIMessage(content="Resposta final em lote"),
        ]
    )
    agent = LangChainToolAgent(
        knowledge_base=kb,
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
        chat_model=model,
    )

    result = agent.run("Pergunta cruzada com lote")

    assert kb.calls == [
        ("datastore", "dados epidemiologicos"),
        ("imdc", "regras principais"),
    ]
    assert result["content"] == "Resposta final em lote"
    assert result["retrieved_blocks"] == ["datastore", "imdc"]
    assert result["tool_calls"][0]["tool"] == "batch_document_search"


def test_single_agent_blocks_repeated_block_within_same_run():
    kb = _StubKnowledgeBase()
    model = _FakeChatModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "datastore",
                        "args": {"question": "dados"},
                        "id": "call-1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "datastore",
                        "args": {"question": "mais detalhes"},
                        "id": "call-2",
                    }
                ],
            ),
            AIMessage(content="Resposta final"),
        ]
    )
    agent = LangChainToolAgent(
        knowledge_base=kb,
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
        chat_model=model,
    )

    result = agent.run("Pergunta com repeticao")

    assert kb.calls == [("datastore", "dados")]
    assert result["retrieved_blocks"] == ["datastore"]
    assert (
        "já foram consultados nesta rodada"
        in result["tool_calls"][1]["result"]
    )


def test_single_agent_blocks_repeated_blocks_inside_batch():
    kb = _StubKnowledgeBase()
    model = _FakeChatModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "batch_document_search",
                        "args": {
                            "requests": [
                                {
                                    "block_key": "datastore",
                                    "question": "dados epidemiologicos",
                                },
                                {
                                    "block_key": "imdc",
                                    "question": "regras principais",
                                },
                            ]
                        },
                        "id": "call-batch-1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "batch_document_search",
                        "args": {
                            "requests": [
                                {
                                    "block_key": "imdc",
                                    "question": "mais regras",
                                }
                            ]
                        },
                        "id": "call-batch-2",
                    }
                ],
            ),
            AIMessage(content="Resposta final"),
        ]
    )
    agent = LangChainToolAgent(
        knowledge_base=kb,
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
        chat_model=model,
    )

    result = agent.run("Pergunta com lote repetido")

    assert kb.calls == [
        ("datastore", "dados epidemiologicos"),
        ("imdc", "regras principais"),
    ]
    assert result["retrieved_blocks"] == ["datastore", "imdc"]
    assert "imdc" in result["tool_calls"][1]["result"]


def test_single_agent_resets_consulted_blocks_on_next_run():
    kb = _StubKnowledgeBase()
    model = _FakeChatModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "datastore",
                        "args": {"question": "dados rodada 1"},
                        "id": "call-1",
                    }
                ],
            ),
            AIMessage(content="Resposta 1"),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "datastore",
                        "args": {"question": "dados rodada 2"},
                        "id": "call-2",
                    }
                ],
            ),
            AIMessage(content="Resposta 2"),
        ]
    )
    agent = LangChainToolAgent(
        knowledge_base=kb,
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
        chat_model=model,
    )

    first = agent.run("Primeira pergunta")
    second = agent.run("Segunda pergunta")

    assert first["retrieved_blocks"] == ["datastore"]
    assert second["retrieved_blocks"] == ["datastore"]
    assert kb.calls == [
        ("datastore", "dados rodada 1"),
        ("datastore", "dados rodada 2"),
    ]


def test_single_agent_forces_final_answer_after_tool_limit():
    kb = _StubKnowledgeBase()
    model = _FakeChatModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "datastore",
                        "args": {"question": "dados"},
                        "id": "call-1",
                    }
                ],
            ),
            AIMessage(content="Resposta final forcada"),
        ]
    )
    agent = LangChainToolAgent(
        knowledge_base=kb,
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
        chat_model=model,
        max_tool_iterations=1,
    )

    result = agent.run("Pergunta que excede o limite")

    assert kb.calls == [("datastore", "dados")]
    assert result["content"] == "Resposta final forcada"
    assert result["iterations"] == 1
    assert result["retrieved_blocks"] == ["datastore"]


def test_assistant_pipeline_signature_is_stable():
    signature = inspect.signature(assistant_pipeline)
    assert list(signature.parameters)[:4] == [
        "question",
        "google_api_key",
        "message_history",
        "lang",
    ]
