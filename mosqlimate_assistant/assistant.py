from langchain_ollama import OllamaLLM
from mosqlimate_assistant.prompts import por
import json

# A ser substituido no futuro
modelo = OllamaLLM(model="deepseek-r1:7b", device='cuda')

BASE_URL_API = "https://api.mosqlimate.org/api/datastore/"

def make_query(user_input:str) -> str:
    full_query = f"""
Você é um assistente de pesquisa de dados do Mosqlimate. Seu dever é, a partir da pergunta abaixo fazer o que se pede:

{user_input}

""" + por.BASE_PROMPT + por.TABLE_PROMPT + por.UF_PROMPT + por.EXAMPLE_PROMPT

    return full_query

def clean_output(output:str) -> dict:
    if "<\think>\n" in output:
        output = output[output.find("</think>\n")+10:]
    output = output.replace("````", "").replace("json\n", "")

    try:
        return json.loads(output)
    except Exception as e:
        print("Error in converting output to json:", e)

def query_llm(prompt:str) -> dict:
    try:
        output = modelo.invoke(prompt)
        return clean_output(output)
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar o Ollama: {e}")

