import os
from typing import Literal

from dotenv import load_dotenv

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(CURRENT_PATH, "../.env")
load_dotenv(DOTENV_PATH)

DEFAULT_API_KEY = "sk-"
DEFAULT_DATABASE_PATH = "../data"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"

MOSQLIMATE_API_DOCS = "https://api.mosqlimate.org/api/openapi.json"
DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Definições de tipos
Diseases = Literal[
    "dengue",
    "zika",
    "chik",
    "chikungunya",
]

# Lista de UFs válidas
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

# Tipo para UFs
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
MUNICIPALITIES_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "municipios.json")
ASKS_PATH = os.path.join(CURRENT_PATH, DATABASE_PATH, "asks.csv")


def ensure_env_variable(key: str, default_value: str) -> None:
    if not os.getenv(key):
        print(
            f"Environment variable {key} not found. Setting to default value: {default_value}"
        )
        with open(DOTENV_PATH, "a") as f:
            f.write(f"{key}={default_value}\n")
        os.environ[key] = default_value


ensure_env_variable("API_KEY", DEFAULT_API_KEY)
ensure_env_variable("DATABASE_PATH", DEFAULT_DATABASE_PATH)
ensure_env_variable("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def update_api_key(api_key: str) -> None:
    with open(DOTENV_PATH, "a") as f:
        f.write(f"API_KEY={api_key}\n")
    os.environ["API_KEY"] = api_key


def update_database_path(database_path: str) -> None:
    with open(DOTENV_PATH, "a") as f:
        f.write(f"DATABASE_PATH={database_path}\n")
    os.environ["DATABASE_PATH"] = database_path


def update_embedding_model(embedding_model: str) -> None:
    with open(DOTENV_PATH, "a") as f:
        f.write(f"EMBEDDING_MODEL={embedding_model}\n")
    os.environ["EMBEDDING_MODEL"] = embedding_model


API_KEY = os.getenv("API_KEY")
BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
