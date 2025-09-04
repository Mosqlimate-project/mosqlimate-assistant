from typing import List

import requests

from mosqlimate_assistant.settings import MOSQLIMATE_API_DOCS_JSON


def get_mosqlimate_api_docs() -> dict:
    url = MOSQLIMATE_API_DOCS_JSON
    response = requests.get(url)
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
    response = requests.get(url)
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
