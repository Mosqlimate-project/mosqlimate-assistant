import json
import Levenshtein
import unidecode

MUNICIPALITIES_PATH = "../data/municipios.json"

VALID_UFS = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
        "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]

def process_input(input_text:str) -> str:
    input_text = unidecode.unidecode(input_text)
    input_text = input_text.lower()
    return input_text.strip()

def get_closest_match(input_text:str, options:list[dict]) -> str:
    closest_match = None
    closest_distance = float('inf')
    for option in options:
        distance = Levenshtein.distance(input_text, option["Municipality"])
        if distance < closest_distance:
            closest_distance = distance
            closest_match = option
    return closest_match, closest_distance

def read_municipalities() -> list[dict]:
    with open(MUNICIPALITIES_PATH, "r") as file:
        municipalities = json.load(file)

        for m in municipalities:
            m["Municipality"] = process_input(m["Municipality"])

    return municipalities

def filter_by_uf(municipalities:list[dict], uf:str) -> list[dict]:
    filtered = [m for m in municipalities if m["UF"] == uf.upper()]
    return filtered

