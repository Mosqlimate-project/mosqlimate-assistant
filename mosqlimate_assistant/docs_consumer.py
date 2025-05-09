import requests

from mosqlimate_assistant.settings import MOSQLIMATE_API_DOCS


def get_mosqlimate_api_docs() -> dict:
    url = MOSQLIMATE_API_DOCS
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
