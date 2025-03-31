import os
from dotenv import load_dotenv

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(CURRENT_PATH, ".env")
load_dotenv(DOTENV_PATH)

DEFAULT_API_KEY = "sk-"
DEFAULT_DATABASE_PATH = "../data"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"

def ensure_env_variable(key: str, default_value: str) -> None:
    if not os.getenv(key):
        print(f"Environment variable {key} not found. Setting to default value: {default_value}")
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

API_KEY = os.getenv("API_KEY", DEFAULT_API_KEY)
DATABASE_PATH = os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
