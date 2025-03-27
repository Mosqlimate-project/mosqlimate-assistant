from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

from mosqlimate_assistant.prompts import por
from mosqlimate_assistant import filters
from mosqlimate_assistant import utils
from mosqlimate_assistant.configs import API_KEY

import mosqlient
import requests
import json

# A ser substituido no futuro
modelo = OllamaLLM(model="llama3.1:latest", device='cuda')
BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"

def make_query(user_input:str) -> str:
    example_template = """Exemplo:\nPergunta: {question}\nResposta: {answer}"""

    prefix = f"""{por.BASE_PROMPT}\n{por.TABLE_PROMPT}\n{por.UF_PROMPT}"""

    suffix = """Agora, responda à seguinte pergunta: {user_question}\n"""

    few_shot_prompt = FewShotPromptTemplate(
        examples=por.EXAMPLES_LIST,
        example_prompt=PromptTemplate(
            input_variables=["question", "answer"],
            template=example_template
        ),
        prefix=prefix,
        suffix=suffix,
        input_variables=["user_question"]
    )

    full_query = few_shot_prompt.format(user_question=user_input)

    return full_query

def clean_output(output:str) -> dict:
    if "```json" in output:
        output = output[output.find("```json")+7:]
    elif "</think>" in output:
        output = output[output.find("</think>")+10:]
    
    output = output.replace("```", "")
    output = output[output.rfind("{"):output.rfind("}")+1]
    output = output.replace("None", "null").strip()
    output = output.replace("{{", "{").replace("}}", "}")
    
    try:
        return json.loads(output)
    except Exception as e:
        raise RuntimeError(f"Erro ao converter o output em json: {e}")

def query_llm(prompt:str) -> dict:
    full_query = make_query(prompt)
    try:
        output = modelo.invoke(full_query)
        return clean_output(output)
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar o Ollama: {e}")
    
def get_municipality_code(municipality:str, uf:str) -> str:
    try:
        municipality_code = utils.get_municipality(municipality, uf)
        return municipality_code["Code"]
    except Exception as e:
        raise RuntimeError(f"Erro ao obter o código do município: {e}")

def get_table_filters(output_json:dict) -> filters.TableFilters:
    try:
        output_data = filters.TableFilters(**output_json)

        if output_data.table == "infodengue":
            return filters.InfodengueFilters(**output_json)
        elif output_data.table == "climate":
            return filters.ClimateFilters(**output_json)
        elif output_data.table == "mosquito":
            return filters.MosquitoFilters(**output_json)
        elif output_data.table == "episcanner":
            return filters.EpiscannerFilters(**output_json)
        
    except Exception as e:
        raise RuntimeError(f"Erro ao converter o output em json: {e}")

def generate_api_infodengue_url(filters:filters.InfodengueFilters) -> str:
    url = f"{BASE_URL_API}infodengue?page=1&per_page=100&disease={filters.disease}&start={filters.start}&end={filters.end}"
    if filters.uf:
        url += f"&uf={filters.uf}"
    if filters.city:
        geocode = get_municipality_code(filters.city, filters.uf)
        url += f"&geocode={geocode}"
    return url

def generate_api_climate_url(filters:filters.ClimateFilters) -> str:
    url = f"{BASE_URL_API}climate?page=1&per_page=100&start={filters.start}&end={filters.end}"
    if filters.uf:
        url += f"&uf={filters.uf}"
    if filters.city:
        geocode = get_municipality_code(filters.city, filters.uf)
        url += f"&geocode={geocode}"
    return url

def generate_api_mosquito_url(filters:filters.MosquitoFilters) -> str:
    return f"{BASE_URL_API}mosquito?page=1&key={filters.key}"

def generate_api_episcanner_url(filters:filters.EpiscannerFilters) -> str:
    url = f"{BASE_URL_API}episcanner?disease={filters.disease}&uf={filters.uf}"
    if filters.year:
        url += f"&year={filters.year}"
    return url

def generate_api_url(filters:filters.TableFilters) -> str:
    if filters.table == "infodengue":
        return generate_api_infodengue_url(filters)
    elif filters.table == "climate":
        return generate_api_climate_url(filters)
    elif filters.table == "mosquito":
        return generate_api_mosquito_url(filters)
    elif filters.table == "episcanner":
        return generate_api_episcanner_url(filters)
    else:
        raise RuntimeError("Tabela não reconhecida")

def generate_mosqlient_infodengue_code(filters:filters.InfodengueFilters) -> str:
    BASE_CODE = f"""from mosqlient import get_infodengue

# return a pd.DataFrame with the data 
df = get_infodengue(
    start_date='{filters.start}',
    end_date='{filters.end}',
    disease='{filters.disease}'\n"""
    
    if filters.uf:
        BASE_CODE += f"    uf='{filters.uf}',\n"
    
    BASE_CODE += ")"
    return BASE_CODE

def generate_mosqlient_climate_code(filters:filters.ClimateFilters) -> str:
    BASE_CODE = f"""from mosqlient import get_climate

# return a pd.DataFrame with the data 
df = get_climate(
    start_date='{filters.start}',
    end_date='{filters.end}'\n"""

    if filters.city:
        geocode = get_municipality_code(filters.city, filters.uf)
        BASE_CODE += f"    geocode='{geocode}',\n"
    
    BASE_CODE += ")"
    return BASE_CODE

def make_query_and_get_url(prompt:str) -> str:
    output_json = query_llm(prompt)
    table_filters = get_table_filters(output_json)
    return generate_api_url(table_filters)

def check_api_response(url:str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erro ao chamar a API: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar a API: {e}")

