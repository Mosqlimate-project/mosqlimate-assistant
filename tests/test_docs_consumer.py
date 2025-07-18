from mosqlimate_assistant import docs_consumer as dc
from mosqlimate_assistant.docs_consumer import (
    get_mosqlimate_authors_docs,
    get_mosqlimate_climate_docs,
    get_mosqlimate_climate_weekly_docs,
    get_mosqlimate_data_platform_docs,
    get_mosqlimate_datastore_base_docs,
    get_mosqlimate_episcanner_docs,
    get_mosqlimate_infodengue_docs,
    get_mosqlimate_models_docs,
    get_mosqlimate_mosquito_docs,
    get_mosqlimate_ovicounter_docs,
    get_mosqlimate_post_models_docs,
    get_mosqlimate_post_predictions_docs,
    get_mosqlimate_predictions_docs,
    get_mosqlimate_project_docs,
    get_mosqlimate_registry_docs,
    get_mosqlimate_uid_key_docs,
)


def test_get_mosqlimate_api():
    dc.get_mosqlimate_api_docs()
    assert isinstance(dc.get_mosqlimate_api_docs(), dict)


def test_get_mosqlimate_api_paths():
    DATASTORE_PATHS = [
        "/api/datastore/infodengue/",
        "/api/datastore/climate/",
        "/api/datastore/climate/weekly/",
        "/api/datastore/mosquito/",
        "/api/datastore/episcanner/",
    ]
    api_paths = dc.get_mosqlimate_api_paths()

    for path in DATASTORE_PATHS:
        assert path in api_paths


def test_format_api_parameters():
    api_json = {
        "parameters": [
            {"name": "page", "schema": {"type": "integer"}},
            {
                "name": "foo",
                "required": True,
                "schema": {
                    "type": "string",
                    "enum": ["a", "chik", "b"],
                    "default": "c",
                    "format": "date",
                },
            },
            {
                "name": "bar",
                "required": False,
                "schema": {
                    "anyOf": [
                        {"type": "null"},
                        {"type": "integer", "default": 5},
                    ]
                },
            },
        ]
    }
    formatted = dc.format_api_parameters(api_json)
    params = formatted.get("parameters", [])

    names = [p["name"] for p in params]
    assert "page" not in names
    assert "foo" in names and "bar" in names

    foo = next(p for p in params if p["name"] == "foo")
    assert foo["type"] == "string"
    assert foo["required"] is True
    assert foo["enum"] == ["a", "b"]
    assert foo["default"] == "c"
    assert foo["format"] == "date"
    assert "nullable" not in foo

    bar = next(p for p in params if p["name"] == "bar")
    assert bar["type"] == "integer"
    assert bar["required"] is False
    assert bar.get("default") == 5
    assert bar.get("nullable") is True


def test_docs_markdowns():
    docs_markdowns_list = [
        get_mosqlimate_project_docs,
        get_mosqlimate_ovicounter_docs,
        get_mosqlimate_data_platform_docs,
        get_mosqlimate_datastore_base_docs,
        get_mosqlimate_registry_docs,
        get_mosqlimate_uid_key_docs,
        get_mosqlimate_infodengue_docs,
        get_mosqlimate_episcanner_docs,
        get_mosqlimate_climate_docs,
        get_mosqlimate_climate_weekly_docs,
        get_mosqlimate_mosquito_docs,
        get_mosqlimate_predictions_docs,
        get_mosqlimate_models_docs,
        get_mosqlimate_authors_docs,
        get_mosqlimate_post_predictions_docs,
        get_mosqlimate_post_models_docs,
    ]

    for doc_func in docs_markdowns_list:
        markdown = doc_func()
        assert isinstance(markdown, str)
        assert len(markdown) > 0
