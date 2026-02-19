from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, Field, PrivateAttr, ValidationError


class ToolInputSchema(BaseModel):
    pass


class BaseTool(BaseModel):
    name: str = Field(..., description="Nome da ferramenta.")
    description: str = Field(..., description="Descrição da ferramenta.")
    args_schema: Type[ToolInputSchema] = Field(
        ..., description="Schema de entrada para os argumentos da ferramenta."
    )
    tool_function: Callable[..., Any] = Field(
        ..., description="Função que implementa a lógica da ferramenta."
    )

    @property
    def get_schema_for_llm(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema(),
        }

    def execute(self, **kwargs) -> Any:
        try:
            validated_args = self.args_schema(**kwargs).model_dump()
            return self.tool_function(**validated_args)
        except ValidationError as e:
            raise ValueError(
                f"Argumentos inválidos para a ferramenta {self.name}: {e}"
            )


class AgentCard(BaseModel):
    name: str = Field(..., description="Nome do agente.")
    description: str = Field(..., description="Descrição do agente.")
    tools: List[BaseTool] = Field(
        default_factory=list,
        description="Lista de ferramentas disponíveis para o agente.",
    )
    search_mode: str = Field(
        default="total",
        description="Modo de busca: 'unitary', 'group', ou 'total'",
    )
    target_groups: List[str] = Field(
        default_factory=list,
        description="Grupos alvo para busca (se aplicável)",
    )
    fallback_docs: Optional[str] = Field(
        default=None,
        description="Coleção de fallback se a busca não retornar resultados satisfatórios",
    )
    _prompt_function: Optional[Callable[..., str]] = PrivateAttr(default=None)
    _executor_callback: Optional[Callable[..., Any]] = PrivateAttr(
        default=None
    )

    def get_prompt(self, *args, **kwargs) -> Optional[str]:
        if self._prompt_function is None:
            return None
        return self._prompt_function(*args, **kwargs)

    def set_prompt_function(self, prompt_function: Callable[..., str]) -> None:
        self._prompt_function = prompt_function

    def set_executor_callback(self, callback: Callable[..., Any]) -> None:
        self._executor_callback = callback

    @property
    def get_tools_schema_for_llm(self) -> List[Dict[str, Any]]:
        return [tool.get_schema_for_llm for tool in self.tools]

    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    @property
    def agent_to_tool(self) -> BaseTool:
        class AgentToolInputSchema(ToolInputSchema):
            user_question: str = Field(
                ..., description="Pergunta do usuário para o agente."
            )
            task_context: str = Field(
                ..., description="Descrição do contexto da tarefa."
            )

        def agent_tool_function(user_question: str, task_context: str) -> str:
            if self._executor_callback:
                result = self._executor_callback(user_question, task_context)
                return (
                    result.get("content", "")
                    if isinstance(result, dict)
                    else str(result)
                )

            prompt = self.get_prompt(
                user_question=user_question, task_context=task_context
            )
            return prompt or ""

        return BaseTool(
            name=self.name,
            description=self.description,
            args_schema=AgentToolInputSchema,
            tool_function=agent_tool_function,
        )
