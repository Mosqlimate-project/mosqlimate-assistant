import json
from typing import Any, Optional

import Levenshtein

from mosqlimate_assistant.settings import MUNICIPALITIES_PATH, VALID_UFS


def get_closest_match(
    input_text: str, options: list[dict[str, Any]]
) -> tuple[dict[str, Any], float]:
    closest_match: dict[str, Any] = {
        "Municipality": "",
        "UF": "",
        "Code": "",
        "distance": float("inf"),
    }
    for option in options:
        distance = float(
            Levenshtein.distance(input_text, option["Municipality"])
        )
        if distance < closest_match["distance"]:
            closest_match = {**option, "distance": distance}
    return closest_match, closest_match["distance"]


def read_municipalities() -> list[dict[str, Any]]:
    with open(MUNICIPALITIES_PATH, "r") as file:
        municipalities = json.load(file)

        for m in municipalities:
            m["Municipality"] = m["Municipality"].lower().strip()

    return municipalities


def filter_by_uf(municipalities: list[dict], uf: str) -> list[dict]:
    if uf.upper() not in VALID_UFS:
        raise ValueError(f"UF inválida: {uf}")

    filtered = [m for m in municipalities if m["UF"] == uf.upper()]
    return filtered


def get_municipality(name: str, uf: str | None = None) -> dict:
    name = name.lower().strip()

    municipalities = read_municipalities()
    closest_match, closest_distance = get_closest_match(name, municipalities)

    if uf and closest_match["UF"] != uf.upper():
        municipalities_filter = filter_by_uf(municipalities, uf)
        closest_match_filter, closest_distance_filter = get_closest_match(
            name, municipalities_filter
        )

        if (
            closest_match_filter["Code"] != closest_match["Code"]
            and closest_distance_filter <= closest_distance
        ):
            closest_match = closest_match_filter
            closest_distance = closest_distance_filter

    if closest_distance > 4:
        raise ValueError(f"Município não encontrado: {name}")

    return closest_match


def get_municipality_code(municipality: str, uf: Optional[str]) -> int:
    try:
        municipality_code = get_municipality(municipality, uf)
        return municipality_code["Code"]
    except ValueError as ve:
        raise RuntimeError(f"Erro ao obter o código do município: {ve}")
    except Exception as e:
        raise RuntimeError(f"Erro ao obter o código do município: {e}")


def get_muni_and_uf_from_code(code: str) -> tuple[str, str]:
    municipalities = read_municipalities()
    for m in municipalities:
        if m["Code"] == code:
            return m["Municipality"], m["UF"]
    raise ValueError(f"Código de município não encontrado: {code}")
