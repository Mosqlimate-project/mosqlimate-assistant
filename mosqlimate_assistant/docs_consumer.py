import requests

from mosqlimate_assistant.settings import (
    MOSQLIMATE_API_DOCS_JSON,
    MOSQLIMATE_DATA_PLATFORM_DOCS,
    MOSQLIMATE_DATASTORE_BASE_DOCS,
    MOSQLIMATE_DATASTORE_GET_AUTHORS_DOCS,
    MOSQLIMATE_DATASTORE_GET_CLIMATE_DOCS,
    MOSQLIMATE_DATASTORE_GET_CLIMATE_WEEKLY_DOCS,
    MOSQLIMATE_DATASTORE_GET_EPISCANNER_DOCS,
    MOSQLIMATE_DATASTORE_GET_INFODENGUE_DOCS,
    MOSQLIMATE_DATASTORE_GET_MODELS_DOCS,
    MOSQLIMATE_DATASTORE_GET_MOSQUITO_DOCS,
    MOSQLIMATE_DATASTORE_GET_PREDICTIONS_DOCS,
    MOSQLIMATE_DATASTORE_POST_MODELS_DOCS,
    MOSQLIMATE_DATASTORE_POST_PREDICTIONS_DOCS,
    MOSQLIMATE_OVICOUNTER_DOCS,
    MOSQLIMATE_PROJECT_DOCS,
    MOSQLIMATE_REGISTRY_DOCS,
    MOSQLIMATE_UID_KEY_DOCS,
)


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


def get_markdown_content(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RuntimeError(f"Erro ao obter markdown de {url}: {e}")


def get_mosqlimate_project_docs() -> str:
    """Obtém a documentação principal do projeto Mosqlimate."""
    return get_markdown_content(MOSQLIMATE_PROJECT_DOCS)


def get_mosqlimate_ovicounter_docs() -> str:
    """Obtém a documentação do Ovicounter (dataset de ovos)."""
    return get_markdown_content(MOSQLIMATE_OVICOUNTER_DOCS)


def get_mosqlimate_data_platform_docs() -> str:
    """Obtém a documentação da plataforma de dados."""
    return get_markdown_content(MOSQLIMATE_DATA_PLATFORM_DOCS)


def get_mosqlimate_datastore_base_docs() -> str:
    """Obtém a documentação base do datastore."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_BASE_DOCS)


def get_mosqlimate_registry_docs() -> str:
    """Obtém a documentação do registry."""
    return get_markdown_content(MOSQLIMATE_REGISTRY_DOCS)


def get_mosqlimate_uid_key_docs() -> str:
    """Obtém a documentação sobre UID keys."""
    return get_markdown_content(MOSQLIMATE_UID_KEY_DOCS)


# Funções para endpoints GET do datastore


def get_mosqlimate_infodengue_docs() -> str:
    """Obtém a documentação do endpoint GET infodengue."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_INFODENGUE_DOCS)


def get_mosqlimate_episcanner_docs() -> str:
    """Obtém a documentação do endpoint GET episcanner."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_EPISCANNER_DOCS)


def get_mosqlimate_climate_docs() -> str:
    """Obtém a documentação do endpoint GET climate."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_CLIMATE_DOCS)


def get_mosqlimate_climate_weekly_docs() -> str:
    """Obtém a documentação do endpoint GET climate weekly."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_CLIMATE_WEEKLY_DOCS)


def get_mosqlimate_mosquito_docs() -> str:
    """Obtém a documentação do endpoint GET mosquito."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_MOSQUITO_DOCS)


# Funções para endpoints GET do registry


def get_mosqlimate_predictions_docs() -> str:
    """Obtém a documentação do endpoint GET predictions."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_PREDICTIONS_DOCS)


def get_mosqlimate_models_docs() -> str:
    """Obtém a documentação do endpoint GET models."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_MODELS_DOCS)


def get_mosqlimate_authors_docs() -> str:
    """Obtém a documentação do endpoint GET authors."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_GET_AUTHORS_DOCS)


# Funções para endpoints POST do registry


def get_mosqlimate_post_predictions_docs() -> str:
    """Obtém a documentação do endpoint POST predictions."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_POST_PREDICTIONS_DOCS)


def get_mosqlimate_post_models_docs() -> str:
    """Obtém a documentação do endpoint POST models."""
    return get_markdown_content(MOSQLIMATE_DATASTORE_POST_MODELS_DOCS)


# Funções para obter múltiplas documentações


def get_all_mosqlimate_docs() -> dict:
    """
    Obtém toda a documentação em markdown do Mosqlimate.
    """
    docs = {
        "project": {
            "main": get_mosqlimate_project_docs(),
            "ovicounter": get_mosqlimate_ovicounter_docs(),
            "data_platform": get_mosqlimate_data_platform_docs(),
            "uid_key": get_mosqlimate_uid_key_docs(),
        },
        "datastore": {
            "base": get_mosqlimate_datastore_base_docs(),
            "get": {
                "infodengue": get_mosqlimate_infodengue_docs(),
                "episcanner": get_mosqlimate_episcanner_docs(),
                "climate": get_mosqlimate_climate_docs(),
                "climate_weekly": get_mosqlimate_climate_weekly_docs(),
                "mosquito": get_mosqlimate_mosquito_docs(),
            },
        },
        "registry": {
            "base": get_mosqlimate_registry_docs(),
            "get": {
                "predictions": get_mosqlimate_predictions_docs(),
                "models": get_mosqlimate_models_docs(),
                "authors": get_mosqlimate_authors_docs(),
            },
            "post": {
                "predictions": get_mosqlimate_post_predictions_docs(),
                "models": get_mosqlimate_post_models_docs(),
            },
        },
    }

    return docs


def get_datastore_docs() -> dict:
    """
    Obtém apenas a documentação relacionada ao datastore.
    """
    docs = {
        "base": get_mosqlimate_datastore_base_docs(),
        "endpoints": {
            "infodengue": get_mosqlimate_infodengue_docs(),
            "episcanner": get_mosqlimate_episcanner_docs(),
            "climate": get_mosqlimate_climate_docs(),
            "climate_weekly": get_mosqlimate_climate_weekly_docs(),
            "mosquito": get_mosqlimate_mosquito_docs(),
        },
    }

    return docs


def get_registry_docs() -> dict:
    """
    Obtém apenas a documentação relacionada ao registry.
    """
    docs = {
        "base": get_mosqlimate_registry_docs(),
        "get_endpoints": {
            "predictions": get_mosqlimate_predictions_docs(),
            "models": get_mosqlimate_models_docs(),
            "authors": get_mosqlimate_authors_docs(),
        },
        "post_endpoints": {
            "predictions": get_mosqlimate_post_predictions_docs(),
            "models": get_mosqlimate_post_models_docs(),
        },
    }

    return docs
