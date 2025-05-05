import json
from typing import Optional, Union

from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from openai import OpenAI

from mosqlimate_assistant import schemas, utils
from mosqlimate_assistant.api_consumer import generate_api_url
from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.prompts import por
from mosqlimate_assistant.settings import (API_KEY, DEEPSEEK_API_URL,
                                           DEEPSEEK_MODEL)


def get_model():
    """
    Inicializa e retorna o modelo de LLM a ser utilizado.
    """
    return OpenAI(api_key=API_KEY, base_url=DEEPSEEK_API_URL)


def make_query(user_input: str) -> str:
    example_template = """Exemplo:\nPergunta: {question}\nResposta: {answer}"""

    prefix = f"""{por.BASE_PROMPT}\n{por.TABLE_PROMPT}\n{por.UF_PROMPT}"""

    suffix = """Agora, responda à seguinte pergunta: {user_question}\n"""

    few_shot_prompt = FewShotPromptTemplate(
        examples=por.EXAMPLES_LIST,
        example_prompt=PromptTemplate(
            input_variables=["question", "answer"], template=example_template
        ),
        prefix=prefix,
        suffix=suffix,
        input_variables=["user_question"],
    )

    full_query = few_shot_prompt.format(user_question=user_input)

    return full_query


def clean_output(output: Optional[str]) -> dict:
    if output is None:
        raise RuntimeError("Erro ao limpar output: output é None")
    if "```json" in output:
        output = output[output.find("```json") + 7 :]
    elif "</think>" in output:
        output = output[output.find("</think>") + 10 :]

    output = output.replace("```", "")
    output = output[output.rfind("{") : output.rfind("}") + 1]
    output = output.replace("None", "null").strip()
    output = output.replace("{{", "{").replace("}}", "}")

    try:
        return json.loads(output)
    except Exception as e:
        raise RuntimeError(f"Erro ao converter o output em json: {e}")


def query_llm(
    prompt: str, save_logs: bool = False, save_path: str = "."
) -> dict:
    full_query = make_query(prompt)
    try:
        modelo = get_model()
        output = (
            modelo.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": full_query},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            .choices[0]
            .message
        )

        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(output)],
                save_path,
            )

        return clean_output(output.content)
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar o modelo: {e}")


def get_table_filters(
    output_json: dict,
) -> Union[
    schemas.InfodengueFilters,
    schemas.ClimateFilters,
    schemas.MosquitoFilters,
    schemas.EpiscannerFilters,
    schemas.TableFilters,
]:
    try:
        output_data = schemas.TableFilters(**output_json)

        if output_data.table == "infodengue":
            return schemas.InfodengueFilters(**output_json)
        elif output_data.table == "climate":
            return schemas.ClimateFilters(**output_json)
        elif output_data.table == "mosquito":
            return schemas.MosquitoFilters(**output_json)
        elif output_data.table == "episcanner":
            return schemas.EpiscannerFilters(**output_json)
        return output_data
    except Exception as e:
        raise RuntimeError(f"Erro ao converter o output em json: {e}")


def generate_mosqlient_infodengue_code(
    filters: schemas.InfodengueFilters,
) -> str:
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


def generate_mosqlient_climate_code(filters: schemas.ClimateFilters) -> str:
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


def make_query_and_get_url(
    prompt: str, save_logs: bool = False, save_path: str = "."
) -> str:
    output_json = query_llm(prompt, save_logs, save_path)
    table_filters = get_table_filters(output_json)
    return generate_api_url(table_filters)
