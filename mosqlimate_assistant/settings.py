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
