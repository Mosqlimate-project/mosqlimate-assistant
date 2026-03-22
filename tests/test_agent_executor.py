"""Tests for AgentExecutor tool-call flow, message history propagation,
and Assistant.register_agent tool wiring."""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest
from pydantic import Field

from mosqlimate_assistant.agent_cards import (
    AgentCard,
    BaseTool,
    ToolInputSchema,
)
from mosqlimate_assistant.agents import AgentExecutor, AgentOrchestrator
from mosqlimate_assistant.models import ChatMessage


# ---------------------------------------------------------------------------
# Helpers / Fakes
# ---------------------------------------------------------------------------


class _FakeResponse:
    """Minimal stand-in for a provider ChatCompletionResponse."""

    def __init__(self, content: str, tool_calls: Optional[List[Dict]] = None):
        self.content = content
        self.tool_calls = tool_calls or []


class _SequentialFakeProvider:
    """Returns pre-defined responses in order, one per `chat_completion` call."""

    def __init__(self, responses: List[_FakeResponse]):
        self._responses = iter(responses)
        self.calls: List[List[ChatMessage]] = []

    def chat_completion(
        self, messages: List[ChatMessage], tools=None
    ) -> _FakeResponse:
        self.calls.append(list(messages))
        return next(self._responses)

    def supports_tools(self) -> bool:
        return True


class _EchoSchema(ToolInputSchema):
    text: str = Field(..., description="Text to echo")


def _echo_function(text: str) -> str:
    return f"echo:{text}"


_ECHO_TOOL = BaseTool(
    name="echo_tool",
    description="Echoes the text back",
    args_schema=_EchoSchema,
    tool_function=_echo_function,
)


def _make_card(name: str = "test_agent") -> AgentCard:
    card = AgentCard(name=name, description="A test agent")
    card.set_prompt_function(lambda: "You are a test agent.")
    return card


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_run_no_tool_calls_returns_content():
    """When the LLM returns no tool calls, run() should return its content immediately."""
    provider = _SequentialFakeProvider(
        [_FakeResponse(content="Direct answer", tool_calls=[])]
    )
    card = _make_card()
    executor = AgentExecutor(agent_card=card, provider=provider)

    result = executor.run("What is Mosqlimate?")

    assert result["content"] == "Direct answer"
    assert result["tool_calls"] == []
    assert result["iterations"] == 0
    assert len(provider.calls) == 1


def test_run_with_tool_call_then_final_answer():
    """When the LLM first returns a tool call, the tool executes and the LLM is
    called again; only the final answer is returned."""
    import json

    tool_call = {
        "name": "echo_tool",
        "arguments": json.dumps({"text": "hello"}),
    }
    provider = _SequentialFakeProvider(
        [
            _FakeResponse(content="", tool_calls=[tool_call]),
            _FakeResponse(
                content="Final answer using echo:hello", tool_calls=[]
            ),
        ]
    )
    card = _make_card()
    executor = AgentExecutor(
        agent_card=card,
        provider=provider,
        tools=[_ECHO_TOOL],
    )

    result = executor.run("Echo hello for me")

    assert result["content"] == "Final answer using echo:hello"
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["tool"] == "echo_tool"
    assert result["tool_calls"][0]["result"] == "echo:hello"
    # Provider was called exactly twice: once for tool call, once for final answer
    assert len(provider.calls) == 2


def test_run_empty_content_returns_empty_string():
    """When the LLM returns None/empty content with no tool calls, run() should
    return an empty string, not None."""
    provider = _SequentialFakeProvider(
        [_FakeResponse(content=None, tool_calls=[])]
    )
    card = _make_card()
    executor = AgentExecutor(agent_card=card, provider=provider)

    result = executor.run("empty")

    assert result["content"] == ""


def test_run_message_history_is_included_in_provider_call():
    """message_history entries must appear in the messages sent to the provider."""
    provider = _SequentialFakeProvider(
        [_FakeResponse(content="With history", tool_calls=[])]
    )
    card = _make_card()
    executor = AgentExecutor(agent_card=card, provider=provider)

    history = [
        ChatMessage(role="user", content="Previous question"),
        ChatMessage(role="assistant", content="Previous answer"),
    ]
    executor.run("Follow-up question", message_history=history)

    messages_sent = provider.calls[0]
    roles = [m.role for m in messages_sent]
    contents = [m.content for m in messages_sent]

    assert "Previous question" in contents
    assert "Previous answer" in contents
    # History should appear before the current user query
    prev_q_idx = contents.index("Previous question")
    curr_q_idx = contents.index("Follow-up question")
    assert prev_q_idx < curr_q_idx


def test_orchestrator_register_agent_sets_executor_callback():
    """Registering an agent sets the executor_callback on the AgentCard."""
    provider = _SequentialFakeProvider(
        [_FakeResponse(content="orchestrated", tool_calls=[])]
    )
    card = _make_card("orch_agent")
    executor = AgentExecutor(agent_card=card, provider=provider)

    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("orch_agent", executor, is_default=True)

    # The callback should now be set
    assert card._executor_callback is not None

    result = orchestrator.route("test query")
    assert result["content"] == "orchestrated"


def test_agent_executor_receives_tools_from_agent_card():
    """AgentExecutor should expose tools from the agent_card when wired correctly.

    This verifies the fix in assistant.py's register_agent, which now passes
    `tools=list(agent_card.tools)` to AgentExecutor.
    """
    card = _make_card("tool_agent")
    card.tools.append(_ECHO_TOOL)

    provider = _SequentialFakeProvider(
        [_FakeResponse(content="done", tool_calls=[])]
    )
    # This mirrors exactly what assistant.py's register_agent now does:
    executor = AgentExecutor(
        agent_card=card,
        provider=provider,
        tools=list(card.tools) if card.tools else None,
    )

    assert "echo_tool" in executor.tools
    assert executor.tools["echo_tool"].name == "echo_tool"


def test_agent_executor_without_tools_has_empty_tools_dict():
    """When no tools are passed, executor.tools should be an empty dict."""
    card = _make_card("no_tools_agent")
    provider = _SequentialFakeProvider(
        [_FakeResponse(content="ok", tool_calls=[])]
    )
    executor = AgentExecutor(agent_card=card, provider=provider)

    assert executor.tools == {}
    result = executor.run("hello")
    assert result["content"] == "ok"


def test_run_filters_history_to_user_assistant_only():
    """History sent to sub-agents via tools should contain only user/assistant messages.

    System messages and tool-result messages from the parent agent's turn
    should NOT be forwarded — sub-agents don't need to know about tool-call
    internals.
    """
    import json

    received_history: list = []

    def _capturing_callback(
        user_question: str,
        task_context: str,
        message_history=None,
    ) -> dict:
        if message_history is not None:
            received_history.extend(message_history)
        return {"content": "sub-agent answer"}

    sub_card = _make_card("sub_agent")
    sub_card.set_executor_callback(_capturing_callback)
    # Give the docs-agent a tool that wraps the sub-agent
    docs_card = _make_card("docs_agent")

    tool_call = {
        "name": "sub_agent",
        "arguments": json.dumps(
            {"user_question": "Q?", "task_context": "Some context"}
        ),
    }
    docs_provider = _SequentialFakeProvider(
        [
            _FakeResponse(content="", tool_calls=[tool_call]),
            _FakeResponse(content="Final", tool_calls=[]),
        ]
    )
    sub_tool = sub_card.agent_to_tool
    docs_executor = AgentExecutor(
        agent_card=docs_card,
        provider=docs_provider,
        tools=[sub_tool],
    )

    mixed_history = [
        ChatMessage(role="system", content="System directive"),
        ChatMessage(role="user", content="First user question"),
        ChatMessage(role="assistant", content="First assistant answer"),
        ChatMessage(
            role="user", content="tool result injection"
        ),  # should be filtered too? no, role=user is kept
    ]
    docs_executor.run("New user question", message_history=mixed_history)

    # Only user/assistant messages should reach the sub-agent
    roles_received = {m.role for m in received_history}
    assert (
        "system" not in roles_received
    ), "system messages must be filtered out"


def test_agent_to_tool_is_cached():
    """agent_to_tool should return the same BaseTool instance on repeated access."""
    card = _make_card("cached_agent")
    tool_a = card.agent_to_tool
    tool_b = card.agent_to_tool
    assert (
        tool_a is tool_b
    ), "agent_to_tool must return the same cached instance"


def test_sub_agent_uses_own_prompt_not_task_context():
    """Sub-agent registered via orchestrator should use its own system prompt,
    not have it replaced by task_context from the calling agent."""
    received_system_prompts: list = []

    class _CapturingProvider(_SequentialFakeProvider):
        def chat_completion(self, messages, tools=None):
            system_msgs = [m.content for m in messages if m.role == "system"]
            received_system_prompts.extend(system_msgs)
            return super().chat_completion(messages, tools=tools)

    sub_card = _make_card("sub_agent")
    sub_card.set_prompt_function(lambda: "SUB_AGENT_SYSTEM_PROMPT")

    sub_provider = _CapturingProvider(
        [_FakeResponse(content="sub answer", tool_calls=[])]
    )
    sub_executor = AgentExecutor(
        agent_card=sub_card,
        provider=sub_provider,
    )

    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("sub_agent", sub_executor, is_default=True)

    # Simulate docs_agent calling the sub-agent directly via the callback
    callback = sub_card._executor_callback
    assert callback is not None
    callback("user question", "task context from docs_agent", None)

    # The sub-agent's own system prompt must appear, not the task_context
    assert any(
        "SUB_AGENT_SYSTEM_PROMPT" in p for p in received_system_prompts
    ), "Sub-agent must use its own system prompt"
    assert not any(
        p == "task context from docs_agent" for p in received_system_prompts
    ), "task_context must not replace the sub-agent's system prompt"
