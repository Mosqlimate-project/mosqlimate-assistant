from mosqlimate_assistant import api_consumer, schemas
from mosqlimate_assistant.settings import (
    BASE_URL_API,
    MOSQLIMATE_API_DOCS_JSON,
)


class DummyResponse:
    def __init__(self, status_code, exc=None):
        self.status_code = status_code
        self._exc = exc

    def raise_for_status(self):
        if self._exc:
            raise self._exc


def test_generate_api_infodengue_url():
    filters = schemas.InfodengueFilters(
        disease="dengue", start="2020-01-01", end="2020-12-31"
    )
    url = api_consumer.generate_api_infodengue_url(filters)
    assert (
        url
        == f"{BASE_URL_API}infodengue?page=1&per_page=100&disease=dengue&start=2020-01-01&end=2020-12-31"
    )

    filters_2 = schemas.InfodengueFilters(
        disease="zika",
        start="2021-01-01",
        end="2021-12-31",
        uf="SP",
        city="Sao Paulo",
    )
    url_2 = api_consumer.generate_api_infodengue_url(filters_2)
    assert "uf=SP" in url_2
    assert "geocode=3550308" in url_2


def test_generate_api_climate_url():
    filters = schemas.ClimateFilters(start="2022-02-01", end="2022-02-28")
    url = api_consumer.generate_api_climate_url(filters)
    assert (
        url
        == f"{BASE_URL_API}climate?page=1&per_page=100&start=2022-02-01&end=2022-02-28"
    )

    filters_2 = schemas.ClimateFilters(
        start="2022-03-01", end="2022-03-31", uf="MG", city="Belo Horizonte"
    )
    url_2 = api_consumer.generate_api_climate_url(filters_2)
    assert "uf=MG" in url_2
    assert "geocode=3106200" in url_2


def test_generate_api_mosquito_url():
    filters = schemas.MosquitoFilters(key="abc123")
    url = api_consumer.generate_api_mosquito_url(filters)
    assert url == f"{BASE_URL_API}mosquito?page=1&key=abc123"


def test_generate_api_episcanner_url():
    filters = schemas.EpiscannerFilters(disease="chikungunya", uf="RJ")
    url = api_consumer.generate_api_episcanner_url(filters)
    assert url == f"{BASE_URL_API}episcanner?disease=chikungunya&uf=RJ"

    filters = schemas.EpiscannerFilters(disease="dengue", uf="SP", year=2020)
    url = api_consumer.generate_api_episcanner_url(filters)
    assert "year=2020" in url


def test_generate_api_url_dispatch_specific():
    inf = schemas.InfodengueFilters(
        disease="dengue", start="2020-01-01", end="2020-12-31"
    )
    assert api_consumer.generate_api_url(
        inf
    ) == api_consumer.generate_api_infodengue_url(inf)
    cli = schemas.ClimateFilters(start="2020-05-01", end="2020-05-31")
    assert api_consumer.generate_api_url(
        cli
    ) == api_consumer.generate_api_climate_url(cli)
    mos = schemas.MosquitoFilters(key="k")
    assert api_consumer.generate_api_url(
        mos
    ) == api_consumer.generate_api_mosquito_url(mos)
    epi = schemas.EpiscannerFilters(disease="zika", uf="BA")
    assert api_consumer.generate_api_url(
        epi
    ) == api_consumer.generate_api_episcanner_url(epi)


def test_check_api_response_success():
    assert api_consumer.check_api_response(MOSQLIMATE_API_DOCS_JSON) == 200
