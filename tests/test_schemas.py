import epiweeks
import pytest
from pydantic import ValidationError

from mosqlimate_assistant import schemas


def test_table_filters_valid():
    filters = schemas.TableFilters(
        table="infodengue",
        disease="dengue",
        start="2023-01-01",
        end="2023-12-31",
        uf="SP",
        city="Sao Paulo",
        key="test_key",
        year=2023,
    )
    assert filters.table == "infodengue"
    assert filters.disease == "dengue"
    assert filters.start == "2023-01-01"
    assert filters.end == "2023-12-31"
    assert filters.uf == "SP"
    assert filters.city == "Sao Paulo"
    assert filters.key == "test_key"
    assert filters.year == 2023

    filters_minimal = schemas.TableFilters(table="climate")
    last_week = epiweeks.Week.thisweek() - 1
    assert filters_minimal.table == "climate"
    assert filters_minimal.disease is None
    assert filters_minimal.start == last_week.startdate().isoformat()
    assert filters_minimal.end == last_week.enddate().isoformat()
    assert filters_minimal.uf is None


def test_table_filters_invalid():
    with pytest.raises(ValidationError):
        schemas.TableFilters(table="invalid_table")

    with pytest.raises(ValidationError):
        schemas.TableFilters(table="infodengue", disease="malaria")

    with pytest.raises(ValidationError):
        schemas.TableFilters(table="infodengue", uf="XYZ")


def test_table_filters_invalid_dates_default_to_epiweek():
    last_week = epiweeks.Week.thisweek() - 1
    filters = schemas.TableFilters(table="climate", start="bad", end="bad")
    assert filters.start == last_week.startdate().isoformat()
    assert filters.end == last_week.enddate().isoformat()


def test_table_filters_extra_fields_ignored():
    filters = schemas.TableFilters(
        table="mosquito", extra_field="should_be_ignored"
    )
    assert filters.table == "mosquito"
    assert not hasattr(filters, "extra_field")


def test_infodengue_filters_valid():
    filters = schemas.InfodengueFilters(
        disease="zika",
        start="2022-01-01",
        end="2022-12-31",
        uf="RJ",
        city="Rio de Janeiro",
    )
    assert filters.table == "infodengue"
    assert filters.disease == "zika"
    assert filters.start == "2022-01-01"
    assert filters.end == "2022-12-31"
    assert filters.uf == "RJ"
    assert filters.city == "Rio de Janeiro"


def test_infodengue_filters_missing_required_fields():
    with pytest.raises(ValidationError):
        schemas.InfodengueFilters(start="2022-01-01", end="2022-12-31")
    with pytest.raises(ValidationError):
        schemas.InfodengueFilters(disease="dengue", end="2022-12-31")
    with pytest.raises(ValidationError):
        schemas.InfodengueFilters(disease="dengue", start="2022-01-01")


def test_infodengue_filters_invalid_disease():
    with pytest.raises(ValidationError):
        schemas.InfodengueFilters(
            disease="malaria", start="2022-01-01", end="2022-12-31"
        )


def test_climate_filters_valid():
    filters = schemas.ClimateFilters(
        start="2023-03-01", end="2023-03-31", uf="MG", city="Belo Horizonte"
    )
    assert filters.table == "climate"
    assert filters.start == "2023-03-01"
    assert filters.end == "2023-03-31"
    assert filters.uf == "MG"
    assert filters.city == "Belo Horizonte"


def test_climate_filters_missing_required_fields():
    with pytest.raises(ValidationError):
        schemas.ClimateFilters(end="2023-03-31")
    with pytest.raises(ValidationError):
        schemas.ClimateFilters(start="2023-03-01")


def test_mosquito_filters_valid():
    filters = schemas.MosquitoFilters(key="my_api_key")
    assert filters.table == "mosquito"
    assert filters.key == "my_api_key"


def test_mosquito_filters_missing_required_fields():
    with pytest.raises(ValidationError):
        schemas.MosquitoFilters()


def test_episcanner_filters_valid():
    filters = schemas.EpiscannerFilters(
        disease="chikungunya", uf="BA", year=2024
    )
    assert filters.table == "episcanner"
    assert filters.disease == "chikungunya"
    assert filters.uf == "BA"
    assert filters.year == 2024

    filters_no_year = schemas.EpiscannerFilters(disease="dengue", uf="CE")
    assert filters_no_year.table == "episcanner"
    assert filters_no_year.disease == "dengue"
    assert filters_no_year.uf == "CE"
    assert filters_no_year.year is None


def test_episcanner_filters_invalid():
    with pytest.raises(ValidationError):
        schemas.EpiscannerFilters(uf="SP")

    with pytest.raises(ValidationError):
        schemas.EpiscannerFilters(disease="zika")

    with pytest.raises(ValidationError):
        schemas.EpiscannerFilters(disease="yellow_fever", uf="AM")

    with pytest.raises(ValidationError):
        schemas.EpiscannerFilters(disease="dengue", uf="XX")
