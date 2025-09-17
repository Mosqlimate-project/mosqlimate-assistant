import json
from typing import Optional, Union, cast

import ollama
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.shared_params import FunctionDefinition

from mosqlimate_assistant import func_tools, utils
from mosqlimate_assistant.prompts import por
from mosqlimate_assistant.settings import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    GOOGLE_API_URL,
    OLLAMA_MODEL,
)

MessageParam = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
]


class Assistant:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def make_docs_query(
        self,
        similar_docs: Optional[list[dict[str, str]]] = None,
    ) -> str:
        prompt = por.BASE_DOCS_PROMPT

        docs_to_include: list[str] = []
        if similar_docs is not None:
            docs_to_include = [
                doc["key"]
                for doc in similar_docs
                if "key" in doc and isinstance(doc["key"], str)
            ]
        else:
            docs_to_include = list(utils.DOCS_KEYWORDS_MAP.keys())

        for key in docs_to_include:
            doc_map = utils.DOCS_KEYWORDS_MAP.get(key)
            if not doc_map:
                continue

            description = doc_map.get("description", "")
            prompt += f"\n---\n**{description}**\n"

            prompt += (
                f"Link para a documentação: {doc_map.get('link', 'N/A')}\n\n"
            )

            doc_function = doc_map.get("function")
            if doc_function:
                try:
                    prompt += f"{doc_function()}\n"
                except Exception as e:
                    prompt += f"(Erro ao carregar conteúdo: {str(e)})\n"

        return prompt

    def execute_tool_call(self, tool_name: str, tool_args: dict) -> str:
        tool_function = func_tools.TOOL_FUNCTIONS.get(tool_name)
        if not tool_function:
            return f"Ferramenta '{tool_name}' não encontrada"

        try:
            return tool_function(**tool_args)
        except Exception as e:
            return f"Erro ao executar a ferramenta '{tool_name}': {str(e)}"

    def build_messages(
        self,
        full_query: str,
        prompt: str,
        message_history: Optional[list[dict[str, str]]] = None,
    ) -> list[MessageParam]:

        system_content = full_query

        if message_history:
            system_content += "\n\nHistórico recente de mensagens:\n"
            for msg in message_history:
                if msg["role"] == "assistant":
                    system_content += f"\nAssistente: {msg['content']}\n"
                elif msg["role"] == "user":
                    system_content += f"\nUsuário: {msg['content']}\n"

        system_content += "\n\nAgora, responda à seguinte pergunta:\n"

        messages: list[MessageParam] = [
            ChatCompletionSystemMessageParam(
                role="system", content=system_content
            ),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]
        return messages

    def parse_tool_calls(self, message: ChatCompletionMessage) -> list[dict]:
        if not message.tool_calls:
            return []

        tool_calls = []
        for tool_call in message.tool_calls:
            tool_calls.append(
                {
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments),
                }
            )

        return tool_calls

    def handle_tool_calls(self, message: ChatCompletionMessage) -> str:
        if not message.tool_calls:
            return (
                message.content or "Não foi possível processar a solicitação."
            )

        tool_calls = self.parse_tool_calls(message)
        if not tool_calls:
            return (
                message.content or "Não foi possível processar a solicitação."
            )

        results = list()
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            results.append(self.execute_tool_call(tool_name, tool_args))

        return (
            "\n\n".join(results)
            if results
            else (
                message.content or "Não foi possível processar a solicitação."
            )
        )

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: Optional[list[dict[str, str]]] = None,
        save_logs: bool = False,
        save_path: str = ".",
        message_history: Optional[list[dict[str, str]]] = None,
    ) -> dict:
        raise NotImplementedError(
            "query_llm_docs deve ser implementado nas subclasses"
        )


class AssistantOpenAI(Assistant):
    def __init__(
        self,
        api_key: Optional[str] = DEEPSEEK_API_KEY,
        base_url: Optional[str] = DEEPSEEK_API_URL,
        model_name: str = DEEPSEEK_MODEL,
    ):
        super().__init__(model_name)
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: Optional[list[dict[str, str]]] = None,
        save_logs: bool = False,
        save_path: str = ".",
        message_history: Optional[list[dict[str, str]]] = None,
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)
        messages = self.build_messages(full_query, prompt, message_history)

        tools = [
            ChatCompletionToolParam(
                type="function", function=cast(FunctionDefinition, schema)
            )
            for schema in func_tools.TOOL_SCHEMAS
            if isinstance(schema, dict) and "name" in schema
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        content = self.handle_tool_calls(response.choices[0].message)

        if save_logs:
            utils.save_logs(
                [f"user: {prompt}", f"assistant:\n{content}"], save_path
            )

        return {"content": content}


class AssistantGemini(AssistantOpenAI):
    def __init__(
        self,
        api_key: Optional[str] = GOOGLE_API_KEY,
        base_url: Optional[str] = GOOGLE_API_URL,
    ):
        super().__init__(
            api_key=api_key, base_url=base_url, model_name=GEMINI_MODEL
        )


class AssistantOllama(Assistant):
    def __init__(self, model_name: str = OLLAMA_MODEL):
        super().__init__(model_name)

    def parse_tool_calls(self, message: ChatCompletionMessage) -> list[dict]:
        tool_calls = list()

        content = getattr(message, "content", "")
        if not content and isinstance(message, str):
            content = message

        if content and "TOOL_CALL:" in content:
            try:
                tool_json_str = (
                    content.split("TOOL_CALL:")[1].strip().split("```")[0]
                )
                tool_call = json.loads(tool_json_str)
                if "name" in tool_call:
                    tool_calls.append(
                        {
                            "name": tool_call.get("name"),
                            "arguments": tool_call.get("arguments", {}),
                        }
                    )
            except Exception:
                pass

        return tool_calls

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: Optional[list[dict[str, str]]] = None,
        save_logs: bool = False,
        save_path: str = ".",
        message_history: Optional[list[dict[str, str]]] = None,
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)
        messages = self.build_messages(full_query, prompt, message_history)

        response = ollama.chat(model=self.model_name, messages=messages)
        output = response["message"]["content"]

        message = ChatCompletionMessage(content=output, role="assistant")
        tool_calls = self.parse_tool_calls(message)

        if tool_calls:
            try:
                results = []
                for tool_call in tool_calls:
                    result = self.execute_tool_call(
                        tool_call["name"], tool_call["arguments"]
                    )
                    results.append(result)
                output = "\n\n".join(results) if results else output
            except Exception as e:
                output = f"Erro ao processar solicitação de ferramenta: {str(e)}\n\nResposta original: {output}"

        if save_logs:
            utils.save_logs(
                [f"user: {prompt}", f"assistant:\n{output}"], save_path
            )

        return {"content": output}
