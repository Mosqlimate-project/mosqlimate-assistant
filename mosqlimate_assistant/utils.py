from mosqlimate_assistant.configs import DATABASE_PATH
import Levenshtein
import json
import os

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

MUNICIPALITIES_PATH = os.path.join(DATABASE_PATH,"municipios.json")
MUNICIPALITIES_PATH = os.path.join(CURRENT_PATH, MUNICIPALITIES_PATH)

VALID_UFS = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
        "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]

MOSQLIMATE_API_DOCS = "https://api.mosqlimate.org/api/openapi.json"

def process_input(input_text:str) -> str:
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
    if uf.upper() not in VALID_UFS:
        raise ValueError(f"UF inválida: {uf}")

    filtered = [m for m in municipalities if m["UF"] == uf.upper()]
    return filtered

def get_municipality(name:str, uf:str|None = None) -> dict:
    name = process_input(name)

    municipalities = read_municipalities()
    closest_match, closest_distance = get_closest_match(name, municipalities)
    
    if uf and closest_match["UF"] != uf.upper():
        municipalities_filter = filter_by_uf(municipalities, uf)
        closest_match_filter, closest_distance_filter = get_closest_match(name, municipalities_filter)
    
        if closest_match_filter["Code"] != closest_match["Code"] & closest_distance_filter <= closest_distance:
            closest_match = closest_match_filter
            closest_distance = closest_distance_filter
            
    if closest_distance > 3:
        raise ValueError(f"Município não encontrado: {name}")
    
    return closest_match

def save_logs(logs:list[str], save_path:str='.') -> None:
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    save_file = os.path.join(save_path, "prompt_logs.txt")
    with open(save_file, "a") as file:
        for log in logs:
            file.write(log)
            file.write("\n")
        file.write("\n\n")

def get_mosqlimate_api_docs() -> dict:
    import requests
    response = requests.get(MOSQLIMATE_API_DOCS)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Erro ao obter a documentação da API: {response.status_code}")
