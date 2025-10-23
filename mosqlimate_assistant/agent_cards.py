import json
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Type, Callable, Optional


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
        ..., description="Lista de ferramentas disponíveis para o agente."
    )
    _prompt_function: Optional[Callable[..., str]] = None

    def get_prompt(self, *args, **kwargs) -> str:
        if self._prompt_function is None:
            raise NotImplementedError(
                "Prompt function not implemented for this agent card."
            )
        return self._prompt_function(*args, **kwargs)

    def set_prompt_function(self, prompt_function: Callable[..., str]) -> None:
        self._prompt_function = prompt_function

    @property
    def get_tools_schema_for_llm(self) -> List[Dict[str, Any]]:
        return [tool.get_schema_for_llm() for tool in self.tools]

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
            return self.get_prompt(
                user_question=user_question, task_context=task_context
            )

        return BaseTool(
            name=self.name,
            description=self.description,
            args_schema=AgentToolInputSchema,
            tool_function=agent_tool_function,
        )
