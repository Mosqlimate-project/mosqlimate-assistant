# Arquivos Python em `mosqlimate_assistant`

## Índice

- [__init__.py](#__init__py)
- [assistant.py](#assistantpy)
- [coder_consumer.py](#coder_consumerpy)
- [docs_consumer.py](#docs_consumerpy)
- [func_tools.py](#func_toolspy)
- [main.py](#mainpy)
- [muni_codes.py](#muni_codespy)
- [prompts/__init__.py](#prompts__init__py)
- [prompts/eng.py](#promptsengpy)
- [prompts/por.py](#promptsporpy)
- [settings.py](#settingspy)
- [utils.py](#utilspy)
- [vector_db.py](#vector_dbpy)
- [web_cache.py](#web_cachepy)

## __init__.py
<sub>caminho: `mosqlimate_assistant/__init__.py`</sub>

```python
from importlib import metadata as importlib_metadata
from typing import List

from . import (
    assistant,
    docs_consumer,
    func_tools,
    main,
    muni_codes,
    prompts,
    settings,
    utils,
    vector_db,
)


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "1.7.2"  # changed by semantic-release


version: str = get_version()
__version__: str = version
__all__: List[str] = [
    "assistant",
    "docs_consumer",
    "func_tools",
    "vector_db",
    "muni_codes",
    "settings",
    "utils",
    "prompts",
    "main",
]  # noqa: WPS410 (the only __variable__ we use)
```

## assistant.py
<sub>caminho: `mosqlimate_assistant/assistant.py`</sub>

```python
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
from mosqlimate_assistant.coder_consumer import (
    build_coder_agent_system_prompt,
    build_coder_agent_user_prompt,
)
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

    def handle_tool_calls(
        self, message: ChatCompletionMessage, x_uid: Optional[str] = None
    ) -> str:
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

            if tool_name == "coder_agent_generate_code":
                prompt = build_coder_agent_user_prompt(
                    tool_args.get("task_description", ""),
                    tool_args.get("code_details"),
                )
                coder_response = self.query_llm_coder(prompt)
                results.append(coder_response["content"])

            else:
                results.append(self.execute_tool_call(tool_name, tool_args))

        if not results:
            return (
                message.content or "Não foi possível processar a solicitação."
            )

        final_response = "\n\n".join(results) if results else ""

        if x_uid:
            return final_response.replace("SUA_CHAVE_API", x_uid).replace(
                "# Substitua pela sua chave de API", ""
            )

        return final_response

    def query_llm_coder(self, prompt: str) -> str:
        full_query = build_coder_agent_system_prompt()
        messages = [
            ChatCompletionSystemMessageParam(
                role="system", content=full_query
            ),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]

        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages
        )

        content = response.choices[0].message.content or ""

        return {"content": content, "prompt": full_query, "messages": messages}

    def query_llm_docs(
        self,
        prompt: str,
        similar_docs: Optional[list[dict[str, str]]] = None,
        save_logs: bool = False,
        save_path: str = ".",
        message_history: Optional[list[dict[str, str]]] = None,
        x_uid: Optional[str] = None,
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
        x_uid: Optional[str] = None,
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)
        messages = self.build_messages(full_query, prompt, message_history)

        coder_tool_schema = {
            "name": "coder_agent_generate_code",
            "description": "Gera um exemplo de código a partir de uma descrição detalhada da tarefa e da documentação fornecida. Usa apenas pandas, numpy, matplotlib, mosqlient e bibliotecas simples de Python ou R.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Descrição detalhada da tarefa a ser resolvida pelo exemplo de código, se necessário adicione os parâmetros das tabelas e explique o que eles são.",
                    },
                    "code_details": {
                        "type": "string",
                        "description": "Detalhes adicionais sobre o código desejado, formato, linguagem, bibliotecas, etc.",
                        "default": "",
                    },
                },
                "required": ["task_description"],
            },
        }
        tools = []
        tools.append(
            ChatCompletionToolParam(
                type="function",
                function=cast(FunctionDefinition, coder_tool_schema),
            )
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        content = self.handle_tool_calls(
            response.choices[0].message, x_uid=x_uid
        )

        if save_logs:
            utils.save_logs(
                [f"user: {prompt}", f"assistant:\n{content}"], save_path
            )

        return {"content": content, "prompt": full_query, "messages": messages}


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
        x_uid: Optional[str] = None,
    ) -> dict:
        full_query = self.make_docs_query(similar_docs)
        messages = self.build_messages(full_query, prompt, message_history)

        response = ollama.chat(model=self.model_name, messages=messages)
        output = response["message"]["content"]

        message = ChatCompletionMessage(content=output, role="assistant")
        tool_calls = self.parse_tool_calls(message)

        if tool_calls:
            try:
                results = list()
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

        return {"content": output, "prompt": full_query, "messages": messages}
```

## coder_consumer.py
<sub>caminho: `mosqlimate_assistant/coder_consumer.py`</sub>

```python
import json
import re
from typing import Optional

import pandas as pd
import requests

from mosqlimate_assistant.prompts import por
from mosqlimate_assistant.settings import CODE_REFERENCES_PATH
from mosqlimate_assistant.web_cache import shared_cache_session


def fetch_file_content(url: str) -> str:
    try:
        response = shared_cache_session.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Erro ao buscar o arquivo {url}: {e}"


def process_documentation_file(
    base_url: str, doc_path: str, file_content: str
) -> str:
    # Processa inclusões de arquivos (--8<--)
    for match in re.finditer(r'--8<-- "(.*?)"', file_content):
        include_path = match.group(1)
        included_content = fetch_file_content(base_url + include_path)
        file_content = file_content.replace(match.group(0), included_content)

    # Processa referências do mkdocstrings (:::)
    for match in re.finditer(r"::: ([\w\._]+)", file_content):
        module_path = match.group(1)
        py_file_path = module_path.replace(".", "/") + ".py"
        module_content_url = base_url + py_file_path
        module_content = fetch_file_content(module_content_url)
        replacement = (
            f"\n---\n"
            f"*Conteúdo de `{py_file_path}`:*\n\n"
            f"```python\n{module_content}\n```\n"
        )
        file_content = file_content.replace(match.group(0), replacement)

    # Processa Jupyter Notebooks
    if doc_path.endswith(".ipynb"):
        try:
            notebook = json.loads(file_content)
            markdown_output = ""
            for cell in notebook.get("cells", []):
                source = "".join(cell.get("source", []))
                if cell.get("cell_type") == "markdown":
                    markdown_output += source + "\n\n"
                elif cell.get("cell_type") == "code":
                    lang = (
                        notebook.get("metadata", {})
                        .get("kernelspec", {})
                        .get("language", "python")
                    )
                    markdown_output += f"```{lang}\n{source}\n```\n\n"
            return markdown_output
        except json.JSONDecodeError:
            return f"Erro: Não foi possível decodificar o JSON do notebook {doc_path}"

    return file_content


def fetch_full_documentation_from_csv(csv_path: str) -> str:
    df = pd.read_csv(csv_path)
    final_output = ""

    for index, row in df.iterrows():
        name = row["name"]
        github_url = row["markdown_link"]
        reference_link = row["url_link"]

        parts = github_url.split("/")
        repo_base_index = parts.index("mosqlimate-client") + 2
        base_url = "/".join(parts[:repo_base_index]) + "/"
        doc_path = "/".join(parts[repo_base_index:])

        final_output += f"# {name}\n"
        final_output += f"[Link de Referência]({reference_link})\n\n"

        file_content = fetch_file_content(github_url)
        processed_content = process_documentation_file(
            base_url, doc_path, file_content
        )

        final_output += processed_content + "\n---\n"
    return final_output.strip()


def build_coder_agent_system_prompt() -> str:
    docs_content = fetch_full_documentation_from_csv(CODE_REFERENCES_PATH)
    prompt = por.BASE_DOCS_PROMPT
    prompt += f"\n\n# Documentação Fornecida\n{docs_content}\n"
    return prompt


def build_coder_agent_user_prompt(
    task_description: str, code_details: Optional[str] = None
) -> str:
    prompt = f"# Descrição da tarefa\n{task_description}\n"
    if code_details:
        prompt += f"\n## Detalhes adicionais\n{code_details}\n"
    return prompt


def tool_call_coder_agent(
    task_description: str, code_details: str = ""
) -> str:
    return json.dumps(
        {"task_description": task_description, "code_details": code_details}
    )
```

## docs_consumer.py
<sub>caminho: `mosqlimate_assistant/docs_consumer.py`</sub>

```python
from typing import List

from mosqlimate_assistant.settings import MOSQLIMATE_API_DOCS_JSON
from mosqlimate_assistant.web_cache import shared_cache_session


def get_mosqlimate_api_docs() -> dict:
    url = MOSQLIMATE_API_DOCS_JSON
    response = shared_cache_session.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(
            f"Erro ao obter a documentação da API: {response.status_code}"
        )


def get_mosqlimate_description() -> dict:
    data = get_mosqlimate_api_docs()
    description = data.get("info", {}).get("description", "")
    return description


def get_mosqlimate_api_schemas() -> dict:
    data = get_mosqlimate_api_docs()
    schemas = data.get("components", {}).get("schemas", {})
    return schemas


def get_mosqlimate_api_paths() -> dict:
    data = get_mosqlimate_api_docs()
    paths = data.get("paths", {})
    return paths


def get_mosqlimate_path(path: str) -> dict:
    data = get_mosqlimate_api_docs()
    paths = data.get("paths", {})
    return paths.get(path, {})


def format_api_parameters(api_json: dict) -> dict:
    parameters = api_json.get("parameters", [])
    formatted_parameters = list()

    for param in parameters:
        name = param.get("name")

        if name == "page" or name == "per_page":
            continue

        required = param.get("required", False)
        schema = param.get("schema", {})

        if "anyOf" in schema:
            any_of = schema.get("anyOf")
            nullable = any(item.get("type") == "null" for item in any_of)
            non_null_schemas = [s for s in any_of if s.get("type") != "null"]
            if non_null_schemas:
                schema = non_null_schemas[0]
            else:
                schema = {}
        else:
            nullable = False

        type_info = schema.get("type")
        enum = schema.get("enum")
        default = schema.get("default")
        format_ = schema.get("format")

        param_dict = {
            "name": name,
            "type": type_info,
            "required": required,
        }

        if enum:
            enum_ = [e for e in enum if e != "chik"]
            param_dict["enum"] = enum_
        if default:
            param_dict["default"] = default
        if format_:
            param_dict["format"] = format_
        if nullable:
            param_dict["nullable"] = True

        formatted_parameters.append(param_dict)

    return {"parameters": formatted_parameters}


# Funções para consumir documentação em Markdown


def get_content_from_url(url: str) -> str:
    response = shared_cache_session.get(url)
    response.raise_for_status()
    return response.text


def get_all_docs(docs_map: dict) -> List[dict]:
    all_docs = []
    for name, data in docs_map.items():
        markdown_link = data.get("markdown_link")
        if markdown_link:
            content = get_content_from_url(markdown_link)
            all_docs.append({"name": name, "content": content})
    return all_docs
```

## func_tools.py
<sub>caminho: `mosqlimate_assistant/func_tools.py`</sub>

```python
from typing import Any, Callable, Dict, List, Optional

from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.settings import BASE_URL_API, Diseases, UFs
from mosqlimate_assistant.utils import DOCS_KEYWORDS_MAP


def get_infodengue_data(
    disease: Diseases,
    start: str,
    end: str,
    uf: Optional[UFs] = None,
    city: Optional[str] = None,
    page: int = 1,
    per_page: int = 100,
) -> str:
    disease_map = {
        "chikungunya": "chikungunya",
        "chick": "chikungunya",
        "dengue": "dengue",
        "zika": "zika",
    }
    api_disease = disease_map.get(disease, disease)

    infodengue_link = DOCS_KEYWORDS_MAP.get("datastore_infodengue", {}).get(
        "link", ""
    )

    base_url = f"{BASE_URL_API}infodengue/"
    params: Dict[str, str | int] = {
        "disease": api_disease,
        "start": start,
        "end": end,
    }

    if uf:
        params["uf"] = uf
    if city and uf:
        geocode = get_municipality_code(city, uf)
        params["geocode"] = geocode

    params["per_page"] = min(per_page, 100)
    params["page"] = page

    params_markdown = "- " + "\n- ".join(
        [f"`{k}`: `{v}`" for k, v in params.items()]
    )

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"

    mosqlient_example = f"""import mosqlient

df = mosqlient.get_infodengue(api_key='SUA_CHAVE_API', # Substitua pela sua chave de API

&emsp;disease='{disease}', start_date='{start}', end_date='{end}'"""

    if uf:
        mosqlient_example += f", uf='{uf}'"
    if params.get("geocode"):
        mosqlient_example += f", geocode={params['geocode']}"

    mosqlient_example += ")\n\nprint(df.head())"

    response_text = f"""
Consulta para a API do InfoDengue:

**[URL da API: {full_url}]({full_url})**

**Parâmetros Utilizados:**
{params_markdown}

**Exemplo de Código Python com mosqlient (Recomendado):**

{mosqlient_example}

"""
    if infodengue_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial do InfoDengue: [{infodengue_link}]({infodengue_link})"""
    return response_text.strip()


def get_climate_data(
    start: str,
    end: str,
    uf: Optional[UFs] = None,
    city: Optional[str] = None,
    page: int = 1,
    per_page: int = 100,
) -> str:
    base_url = f"{BASE_URL_API}climate/"
    params: Dict[str, str | int] = {
        "start": start,
        "end": end,
    }

    climate_link = DOCS_KEYWORDS_MAP.get("datastore_climate", {}).get(
        "link", ""
    )

    if uf:
        params["uf"] = uf
    if city and uf:
        geocode = get_municipality_code(city, uf)
        params["geocode"] = geocode

    params["page"] = page
    params["per_page"] = min(per_page, 100)

    params_markdown = "- " + "\n- ".join(
        [f"`{k}`: `{v}`" for k, v in params.items()]
    )

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"

    mosqlient_example = f"""import mosqlient

df = mosqlient.get_climate(api_key='SUA_CHAVE_API', # Substitua pela sua chave de API

&emsp;start_date='{start}', end_date='{end}'"""

    if uf:
        mosqlient_example += f", uf='{uf}'"
    if params.get("geocode"):
        mosqlient_example += f", geocode={params['geocode']}"

    mosqlient_example += ")\n\nprint(df.head())"

    response_text = f"""
Consulta para a API de dados climáticos gerada:

**[URL da API: {full_url}]({full_url})**

**Parâmetros Utilizados:**
{params_markdown}

**Exemplo de Código Python com mosqlient (Recomendado):**

{mosqlient_example}

"""
    if climate_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial de dados climáticos: [{climate_link}]({climate_link})"""
    return response_text.strip()


def get_mosquito_data(
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    state: Optional[UFs] = None,
    municipality: Optional[str] = None,
    page: int = 1,
) -> str:
    base_url = f"{BASE_URL_API}mosquito/"
    params: Dict[str, str | int] = {}

    mosquito_link = DOCS_KEYWORDS_MAP.get("datastore_mosquito", {}).get(
        "link", ""
    )

    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end
    if state:
        params["state"] = state
    if municipality:
        params["municipality"] = municipality
    if page > 1:
        params["page"] = str(page)

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}" if params else base_url

    params_markdown = (
        "- " + "\n- ".join([f"`{k}`: `{v}`" for k, v in params.items()])
        if params
        else "Nenhum parâmetro utilizado."
    )

    mosqlient_example = """import mosqlient

df = mosqlient.get_mosquito(api_key="SUA_CHAVE_API", # Substitua pela sua chave de API\n
"""

    if date_start:
        mosqlient_example += f"&emsp;date_start='{date_start}'"
    if date_end:
        mosqlient_example += f", date_end='{date_end}'"
    if state:
        mosqlient_example += f", state='{state}'"
    if municipality:
        mosqlient_example += f", municipality='{municipality}'"

    mosqlient_example += ")\n\nprint(df.head())"

    response_text = f"""
Consulta para a API de dados de mosquito gerada:

**[URL da API: {full_url}]({full_url})**

**Parâmetros Utilizados:**
{params_markdown}

**Exemplo de Código Python com mosqlient (Recomendado):**

{mosqlient_example}

"""
    if mosquito_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial do ContaOvos: [{mosquito_link}]({mosquito_link})"""
    return response_text.strip()


def get_episcanner_data(
    disease: Diseases,
    uf: UFs,
    year: Optional[int] = None,
) -> str:
    disease_map = {"chikungunya": "chik", "dengue": "dengue", "zika": "zika"}
    api_disease = disease_map.get(disease, disease)

    episcanner_link = DOCS_KEYWORDS_MAP.get("datastore_episcanner", {}).get(
        "link", ""
    )

    base_url = f"{BASE_URL_API}episcanner/"
    params: Dict[str, str | int] = {
        "disease": api_disease,
        "uf": uf,
    }

    if year:
        params["year"] = str(year)

    params_markdown = "- " + "\n- ".join(
        [f"`{k}`: `{v}`" for k, v in params.items()]
    )

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"

    mosqlient_example = f"""import mosqlient

df = mosqlient.get_episcanner(api_key='SUA_CHAVE_API', # Substitua pela sua chave de API

&emsp;disease='{disease}', uf='{uf}'"""

    if year:
        mosqlient_example += f", year={year}"

    mosqlient_example += ")\n\nprint(df.head())"

    response_text = f"""
Consulta para a API do EpiScanner gerada:

**[URL da API: {full_url}]({full_url})**

**Parâmetros Utilizados:**
{params_markdown}

**Exemplo de Código Python com mosqlient (Recomendado):**

{mosqlient_example}

"""
    if episcanner_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial do EpiScanner: [{episcanner_link}]({episcanner_link})"""
    return response_text.strip()


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "get_infodengue_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados epidemiológicos do InfoDengue sobre doenças transmitidas por mosquitos (dengue, zika, chikungunya). Fornece dados semanais com estimativas de casos, níveis de alerta e variáveis climáticas.",
        "parameters": {
            "type": "object",
            "properties": {
                "disease": {
                    "type": "string",
                    "enum": ["dengue", "zika", "chikungunya"],
                    "description": "A doença a ser consultada: 'dengue', 'zika' ou 'chikungunya'",
                },
                "start": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de início da consulta (formato YYYY-MM-DD, semana epidemiológica)",
                },
                "end": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de término da consulta (formato YYYY-MM-DD, semana epidemiológica)",
                },
                "uf": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "A sigla do estado brasileiro (duas letras), ex: SP",
                },
                "city": {
                    "type": "string",
                    "description": "O nome do município",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Página a ser exibida (padrão: 1)",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Quantos itens por página, até 100 (padrão: 100)",
                },
            },
            "required": ["disease", "start", "end"],
        },
    },
    {
        "name": "get_climate_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados climáticos diários da API Mosqlimate. Fornece séries temporais de variáveis climáticas baseadas em dados de satélite ERA5 da Copernicus.",
        "parameters": {
            "type": "object",
            "properties": {
                "start": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de início da consulta (formato YYYY-MM-DD)",
                },
                "end": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de término da consulta (formato YYYY-MM-DD)",
                },
                "uf": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "A sigla do estado brasileiro (duas letras), ex: SP",
                },
                "city": {
                    "type": "string",
                    "description": "O nome do município",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Página a ser exibida (padrão: 1)",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Quantos itens por página, até 100 (padrão: 100)",
                },
            },
            "required": ["start", "end"],
        },
    },
    {
        "name": "get_mosquito_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados do ContaOvos (monitoramento de mosquitos). Fornece dados de abundância de mosquitos baseados em armadilhas de ovos distribuídas pelo Brasil.",
        "parameters": {
            "type": "object",
            "properties": {
                "date_start": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Data de início no formato ISO (YYYY-MM-DD, opcional)",
                },
                "date_end": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Data de fim no formato ISO (YYYY-MM-DD, opcional)",
                },
                "state": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "Sigla do estado brasileiro (UF, opcional)",
                },
                "municipality": {
                    "type": "string",
                    "description": "Nome do município (opcional)",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Página a ser exibida (padrão: 1)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_episcanner_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados do EpiScanner sobre parâmetros epidemiológicos e expansão de epidemias. Fornece estimativas de R0, taxa de transmissibilidade e duração de epidemias.",
        "parameters": {
            "type": "object",
            "properties": {
                "disease": {
                    "type": "string",
                    "enum": ["dengue", "zika", "chikungunya"],
                    "description": "A doença a ser consultada: 'dengue', 'zika' ou 'chikungunya'",
                },
                "uf": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "A sigla do estado brasileiro (duas letras), ex: SP",
                },
                "year": {
                    "type": "integer",
                    "minimum": 2010,
                    "maximum": 2030,
                    "description": "O ano específico para consulta (opcional, padrão: ano atual)",
                },
            },
            "required": ["disease", "uf"],
        },
    },
]


TOOL_FUNCTIONS: Dict[str, Callable[..., str]] = {
    "get_infodengue_data": get_infodengue_data,
    "get_climate_data": get_climate_data,
    "get_mosquito_data": get_mosquito_data,
    "get_episcanner_data": get_episcanner_data,
}
```

## main.py
<sub>caminho: `mosqlimate_assistant/main.py`</sub>

```python
from typing import Dict, List, Optional

from mosqlimate_assistant import assistant, utils, vector_db


def docs_pipeline(
    question: str,
    similar_docs: Optional[List[Dict[str, str]]] = None,
    x_uid: Optional[str] = None,
    message_history: Optional[list[dict[str, str]]] = None,
) -> str:
    mosqlimate_assistant = assistant.AssistantGemini()

    if similar_docs is None:
        similar_docs = [
            {
                "key": key,
                "category": value["category"],
                "description": value["description"],
                "link": value.get("link", ""),
            }
            for key, value in utils.DOCS_KEYWORDS_MAP.items()
        ]

    result = mosqlimate_assistant.query_llm_docs(
        prompt=question,
        similar_docs=similar_docs,
        x_uid=x_uid,
        message_history=message_history,
    )
    return result["content"]


def assistant_pipeline(
    question: str,
    k_num: int = 4,
    full_context: bool = True,
    x_uid: Optional[str] = None,
    message_history: Optional[list[dict[str, str]]] = None,
) -> str:
    if full_context:
        similar_docs = [
            {
                "key": key,
                "category": value["category"],
                "description": value["description"],
                "link": value.get("link", ""),
            }
            for key, value in utils.DOCS_KEYWORDS_MAP.items()
        ]
    else:
        relevant_docs, docs_scores = vector_db.get_relevant_docs(
            question, k=k_num
        )
        similar_docs = [
            doc
            for doc, score in zip(relevant_docs, docs_scores)
            if score > 0.5
        ]
    return docs_pipeline(
        question, similar_docs, x_uid=x_uid, message_history=message_history
    )
```

## muni_codes.py
<sub>caminho: `mosqlimate_assistant/muni_codes.py`</sub>

```python
import json
from typing import Any, Optional

import Levenshtein

from mosqlimate_assistant.settings import MUNICIPALITIES_PATH, VALID_UFS


def get_closest_match(
    input_text: str, options: list[dict[str, Any]]
) -> tuple[dict[str, Any], float]:
    closest_match: dict[str, Any] = {
        "Municipality": "",
        "UF": "",
        "Code": "",
        "distance": float("inf"),
    }
    for option in options:
        distance = float(
            Levenshtein.distance(input_text, option["Municipality"])
        )
        if distance < closest_match["distance"]:
            closest_match = {**option, "distance": distance}
    return closest_match, closest_match["distance"]


def read_municipalities() -> list[dict[str, Any]]:
    with open(MUNICIPALITIES_PATH, "r") as file:
        municipalities = json.load(file)

        for m in municipalities:
            m["Municipality"] = m["Municipality"].lower().strip()

    return municipalities


def filter_by_uf(municipalities: list[dict], uf: str) -> list[dict]:
    if uf.upper() not in VALID_UFS:
        raise ValueError(f"UF inválida: {uf}")

    filtered = [m for m in municipalities if m["UF"] == uf.upper()]
    return filtered


def get_municipality(name: str, uf: str | None = None) -> dict:
    name = name.lower().strip()

    municipalities = read_municipalities()
    closest_match, closest_distance = get_closest_match(name, municipalities)

    if uf and closest_match["UF"] != uf.upper():
        municipalities_filter = filter_by_uf(municipalities, uf)
        closest_match_filter, closest_distance_filter = get_closest_match(
            name, municipalities_filter
        )

        if (
            closest_match_filter["Code"] != closest_match["Code"]
            and closest_distance_filter <= closest_distance
        ):
            closest_match = closest_match_filter
            closest_distance = closest_distance_filter

    if closest_distance > 4:
        raise ValueError(f"Município não encontrado: {name}")

    return closest_match


def get_municipality_code(municipality: str, uf: Optional[str]) -> int:
    try:
        municipality_code = get_municipality(municipality, uf)
        return municipality_code["Code"]
    except ValueError as ve:
        raise RuntimeError(f"Erro ao obter o código do município: {ve}")
    except Exception as e:
        raise RuntimeError(f"Erro ao obter o código do município: {e}")


def get_muni_and_uf_from_code(code: str) -> tuple[str, str]:
    municipalities = read_municipalities()
    for m in municipalities:
        if m["Code"] == code:
            return m["Municipality"], m["UF"]
    raise ValueError(f"Código de município não encontrado: {code}")
```

## prompts/__init__.py
<sub>caminho: `mosqlimate_assistant/prompts/__init__.py`</sub>

```python
from . import eng, por

__all__ = [
    "eng",
    "por",
]
```

## prompts/eng.py
<sub>caminho: `mosqlimate_assistant/prompts/eng.py`</sub>

```python

```

## prompts/por.py
<sub>caminho: `mosqlimate_assistant/prompts/por.py`</sub>

```python
from datetime import datetime

from mosqlimate_assistant import utils

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

BASE_DOCS_PROMPT = f"""Você é um assistente amigável e especialista na plataforma Mosqlimate. Sua principal função é ajudar os usuários a entender e utilizar a plataforma, transformando a documentação técnica em respostas claras e práticas.

Considere a data de hoje: {CURRENT_DATE}.

**COMO VOCÊ DEVE SE COMPORTAR:**
- **Seja um Guia, Não um Robô:** Em vez de apenas citar a documentação, explique os conceitos. Sintetize informações de diferentes partes da documentação para fornecer uma resposta completa.
- **Use Apenas a Documentação Fornecida:** Baseie TODAS as suas respostas estritamente nas informações contidas na documentação oficial fornecida no contexto. NUNCA invente funcionalidades, endpoints ou parâmetros.
- **Sempre que possível, inclua o link oficial da documentação Mosqlimate na sua resposta, para que o usuário possa consultar diretamente.**
- **Use Linguagem Acessível:** Evite jargões técnicos sempre que possível. Se precisar usá-los, explique o que significam.
- **Mantenha-se no Tópico:** Responda exclusivamente a perguntas sobre a plataforma Mosqlimate, seus dados, API e funcionalidades. Se a pergunta for fora do escopo, informe educadamente que você só pode ajudar com tópicos relacionados ao Mosqlimate.
- **Seja Direto:** Forneça respostas claras e concisas, tente manter as respostas curtas, resuma o que for possível.
- **Use Ferramentas:** Se detectar uma solicitação de dados, use as ferramentas disponíveis para fornecer URLs e códigos precisos, use elas apenas se tiver os parâmetros necessários.
- **Instrua o Usuário:** Se a pergunta de um usuário for vaga, tente entender a intenção e sugira o que ele pode estar procurando, ou os parâmetros que faltam.
- **Responda no Idioma do Usuário:** Mantenha a conversação no mesmo idioma em que a pergunta foi feita.
- **Use o contexto histórico:** Utilize o histórico de mensagens para entender melhor a pergunta do usuário e fornecer uma resposta mais contextualizada se necessário.

**O QUE VOCÊ NÃO DEVE FAZER:**
- Fornecer opiniões pessoais ou informações não verificadas.
- Compartilhar chaves de API ou credenciais de qualquer tipo.
- Escrever código em linguagens não suportadas (suporte apenas Python e R).
- Inventar URLs ou parâmetros - sempre use as ferramentas quando necessário.

**FERRAMENTAS DISPONÍVEIS:**
Você tem acesso a ferramentas especiais para consultar a API Mosqlimate. Quando o usuário solicitar dados específicos, URLs de API ou códigos de exemplo, use as ferramentas apropriadas:
- **coder_agent_generate_code**: Para gerar exemplos de código em Python ou R com base na documentação oficial do Mosqlimate.

**QUANDO USAR AS FERRAMENTAS:**
- Quando o usuário pedir dados da API, URLs, endpoints ou códigos.
- Quando todos os parâmetros necessários forem fornecidos.
- Quando mencionar doenças específicas (dengue, zika, chikungunya).
- Quando solicitar informações ou dados climáticos.
- Quando pedir dados de mosquitos ou ContaOvos.
- Quando mencionar epidemias, surtos ou expansão de doenças.
"""

DEFAULT_DOCS_LIST = [
    {
        "key": key,
        "category": value["category"],
        "description": value["description"],
        "link": value.get("link", ""),
    }
    for key, value in utils.DOCS_KEYWORDS_MAP.items()
]

CODER_AGENT_PROMPT = f"""Você é um assistente especializado em gerar exemplos de código com base na documentação fornecida. Sua tarefa é criar scripts claros, funcionais e simples, utilizando apenas bibliotecas simples de Python (como pandas, numpy, matplotlib, mosqlient) ou R, conforme necessário.

Considere a data de hoje: {CURRENT_DATE}.

**COMO VOCÊ DEVE SE COMPORTAR:**
- **Baseie-se na Documentação:** Use exclusivamente as informações fornecidas na documentação para criar os exemplos de código. Não invente funcionalidades ou parâmetros.
- **Foque na Simplicidade:** Garanta que o código seja simples, legível e bem comentado, para que até mesmo iniciantes possam entendê-lo, não dê explicações extras muito longas ou complexas, deixe elas curtas e diretas, não faça if, else, try e exept desnecessários, use apenas se precisar.
- **Não saia do escopo:** Responda apenas a perguntas relacionadas à geração de código com base na documentação fornecida do mosqlient.
- **Utilize Bibliotecas Permitidas:** Limite-se às bibliotecas mencionadas (pandas, numpy, matplotlib, mosqlient para Python e bibliotecas padrão do R).
- **Explique o Código:** Sempre inclua comentários explicativos no código para descrever o que cada parte faz.
- **Responda no Idioma do Usuário:** Mantenha a explicação e os comentários no mesmo idioma da pergunta.
- **Instrua o usuário sobre a chave api** Sempre que necessário inserir a chave de api, use `'YOUR_X_UID_Key', # Substitua aqui pela sua chave de api` como placeholder, nunca insira uma chave real ou use dotenv. ****

**O QUE VOCÊ NÃO DEVE FAZER:**
- Usar bibliotecas ou ferramentas não mencionadas.
- Criar exemplos que não sejam funcionais ou que dependam de configurações externas complexas.
- Fornecer explicações vagas ou incompletas.
- Responder a perguntas fora do escopo de geração de código do mosqlient.

**FORMATO DO EXEMPLO:**
1. Inclua uma breve introdução explicando o objetivo do código, com referências à documentação.
2. Forneça o código completo, com comentários detalhados.
3. Certifique-se de que o código esteja pronto para ser executado sem modificações adicionais.
"""
```

## settings.py
<sub>caminho: `mosqlimate_assistant/settings.py`</sub>

```python
import os
import urllib.request
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Mosqlimate API URLs
MOSQLIMATE_API_DOCS_JSON = "https://api.mosqlimate.org/api/openapi.json"


BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"


# Models
OLLAMA_MODEL = "llama3.2:latest"

DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com"

GEMINI_MODEL = "gemini-2.5-flash"
GOOGLE_API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


# Relative Paths
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(CURRENT_PATH, "../.env")


# Default Values
DEFAULT_API_KEY = "sk-"
DEFAULT_DATABASE_PATH = "data"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"


# Environment Variables
class Settings(BaseSettings):
    deepseek_api_key: str = DEFAULT_API_KEY
    google_api_key: str = DEFAULT_API_KEY
    database_path: str = DEFAULT_DATABASE_PATH
    embedding_model: str = DEFAULT_EMBEDDING_MODEL

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
    )


settings = Settings()

DEEPSEEK_API_KEY = settings.deepseek_api_key
GOOGLE_API_KEY = settings.google_api_key
EMBEDDING_MODEL = settings.embedding_model
DATABASE_PATH = settings.database_path


# Caminhos dos arquivos
MUNICIPALITIES_PATH = os.path.join(
    CURRENT_PATH, DATABASE_PATH, "municipios.json"
)
ASKS_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks.csv")
KEYWORDS_MAP_PATH = os.path.join(
    CURRENT_PATH, DATABASE_PATH, "keywords_map.csv"
)
ASKS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks_db")
DOCS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "docs_db")
BLOCKS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "blocks_db")
ASKS_VECTOR_DB_PATH = os.path.join(
    os.path.dirname(ASKS_PATH), "vector_dbs", "asks_chroma"
)
DOCS_VECTOR_DB_PATH = os.path.join(
    os.path.dirname(DOCS_DB_PATH), "vector_dbs", "docs_chroma"
)
CODE_REFERENCES_PATH = os.path.join(
    CURRENT_PATH, DATABASE_PATH, "code_references.csv"
)

MUNICIPALITIES_URL = "https://raw.githubusercontent.com/Mosqlimate-project/mosqlimate-assistant/refs/heads/main/mosqlimate_assistant/data/municipios.json"
ASKS_URL = "https://raw.githubusercontent.com/Mosqlimate-project/mosqlimate-assistant/refs/heads/main/mosqlimate_assistant/data/asks.csv"
KEYWORDS_MAP_URL = "https://raw.githubusercontent.com/Mosqlimate-project/mosqlimate-assistant/refs/heads/main/mosqlimate_assistant/data/keywords_map.csv"


def ensure_file_exists(local_path: str, remote_url: str):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not os.path.exists(local_path):
        try:
            urllib.request.urlretrieve(remote_url, local_path)
        except Exception as e:
            print(f"Erro ao baixar {local_path}: {e}")


ensure_file_exists(MUNICIPALITIES_PATH, MUNICIPALITIES_URL)
ensure_file_exists(ASKS_PATH, ASKS_URL)
ensure_file_exists(KEYWORDS_MAP_PATH, KEYWORDS_MAP_URL)

VALID_UFS = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]

Diseases = Literal[
    "dengue",
    "zika",
    "chikungunya",
]

UFs = Literal[
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]
```

## utils.py
<sub>caminho: `mosqlimate_assistant/utils.py`</sub>

```python
import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import requests

from mosqlimate_assistant.settings import KEYWORDS_MAP_PATH


def get_content_from_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def save_logs(logs: list[str], save_path: str = ".") -> None:
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    save_file = os.path.join(save_path, "prompt_logs.txt")
    with open(save_file, "a") as file:
        for log in logs:
            file.write(log)
            file.write("\n")
        file.write("\n\n")


def format_answer(answer: str) -> str:
    ans_dict = json.loads(answer)
    answer = "```json\n"
    answer += json.dumps(ans_dict, indent=2) + "\n```"

    return answer


def load_keywords_from_csv(file_path: Path) -> Dict[str, Dict[str, Any]]:
    keywords_map = {}
    with open(file_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            name = row["name"]
            keywords_map[name] = {
                "markdown_link": row["markdown_link"],
                "url_link": row["url_link"],
                "keywords": [
                    keyword.strip() for keyword in row["keywords"].split("-")
                ],
            }
    return keywords_map


def get_full_docs_map() -> Dict[str, Dict[str, Any]]:
    keywords_map = load_keywords_from_csv(Path(KEYWORDS_MAP_PATH))

    for name, data in keywords_map.items():
        data["function"] = lambda url=data[
            "markdown_link"
        ]: get_content_from_url(url)
        data["category"] = name.split("_")[0] if "_" in name else "other"
        data["link"] = data["url_link"]
        data["description"] = f"Documentação sobre {name}"

    return keywords_map


DOCS_KEYWORDS_MAP = get_full_docs_map()

DOCS_BLOCKS_MAP = {
    # Bloco 1: Projeto, equipe, autenticação, plataforma
    "project_block": [
        "project_main",
        "project_team",
        "data_platform",
        "uid_key",
    ],
    # Bloco 2: Todos os datastores
    "datastore_block": [
        "datastore_base",
        "datastore_infodengue",
        "datastore_episcanner",
        "datastore_climate",
        "datastore_climate_weekly",
        "datastore_mosquito",
        "project_ovicounter",
    ],
    # Bloco 3: Registro, modelos, previsões, autores
    "registry_block": [
        "registry_base",
        "registry_predictions_get",
        "registry_predictions_post",
        "registry_models_get",
        "registry_models_post",
        "registry_authors_get",
    ],
    # Bloco 4: Todos os documentos juntos
    "all_docs_block": [
        "project_main",
        "project_team",
        "data_platform",
        "uid_key",
        "datastore_base",
        "datastore_infodengue",
        "datastore_episcanner",
        "datastore_climate",
        "datastore_climate_weekly",
        "datastore_mosquito",
        "project_ovicounter",
        "registry_base",
        "registry_predictions_get",
        "registry_predictions_post",
        "registry_models_get",
        "registry_models_post",
        "registry_authors_get",
    ],
}


def get_formated_keywords_docs_map() -> dict:
    formatted_map = dict()
    for key, value in DOCS_KEYWORDS_MAP.items():
        keywords_list: List[str] = value.get("keywords", [])
        formatted_map[key] = {
            "keywords": ", ".join(keywords_list),
            "category": value.get("category", "other"),
            "description": value.get("description", "N/A"),
            "link": value.get("link", ""),
        }
    return formatted_map


def get_formated_docs_map() -> dict:
    formatted_map = dict()
    for key, value in DOCS_KEYWORDS_MAP.items():
        formatted_map[key] = {
            "link": value.get("link", ""),
            "function": value.get("function", lambda: ""),
            "keywords": ", ".join(value.get("keywords", [])),
            "category": value.get("category", "other"),
            "description": value.get("description", "N/A"),
        }
    return formatted_map
```

## vector_db.py
<sub>caminho: `mosqlimate_assistant/vector_db.py`</sub>

```python
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import ollama
import pandas as pd
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from mosqlimate_assistant import utils
from mosqlimate_assistant.settings import (
    ASKS_DB_PATH,
    ASKS_PATH,
    BLOCKS_DB_PATH,
    DOCS_DB_PATH,
    EMBEDDING_MODEL,
)


class OllamaEmbeddingWrapper(Embeddings):
    def __init__(self, model: str, base_url: Optional[str] = None):
        self.model = model
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        arr = np.asarray(vector, dtype=float)
        norm = np.linalg.norm(arr)
        return (arr / norm).tolist() if norm > 0 else vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [
            self._normalize(
                self.client.embeddings(model=self.model, prompt=text)[
                    "embedding"
                ]
            )
            for text in texts
        ]

    def embed_query(self, text: str) -> List[float]:
        vec = self.client.embeddings(model=self.model, prompt=text)[
            "embedding"
        ]
        return self._normalize(vec)


class VectorDB:
    def __init__(
        self,
        embedding_model: str = EMBEDDING_MODEL,
        embedding_column: str = "keywords",
    ):
        self.embedding_model = embedding_model
        self.embedding_column = embedding_column
        self.embedding_function = OllamaEmbeddingWrapper(
            model=embedding_model,
            base_url=os.getenv("OLLAMA_URL"),
        )
        self.embeddings: Optional[np.ndarray] = None
        self.documents: Optional[List[Document]] = None

    def _compute_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        if self.embeddings is None:
            raise ValueError("O banco de dados vetorial não foi inicializado")
        norm = np.linalg.norm(query_embedding)
        return np.dot(
            self.embeddings,
            query_embedding if norm == 0 else query_embedding / norm,
        )

    def add_documents(self, documents: List[Document], save_path: str) -> None:
        texts = []
        for doc in documents:

            if self.embedding_column in doc.metadata:
                texts.append(doc.metadata[self.embedding_column])
            else:
                texts.append(doc.page_content)

        embeddings = self.embedding_function.embed_documents(texts)

        self.embeddings = np.array(embeddings)
        self.documents = documents

        Path(save_path).mkdir(parents=True, exist_ok=True)
        store_path = Path(save_path) / "vector_store.pkl"

        data = {
            "embeddings": self.embeddings,
            "docs_content": [doc.page_content for doc in documents],
            "docs_metadata": [doc.metadata for doc in documents],
            "embedding_column": self.embedding_column,
        }
        with open(store_path, "wb") as f:
            pickle.dump(data, f)

    def load(self, load_path: str) -> None:
        store_path = Path(load_path) / "vector_store.pkl"

        if not store_path.exists():
            raise FileNotFoundError(
                f"Arquivo do banco de dados não encontrado: {store_path}"
            )

        try:
            with open(store_path, "rb") as f:
                data = pickle.load(f)
            self.embeddings = data["embeddings"]
            self.embedding_column = data.get("embedding_column", "keywords")
            self.documents = [
                Document(page_content=content, metadata=metadata)
                for content, metadata in zip(
                    data["docs_content"], data["docs_metadata"]
                )
            ]
        except Exception as e:
            raise IOError(
                f"Erro ao carregar o banco de dados vetorial: {str(e)}"
            )

    def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        if self.embeddings is None or self.documents is None:
            raise ValueError("O banco de dados vetorial não foi inicializado")

        query_embedding = np.array(self.embedding_function.embed_query(query))
        similarities = self._compute_similarity(query_embedding)
        top_k_idx = np.argsort(similarities)[-k:][::-1]

        results = list()
        for idx in top_k_idx:
            results.append((self.documents[idx], float(similarities[idx])))

        return results


def load_asks(asks_path: str = ASKS_PATH) -> Dict[int, Document]:
    processed_asks: Dict[int, Document] = dict()
    asks_df = pd.read_csv(asks_path)
    for index, row in asks_df.iterrows():
        ask = Document(
            page_content=row["Pergunta"],
            metadata={
                "table": row["Tabela"],
                "output": row["JSON"],
            },
        )
        processed_asks[int(str(index))] = ask
    return processed_asks


def get_or_create_vector_db(
    db_path: str = ASKS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
) -> VectorDB:
    vector_db = VectorDB(embedding_model)

    try:
        vector_db.load(db_path)
    except (FileNotFoundError, Exception):
        asks = load_asks()
        vector_db.add_documents(list(asks.values()), db_path)

    return vector_db


def get_relevant_sample_asks(
    prompt: str,
    k: int = 3,
    db_path: Optional[str] = None,
) -> Tuple[List[Dict[str, str]], List[float]]:
    if db_path is None:
        db_path = ASKS_DB_PATH

    vector_db = get_or_create_vector_db(db_path)
    docs = vector_db.similarity_search_with_score(prompt, k=k)

    samples = [
        {
            "ask": doc[0].page_content,
            "table": doc[0].metadata["table"],
            "output": doc[0].metadata["output"],
        }
        for doc in docs
    ]
    scores = [float(doc[1]) for doc in docs]

    return samples, scores


def load_docs_documents() -> List[Document]:
    docs_map = utils.DOCS_KEYWORDS_MAP
    documents = []
    for key, value in docs_map.items():

        markdown_link = value.get("markdown_link", "")
        if not markdown_link:
            continue

        markdown_content = utils.get_content_from_url(markdown_link)

        keywords = value.get("keywords", [])
        description = value.get("description", f"Documentação sobre {key}")
        category = value.get("category", "other")
        link = value.get("url_link", "")

        structured_content = f"""Descrição: {description}
Palavras-chave: {", ".join(keywords)}

Conteúdo do documento:
{markdown_content}"""

        doc = Document(
            page_content=structured_content,
            metadata={
                "key": key,
                "category": category,
                "description": description,
                "link": link,
                "keywords": ", ".join(keywords),
                "raw_content": markdown_content,
            },
        )
        documents.append(doc)
    return documents


def get_or_create_docs_vector_db(
    db_path: str = DOCS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
) -> VectorDB:
    vector_db = VectorDB(embedding_model)

    try:
        vector_db.load(db_path)
    except (FileNotFoundError, Exception):
        documents = load_docs_documents()
        vector_db.add_documents(documents, db_path)

    return vector_db


def get_relevant_docs(
    prompt: str,
    k: int = 3,
    db_path: Optional[str] = None,
) -> Tuple[List[Dict[str, str]], List[float]]:
    if db_path is None:
        db_path = DOCS_DB_PATH

    vector_db = get_or_create_docs_vector_db(db_path)
    docs = vector_db.similarity_search_with_score(prompt, k=k)

    samples = [
        {
            "key": doc[0].metadata.get("key", "unknown"),
            "category": doc[0].metadata.get("category", "unknown"),
            "description": doc[0].metadata.get("description", "Sem descrição"),
            "link": doc[0].metadata.get("link", ""),
            "keywords": doc[0].metadata.get("keywords", ""),
            "content": doc[0].page_content,
            "raw_content": doc[0].metadata.get(
                "raw_content", doc[0].page_content
            ),
        }
        for doc in docs
    ]
    scores = [float(doc[1]) for doc in docs]

    return samples, scores


def load_docs_blocks() -> List[Document]:
    blocks_map = utils.DOCS_BLOCKS_MAP
    docs_map = utils.DOCS_KEYWORDS_MAP
    documents = list()

    for block_key, doc_keys in blocks_map.items():

        structured_content = f"Bloco: {block_key}\n\n"
        all_keywords = list()
        all_links = list()
        all_descriptions = list()
        combined_raw_content = ""

        for doc_key in doc_keys:
            if doc_key in docs_map:
                doc_info = docs_map[doc_key]

                markdown_link = doc_info.get("markdown_link", "")
                if not markdown_link:
                    continue

                content = utils.get_content_from_url(markdown_link)
                keywords = doc_info.get("keywords", [])
                description = doc_info.get(
                    "description", f"Documentação sobre {doc_key}"
                )
                link = doc_info.get("url_link", "")

                structured_content += f"""Documento: {description}
Palavras-chave: {", ".join(keywords)}

Conteúdo:
{content}

---

"""

                all_keywords.extend(keywords)
                all_links.append(link)
                all_descriptions.append(description)
                combined_raw_content += f"\n\n# {description}\n\n{content}"

        doc = Document(
            page_content=structured_content.strip(),
            metadata={
                "block_key": block_key,
                "doc_keys": doc_keys,
                "links": all_links,
                "descriptions": all_descriptions,
                "keywords": ", ".join(set(all_keywords)),
                "raw_content": combined_raw_content.strip(),
            },
        )
        documents.append(doc)

    return documents


def get_or_create_blocks_vector_db(
    db_path: str = BLOCKS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
) -> VectorDB:
    vector_db = VectorDB(embedding_model)

    try:
        vector_db.load(db_path)
    except (FileNotFoundError, Exception):
        documents = load_docs_blocks()
        vector_db.add_documents(documents, db_path)

    return vector_db


def get_relevant_blocks(
    prompt: str,
    k: int = 3,
    threshold: float = 0.3,
    db_path: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[float]]:
    if db_path is None:
        db_path = BLOCKS_DB_PATH

    vector_db = get_or_create_blocks_vector_db(db_path)
    docs_with_scores = vector_db.similarity_search_with_score(
        prompt, k=len(vector_db.documents) if vector_db.documents else k
    )

    best_score = docs_with_scores[0][1] if docs_with_scores else 0

    if best_score < threshold:
        intro_blocks = ["project_intro_block", "getting_started_block"]
        filtered_docs = [
            doc
            for doc in docs_with_scores
            if doc[0].metadata["block_key"] in intro_blocks
        ]
        if filtered_docs:
            docs_with_scores = filtered_docs[:1] + docs_with_scores[: k - 1]

    docs_with_scores = docs_with_scores[:k]

    samples = []
    scores = []

    for doc, score in docs_with_scores:
        samples.append(
            {
                "block_key": doc.metadata["block_key"],
                "doc_keys": doc.metadata["doc_keys"],
                "links": doc.metadata["links"],
                "descriptions": doc.metadata["descriptions"],
                "keywords": (
                    doc.metadata["keywords"][:200] + "..."
                    if len(doc.metadata["keywords"]) > 200
                    else doc.metadata["keywords"]
                ),
                "content": (
                    doc.page_content[:1000] + "..."
                    if len(doc.page_content) > 1000
                    else doc.page_content
                ),
                "raw_content": (
                    doc.metadata.get("raw_content", "")[:1000] + "..."
                    if len(doc.metadata.get("raw_content", "")) > 1000
                    else doc.metadata.get("raw_content", "")
                ),
            }
        )
        scores.append(float(score))

    return samples, scores
```

## web_cache.py
<sub>caminho: `mosqlimate_assistant/web_cache.py`</sub>

```python
import requests_cache

shared_cache_session = requests_cache.CachedSession(
    'mosqlimate_docs_cache',
    backend='sqlite',
    expire_after=60 * 60 * 24 * 3,  # 3 dias
)
```
