import json
from typing import Optional, cast

import ollama
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam

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


class Assistant:
    def make_docs_query(
        self,
        similar_docs: list[dict[str, str]] = por.DEFAULT_DOCS_LIST,
    ) -> str:
        prompt = por.BASE_DOCS_PROMPT

        for doc in similar_docs:
            key = doc.get("key")
            if not isinstance(key, str):
                continue
            doc_map = utils.DOCS_KEYWORDS_MAP.get(key, None)

            if doc_map:
                doc_description = doc_map.get("description", "")
                prompt += f"\n---\n**{doc_description}**\n"

                doc_function = doc_map.get("function", None)
                if doc_function:
                    documentation = doc_function()
                    prompt += f"{documentation}\n"

        prompt += "\nAgora, responda à seguinte pergunta:\n"

        return prompt

    def execute_tool_call(self, tool_name: str, tool_args: dict) -> str:
        if tool_name in func_tools.TOOL_FUNCTIONS:
            tool_function = func_tools.TOOL_FUNCTIONS[tool_name]
            try:
                return tool_function(**tool_args)
            except Exception as e:
                return f"Erro ao executar a ferramenta {tool_name}: {str(e)}"
        else:
            return f"Ferramenta '{tool_name}' não encontrada"

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: list[dict[str, str]] = por.DEFAULT_DOCS_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        raise NotImplementedError(
            "query_llm_docs deve ser implementado nas subclasses"
        )


class AssistantOpenAI(Assistant):
    def __init__(
        self,
        api_key: Optional[str] = DEEPSEEK_API_KEY,
        base_url: Optional[str] = DEEPSEEK_API_URL,
    ):
        self.model = OpenAI(api_key=api_key, base_url=base_url)

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: list[dict[str, str]] = por.DEFAULT_DOCS_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)

        # Chama o modelo com suporte a tool calling
        response = self.model.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": full_query},
                {"role": "user", "content": prompt},
            ],
            tools=cast(
                list[ChatCompletionToolParam],
                [
                    {"type": "function", "function": schema}
                    for schema in func_tools.TOOL_SCHEMAS
                ],
            ),
            tool_choice="auto",
            stream=False,
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_results = []
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                result = self.execute_tool_call(tool_name, tool_args)
                tool_results.append(result)

            if tool_results:
                final_content = "\n\n".join(tool_results)
            else:
                final_content = (
                    message.content
                    or "Não foi possível processar a solicitação."
                )
        else:
            final_content = (
                message.content or "Não foi possível processar a solicitação."
            )

        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(final_content)],
                save_path,
            )

        return {"content": final_content}


class AssistantOllama(Assistant):
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.model_name = model_name

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: list[dict[str, str]] = por.DEFAULT_DOCS_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)

        enhanced_prompt = f"""
        {full_query}

        IMPORTANTE: Se o usuário está pedindo dados da API, códigos ou URLs, você deve responder com uma solicitação de ferramenta no formato:

        TOOL_CALL: {{
            "name": "nome_da_ferramenta",
            "arguments": {{
                "param1": "valor1",
                "param2": "valor2"
            }}
        }}

        Ferramentas disponíveis:
        - get_infodengue_data: Para dados de dengue, zika, chikungunya
        - get_climate_data: Para dados climáticos
        - get_mosquito_data: Para dados de mosquito (ContaOvos)
        - get_episcanner_data: Para dados do EpiScanner

        Pergunta: {prompt}
        """

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "user", "content": enhanced_prompt},
            ],
        )

        output = response["message"]["content"]

        if "TOOL_CALL:" in output:
            try:
                tool_start = output.find("TOOL_CALL:") + 10
                tool_json_str = output[tool_start:].strip()

                if "```" in tool_json_str:
                    tool_json_str = tool_json_str.split("```")[0]

                tool_call = json.loads(tool_json_str)
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                result = self.execute_tool_call(tool_name, tool_args)
                output = result

            except Exception as e:
                output = f"Erro ao processar solicitação de ferramenta: {str(e)}\n\nResposta original: {output}"

        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(output)],
                save_path,
            )

        return {"content": output}


class AssistantGemini(Assistant):
    def __init__(
        self,
        api_key: Optional[str] = GOOGLE_API_KEY,
        base_url: Optional[str] = GOOGLE_API_URL,
    ):
        self.api_key = api_key
        self.model = OpenAI(api_key=api_key, base_url=base_url)

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: list[dict[str, str]] = por.DEFAULT_DOCS_LIST,
        save_logs: bool = False,
        save_path: str = ".",
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)

        response = self.model.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": full_query},
                {"role": "user", "content": prompt},
            ],
            tools=cast(
                list[ChatCompletionToolParam],
                [
                    {"type": "function", "function": schema}
                    for schema in func_tools.TOOL_SCHEMAS
                ],
            ),
            tool_choice="auto",
            stream=False,
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_results = []
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                result = self.execute_tool_call(tool_name, tool_args)
                tool_results.append(result)

            if tool_results:
                final_content = "\n\n".join(tool_results)
            else:
                final_content = (
                    message.content
                    or "Não foi possível processar a solicitação."
                )
        else:
            final_content = (
                message.content or "Não foi possível processar a solicitação."
            )

        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(final_content)],
                save_path,
            )

        return {"content": final_content}
