"""Agent configuration cards and tool definitions.

An ``AgentCard`` describes an agent's identity, capabilities, search
strategy, and fallback behavior. Each card can hold a list of
``BaseTool`` instances that the agent can invoke during execution,
as well as a prompt function and an executor callback.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Type  # noqa: F401

from pydantic import BaseModel, Field, PrivateAttr, ValidationError


class ToolInputSchema(BaseModel):
    """Base Pydantic schema for tool arguments.

    All specific tool schemas should inherit from this base class
    to ensure predictable validation structure.
    """

    pass


class BaseTool(BaseModel):
    """Wraps a callable with a validated input schema.

    Attributes:
        name (str): Name of the tool.
        description (str): Description of the tool.
        args_schema (Type[ToolInputSchema]): Pydantic schema to validate the arguments.
        tool_function (Callable): The function or method that implements the logic.

    """

    name: str = Field(..., description="Name of the tool.")
    description: str = Field(..., description="Description of the tool.")
    args_schema: Type[ToolInputSchema] = Field(
        ..., description="Input schema for the tool arguments."
    )
    tool_function: Callable[..., Any] = Field(
        ..., description="Function that implements the tool logic."
    )

    @property
    def schema_for_llm(self) -> Dict[str, Any]:
        """Convert the tool into an LLM-compatible JSON schema representation.

        Returns:
            Dict[str, Any]: Representation of the tool including its name,
                description, and input parameters schema.

        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema(),
        }

    def execute(self, **kwargs) -> Any:
        """Validate arguments and execute the configured tool function.

        ``_message_history`` is a special keyword that is extracted before
        Pydantic validation and forwarded to the tool function only if that
        function explicitly declares the parameter.

        Args:
            **kwargs: The arbitrary keyword arguments to pass to the tool.
                A special ``_message_history`` key may be included to thread
                conversation history into agent-type tools.

        Returns:
            Any: The result returned by the internal `tool_function`.

        Raises:
            ValueError: If the provided `kwargs` don't match the `args_schema`.

        """
        _message_history = kwargs.pop("_message_history", None)
        try:
            validated_args = self.args_schema(**kwargs).model_dump()
        except ValidationError as e:
            raise ValueError(f"Invalid arguments for tool {self.name}: {e}")

        sig = inspect.signature(self.tool_function)
        if (
            _message_history is not None
            and "_message_history" in sig.parameters
        ):
            return self.tool_function(
                **validated_args, _message_history=_message_history
            )
        return self.tool_function(**validated_args)


class AgentCard(BaseModel):
    """Declarative configuration for a specialized agent.

    It defines an agent's identity, searching strategies, fallback thresholds,
    and available tools. It also handles providing itself as a tool for
    other agents via `agent_to_tool()`.

    Attributes:
        name (str): Name of the agent.
        description (str): Description of the agent.
        tools (List[BaseTool]): Available tools for the agent.
        search_mode (str): Type of search for contextual retrieval.
        target_groups (List[str]): List of target groups to constrain the search.
        named_groups (List[List[str]]): Grouped keys to search multiple blocks simultaneously.
        group_key (str): Default metadata group key used in fallback or chunking.
        fallback_docs (Optional[str]): Primary fallback collection.
        fallback_threshold (float): Similarity threshold below which we consider fallback.

    """

    name: str = Field(..., description="Name of the agent.")
    description: str = Field(..., description="Description of the agent.")
    tools: List[BaseTool] = Field(
        default_factory=list,
        description="List of available tools for the agent.",
    )
    search_mode: str = Field(
        default="total",
        description="Search mode: 'unitary', 'group', or 'total'",
    )
    target_groups: List[str] = Field(
        default_factory=list,
        description="Target groups for search (if applicable)",
    )
    named_groups: List[List[str]] = Field(
        default_factory=list,
        description=(
            "Custom groups for search_mode='group'. "
            "Each element is a list of values from the `group_key` column "
            "of the CSV (e.g., values from the 'name' column). "
            "The search compares the query with the concatenation of each group."
        ),
    )
    group_key: str = Field(
        default="name",
        description=(
            "Metadata column used to identify documents "
            "in named_groups (default: 'name')."
        ),
    )
    fallback_docs: Optional[str] = Field(
        default=None,
        description="Fallback collection if the search does not return satisfactory results",
    )
    fallback_threshold: float = Field(
        default=0.75,
        description=(
            "Minimum score to consider the results satisfactory. "
            "If the best result falls below, triggers the fallback."
        ),
    )
    _prompt_function: Optional[Callable[..., str]] = PrivateAttr(default=None)
    _executor_callback: Optional[Callable[..., Any]] = PrivateAttr(
        default=None
    )
    _cached_tool: Optional[Any] = PrivateAttr(default=None)

    def get_prompt(self, *args, **kwargs) -> Optional[str]:
        """Evaluate the assigned prompt function to get the system message.

        Args:
            *args: Positional arguments for the prompt function.
            **kwargs: Keyword arguments for the prompt function.

        Returns:
            Optional[str]: The generated string prompt, or None if no function is set.

        """
        if self._prompt_function is None:
            return None
        return self._prompt_function(*args, **kwargs)

    def set_prompt_function(self, prompt_function: Callable[..., str]) -> None:
        """Assign a function to generate this agent's instructions based on context.

        Args:
            prompt_function (Callable): A callable returning the instruction string.

        """
        self._prompt_function = prompt_function

    def set_executor_callback(self, callback: Callable[..., Any]) -> None:
        """Assign an executor callback function for when this agent runs as a tool.

        Args:
            callback (Callable): The callback function.

        """
        self._executor_callback = callback

    @property
    def tools_schema_for_llm(self) -> List[Dict[str, Any]]:
        """Return the JSON schema representation for all attached tools.

        Returns:
            List[Dict[str, Any]]: A list of schema dictionaries.

        """
        return [tool.schema_for_llm for tool in self.tools]

    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """Look up an attached tool by its registered name.

        Args:
            name (str): The name of the tool to retrieve.

        Returns:
            Optional[BaseTool]: The tool if found, None otherwise.

        """
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    @property
    def agent_to_tool(self) -> BaseTool:
        """Expose this agent as a callable tool for multi-agent workflows.

        The returned ``BaseTool`` is cached on first access so that the same
        ``AgentToolInputSchema`` class and closure are reused on every call.

        Returns:
            BaseTool: A configured tool wrapping the agent invocation.

        """
        if self._cached_tool is not None:
            return self._cached_tool  # type: ignore[return-value]

        class AgentToolInputSchema(ToolInputSchema):
            user_question: str = Field(
                ..., description="User's question for the agent."
            )
            task_context: str = Field(
                ..., description="Description of the task context."
            )

        def agent_tool_function(
            user_question: str,
            task_context: str,
            _message_history: Optional[Any] = None,
        ) -> str:
            if self._executor_callback:
                result = self._executor_callback(
                    user_question, task_context, _message_history
                )
                if isinstance(result, dict):
                    return result.get("content", "")
                return str(result)
            return self.get_prompt() or ""

        tool = BaseTool(
            name=self.name,
            description=self.description,
            args_schema=AgentToolInputSchema,
            tool_function=agent_tool_function,
        )
        self._cached_tool = tool
        return tool
