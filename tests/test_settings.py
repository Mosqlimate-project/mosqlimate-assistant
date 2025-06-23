import os
from typing import get_args

from mosqlimate_assistant import settings


def test_current_path():
    expected_path_suffix = "mosqlimate_assistant"

    assert settings.CURRENT_PATH.endswith(expected_path_suffix)
    assert os.path.isdir(settings.CURRENT_PATH)


def test_dotenv_path():
    expected_path = os.path.join(settings.CURRENT_PATH, "../.env")
    assert settings.DOTENV_PATH == expected_path


def test_default_api_key():
    assert settings.DEFAULT_API_KEY == "sk-"


def test_default_database_path():
    assert settings.DEFAULT_DATABASE_PATH == "../data"


def test_default_embedding_model():
    assert settings.DEFAULT_EMBEDDING_MODEL == "mxbai-embed-large:latest"


def test_mosqlimate_api_docs():
    assert (
        settings.MOSQLIMATE_API_DOCS_JSON
        == "https://api.mosqlimate.org/api/openapi.json"
    )


def test_deepseek_api_url():
    assert settings.DEEPSEEK_API_URL == "https://api.deepseek.com"


def test_deepseek_model():
    assert settings.DEEPSEEK_MODEL == "deepseek-chat"


def test_valid_ufs_list():
    expected_ufs = [
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
    assert settings.VALID_UFS == expected_ufs


def test_ufs_literal_type():
    ufs_args = get_args(settings.UFs)
    assert sorted(list(ufs_args)) == sorted(settings.VALID_UFS)


def test_diseases_literal_type():
    diseases_args = get_args(settings.Diseases)
    expected_diseases = ["dengue", "zika", "chikungunya"]
    assert sorted(list(diseases_args)) == sorted(expected_diseases)


def test_derived_paths():
    db_path_val = os.getenv("DATABASE_PATH", settings.DEFAULT_DATABASE_PATH)

    expected_municipalities_path = os.path.join(
        settings.CURRENT_PATH, db_path_val, "municipios.json"
    )

    assert os.path.normpath(settings.MUNICIPALITIES_PATH) == os.path.normpath(
        expected_municipalities_path
    )

    expected_asks_path = os.path.join(
        settings.CURRENT_PATH, db_path_val, "asks.csv"
    )
    assert os.path.normpath(settings.ASKS_PATH) == os.path.normpath(
        expected_asks_path
    )

    expected_asks_db_path = os.path.join(
        settings.CURRENT_PATH, db_path_val, "asks_db"
    )
    assert os.path.normpath(settings.ASKS_DB_PATH) == os.path.normpath(
        expected_asks_db_path
    )


def test_base_url_api():
    assert settings.BASE_URL_API == "https://api.mosqlimate.org/api/datastore/"
