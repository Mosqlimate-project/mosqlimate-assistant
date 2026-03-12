from pydantic import Field

from mosqlimate_assistant.agent_cards import (
    AgentCard,
    BaseTool,
    ToolInputSchema,
)


class DummySchema(ToolInputSchema):
    text: str = Field(...)


def dummy_function(text: str) -> str:
    return text.upper()


def test_base_tool():
    tool = BaseTool(
        name="uppercase_tool",
        description="Converts text to uppercase",
        args_schema=DummySchema,
        tool_function=dummy_function,
    )
    assert tool.name == "uppercase_tool"
    assert tool.schema_for_llm["name"] == "uppercase_tool"
    assert "text" in tool.schema_for_llm["parameters"]["properties"]

    result = tool.execute(text="hello")
    assert result == "HELLO"


def test_agent_card():
    card = AgentCard(
        name="test_agent",
        description="A test agent",
    )
    assert card.name == "test_agent"
    assert card.search_mode == "total"
    assert card.fallback_threshold == 0.75

    # Prompt testing
    card.set_prompt_function(lambda x: f"Prompt: {x}")
    assert card.get_prompt("test") == "Prompt: test"

    # Executor callback testing
    card.set_executor_callback(
        lambda user_question, task_context: {
            "content": f"Res: {user_question}-{task_context}"
        }
    )
    tool = card.agent_to_tool
    assert tool.name == "test_agent"

    res = tool.execute(user_question="Q", task_context="C")
    assert res == "Res: Q-C"
