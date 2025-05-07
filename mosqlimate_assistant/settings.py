import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(CURRENT_PATH, "../.env")

DEFAULT_API_KEY = "sk-"
DEFAULT_DATABASE_PATH = "../data"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"

MOSQLIMATE_API_DOCS = "https://api.mosqlimate.org/api/openapi.json"
DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

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

DATABASE_PATH = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
MUNICIPALITIES_PATH = os.path.join(
    CURRENT_PATH, DATABASE_PATH, "municipios.json"
)
ASKS_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks.csv")
ASKS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks_db")


class Settings(BaseSettings):
    api_key: str = DEFAULT_API_KEY
    database_path: str = DEFAULT_DATABASE_PATH
    embedding_model: str = DEFAULT_EMBEDDING_MODEL

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
    )


settings = Settings()

API_KEY = settings.api_key
BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"
EMBEDDING_MODEL = settings.embedding_model
