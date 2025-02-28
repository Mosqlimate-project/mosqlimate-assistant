from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from mosqlimate_assistant.prompts import por
from mosqlimate_assistant import filters
import requests
import json

# A ser substituido no futuro
modelo = OllamaLLM(model="llama3.1:latest", device='cuda')

BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"

def make_query(user_input:str) -> str:
    example_template = """Exemplo:
Pergunta: {question}
Resposta: {answer}"""

    prefix = f"""{por.BASE_PROMPT}
{por.TABLE_PROMPT}
{por.UF_PROMPT}"""

    suffix = """Agora, responda à seguinte pergunta: {user_question}
"""

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

    print(full_query)
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

def get_table_filters(output_json:dict) -> filters.TableFilters:
    output_data = filters.TableFilters(**output_json)
    try:
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
    # if filters.geocode:
    #     url += f"&geocode={filters.geocode}"
    return url

def generate_api_climate_url(filters:filters.ClimateFilters) -> str:
    url = f"{BASE_URL_API}climate?page=1&per_page=100&start={filters.start}&end={filters.end}"
    if filters.uf:
        url += f"&uf={filters.uf}"
    # if filters.geocode:
    #     url += f"&geocode={filters.geocode}"
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

