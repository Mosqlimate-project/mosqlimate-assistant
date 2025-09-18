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
