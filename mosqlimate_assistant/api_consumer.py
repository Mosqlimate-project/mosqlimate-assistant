import requests
from typing import Union

from mosqlimate_assistant import schemas
from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.settings import BASE_URL_API


def generate_api_infodengue_url(filters: schemas.InfodengueFilters) -> str:
    url = f"{BASE_URL_API}infodengue?page=1&per_page=100&disease={filters.disease}&start={filters.start}&end={filters.end}"
    if filters.uf:
        url += f"&uf={filters.uf}"
    if filters.city:
        geocode = get_municipality_code(filters.city, filters.uf)
        url += f"&geocode={geocode}"
    return url


def generate_api_climate_url(filters: schemas.ClimateFilters) -> str:
    url = f"{BASE_URL_API}climate?page=1&per_page=100&start={filters.start}&end={filters.end}"
    if filters.uf:
        url += f"&uf={filters.uf}"
    if filters.city:
        geocode = get_municipality_code(filters.city, filters.uf)
        url += f"&geocode={geocode}"
    return url


def generate_api_mosquito_url(filters: schemas.MosquitoFilters) -> str:
    return f"{BASE_URL_API}mosquito?page=1&key={filters.key}"


def generate_api_episcanner_url(filters: schemas.EpiscannerFilters) -> str:
    url = f"{BASE_URL_API}episcanner?disease={filters.disease}&uf={filters.uf}"
    if filters.year:
        url += f"&year={filters.year}"
    return url


def generate_api_url(
    filters_obj: Union[
        schemas.InfodengueFilters,
        schemas.ClimateFilters,
        schemas.MosquitoFilters,
        schemas.EpiscannerFilters,
        schemas.TableFilters,
    ],
) -> str:
    if isinstance(filters_obj, schemas.InfodengueFilters):
        return generate_api_infodengue_url(filters_obj)
    elif isinstance(filters_obj, schemas.ClimateFilters):
        return generate_api_climate_url(filters_obj)
    elif isinstance(filters_obj, schemas.MosquitoFilters):
        return generate_api_mosquito_url(filters_obj)
    elif isinstance(filters_obj, schemas.EpiscannerFilters):
        return generate_api_episcanner_url(filters_obj)

    if filters_obj.table == "infodengue":
        return generate_api_infodengue_url(
            schemas.InfodengueFilters(**filters_obj.model_dump())
        )
    elif filters_obj.table == "climate":
        return generate_api_climate_url(
            schemas.ClimateFilters(**filters_obj.model_dump())
        )
    elif filters_obj.table == "mosquito":
        return generate_api_mosquito_url(
            schemas.MosquitoFilters(**filters_obj.model_dump())
        )
    elif filters_obj.table == "episcanner":
        return generate_api_episcanner_url(
            schemas.EpiscannerFilters(**filters_obj.model_dump())
        )
    else:
        raise RuntimeError("Tabela não reconhecida")


def check_api_response(url: str) -> int:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erro ao chamar a API: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar a API: {e}")
