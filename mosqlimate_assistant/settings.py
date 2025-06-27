import os
import urllib.request
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Mosqlimate API URLs
MOSQLIMATE_API_DOCS_JSON = "https://api.mosqlimate.org/api/openapi.json"

MOSQLIMATE_PROJECT_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Mosqlimate-project.github.io/refs/heads/main/pages/index.md"

MOSQLIMATE_OVICOUNTER_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Mosqlimate-project.github.io/refs/heads/main/pages/egg-dataset.md"

MOSQLIMATE_DATA_PLATFORM_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/index.pt.md"
MOSQLIMATE_DATASTORE_BASE_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/index.pt.md"

MOSQLIMATE_DATASTORE_GET_INFODENGUE_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/infodengue.pt.md"
MOSQLIMATE_DATASTORE_GET_EPISCANNER_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/episcanner.pt.md"
MOSQLIMATE_DATASTORE_GET_CLIMATE_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/climate.pt.md"
MOSQLIMATE_DATASTORE_GET_CLIMATE_WEEKLY_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/climate-weekly.pt.md"
MOSQLIMATE_DATASTORE_GET_MOSQUITO_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/mosquito.pt.md"

MOSQLIMATE_REGISTRY_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/index.pt.md"

MOSQLIMATE_DATASTORE_GET_PREDICTIONS_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/GET/predictions.pt.md"
MOSQLIMATE_DATASTORE_GET_MODELS_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/GET/models.pt.md"
MOSQLIMATE_DATASTORE_GET_AUTHORS_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/GET/authors.pt.md"

MOSQLIMATE_DATASTORE_POST_PREDICTIONS_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/POST/predictions.pt.md"
MOSQLIMATE_DATASTORE_POST_MODELS_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/POST/models.pt.md"

MOSQLIMATE_UID_KEY_DOCS = "https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/uid-key.pt.md"


BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"


# Models
OLLAMA_MODEL = "llama3.2:latest"

DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com"

GEMINI_MODEL = "gemini-2.0-flash"
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
ASKS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks_db")
DOCS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "docs_db")

MUNICIPALITIES_URL = "https://raw.githubusercontent.com/Mosqlimate-project/mosqlimate-assistant/refs/heads/main/mosqlimate_assistant/data/municipios.json"
ASKS_URL = "https://raw.githubusercontent.com/Mosqlimate-project/mosqlimate-assistant/refs/heads/main/mosqlimate_assistant/data/asks.csv"


def ensure_file_exists(local_path: str, remote_url: str):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not os.path.exists(local_path):
        try:
            urllib.request.urlretrieve(remote_url, local_path)
        except Exception as e:
            print(f"Erro ao baixar {local_path}: {e}")


ensure_file_exists(MUNICIPALITIES_PATH, MUNICIPALITIES_URL)
ensure_file_exists(ASKS_PATH, ASKS_URL)

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
