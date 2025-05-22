import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Mosqlimate API URLs
MOSQLIMATE_API_DOCS = "https://api.mosqlimate.org/api/openapi.json"
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
DEFAULT_DATABASE_PATH = "../data"
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


# Paths
MUNICIPALITIES_PATH = os.path.join(
    CURRENT_PATH, DATABASE_PATH, "municipios.json"
)
ASKS_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks.csv")
ASKS_DB_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks_db")


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
