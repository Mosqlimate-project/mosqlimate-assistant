from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from mosqlimate_assistant.knowledge_base import build_default_blocks

EXPECTED_CSV_COLUMNS = (
    "name",
    "markdown_link",
    "url_link",
    "keywords",
    "group",
)

EXPECTED_BLOCK_KEYS = {
    "platform_overview",
    "platform_epi_data",
    "platform_env_data",
    "platform_registry_models",
    "platform_registry_predictions",
    "platform_visualize",
    "mosqlient_getting_started",
    "mosqlient_datastore",
    "mosqlient_registry",
    "mosqlient_scoring_tutorial",
    "mosqlient_score_reference",
    "mosqlient_forecast_baseline",
    "mosqlient_ensemble",
    "mosqlient_prediction_optimize",
    "imdc_overview",
    "imdc_data",
}

EXPECTED_BLOCK_MEMBERS = {
    "platform_overview": {
        "project_main",
        "project_ovicounter",
        "project_products",
        "project_team",
        "data_platform",
        "uid_key",
    },
    "platform_epi_data": {
        "data_platform",
        "datastore_base",
        "datastore_infodengue",
        "datastore_episcanner",
    },
    "platform_env_data": {
        "data_platform",
        "datastore_climate",
        "datastore_climate_weekly",
        "datastore_mosquito",
        "project_ovicounter",
    },
    "platform_registry_models": {
        "registry_base",
        "registry_models_get",
        "registry_models_post",
        "registry_predictions_get",
    },
    "platform_registry_predictions": {
        "registry_base",
        "registry_models_get",
        "registry_predictions_get",
        "registry_predictions_post",
    },
    "mosqlient_datastore": {
        "Overview",
        "Tutorial - Datastore",
        "Reference - Infodengue data",
        "Reference - Climate data",
        "Reference - CLI",
    },
    "mosqlient_registry": {
        "Overview",
        "Tutorial - Registry",
        "Reference - Get, post and delete models",
        "Reference - Get, post and delete predictions",
        "Reference - CLI",
    },
    "mosqlient_scoring_tutorial": {
        "Tutorial - Model Scoring",
        "Tutorial - Simple forecast model",
    },
    "mosqlient_score_reference": {
        "Tutorial - Model Scoring",
        "Reference - Score",
    },
    "mosqlient_forecast_baseline": {
        "Tutorial - Simple forecast model",
        "Reference - Baseline Arima",
        "Reference - Prediction optimize",
    },
    "mosqlient_ensemble": {
        "Tutorial - Model Scoring",
        "Tutorial - Ensemble predictions",
        "Reference - Ensemble",
        "Reference - Score",
    },
    "mosqlient_prediction_optimize": {
        "Reference - Baseline Arima",
        "Reference - Score",
        "Reference - Prediction optimize",
    },
}


def test_block_catalog_exposes_expected_groups() -> None:
    blocks = {block.key: block for block in build_default_blocks(lang="pt")}

    assert set(blocks) == EXPECTED_BLOCK_KEYS
    for key, expected_names in EXPECTED_BLOCK_MEMBERS.items():
        assert blocks[key].names == frozenset(expected_names)
    assert {
        "/content/organize/index.md",
        "/content/sprint/2025/index.md",
        "/content/instructions/2025/index.md",
        "/content/calendar/index.md",
        "/content/results/2025/index.md",
        "/content/publications/index.md",
    }.issubset(blocks["imdc_overview"].url_fragments)
    assert {
        "/content/data/2025/index.md",
        "/content/instructions/2025/index.md",
    }.issubset(blocks["imdc_data"].url_fragments)


def test_english_project_links_use_en_locale() -> None:
    csv_path = Path("mosqlimate_assistant/data/docs_en_references.csv")
    with csv_path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    indexed = {row["name"]: row for row in rows}

    assert indexed["project_main"]["url_link"] == "https://mosqlimate.org/en/"
    assert (
        indexed["project_ovicounter"]["url_link"]
        == "https://mosqlimate.org/en/egg-dataset/"
    )
    assert (
        indexed["project_products"]["url_link"]
        == "https://mosqlimate.org/en/products/"
    )
    assert (
        indexed["project_team"]["url_link"]
        == "https://mosqlimate.org/en/team/"
    )


def test_reference_csv_validator_passes_for_all_catalogs() -> None:
    for file_name in (
        "docs_references.csv",
        "docs_en_references.csv",
        "code_references.csv",
        "imdc_references.csv",
    ):
        csv_path = Path("mosqlimate_assistant/data") / file_name
        with csv_path.open("r", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        fieldnames = tuple(rows[0].keys()) if rows else ()
        duplicate_names = [
            key
            for key, count in Counter(row["name"] for row in rows).items()
            if count > 1
        ]
        empty_required_fields = {
            column: sum(not (row.get(column) or "").strip() for row in rows)
            for column in EXPECTED_CSV_COLUMNS
        }

        assert fieldnames == EXPECTED_CSV_COLUMNS
        assert duplicate_names == []
        assert all(count == 0 for count in empty_required_fields.values())


def test_reference_csv_groups_follow_standardized_names() -> None:
    expected_groups = {
        "docs_references.csv": {
            "project_team",
            "project_resources",
            "platform_auth",
            "datastores",
            "registry",
            "dashboard",
        },
        "docs_en_references.csv": {
            "project_team",
            "project_resources",
            "platform_auth",
            "datastores",
            "registry",
            "dashboard",
        },
        "code_references.csv": {
            "overview",
            "datastore",
            "registry",
            "advanced",
            "forecasting",
        },
        "imdc_references.csv": {
            "overview",
            "data",
            "instructions",
            "results",
        },
    }

    for file_name, expected in expected_groups.items():
        csv_path = Path("mosqlimate_assistant/data") / file_name
        with csv_path.open("r", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        group_counts = Counter(
            (row.get("group") or "").strip() for row in rows
        )
        assert set(group_counts) == expected
