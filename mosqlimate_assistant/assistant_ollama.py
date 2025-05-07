import json
from typing import Optional, Union

import ollama
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

from mosqlimate_assistant import faiss_db, schemas, utils
from mosqlimate_assistant.api_consumer import generate_api_url
from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.prompts import por

OLLAMA_MODEL = "llama3.2:latest"


def make_query(
    user_input: str, examples_list: list[dict[str, str]] = por.EXAMPLES_LIST
) -> str:
    # Escape braces in example answers to prevent formatting errors
    escaped_examples: list[dict[str, str]] = []
    for ex in examples_list:
        escaped_examples.append(
            {
                "question": ex["question"],
                "answer": ex["answer"].replace("{", "{{").replace("}", "}}"),
            }
        )
    example_template = """Exemplo:\nPergunta: {question}\nResposta: {answer}"""

    prefix = f"""{por.BASE_PROMPT}\n{por.TABLE_PROMPT}\n{por.UF_PROMPT}"""

    suffix = """Agora, responda à seguinte pergunta: {user_question}\n"""

    few_shot_prompt = FewShotPromptTemplate(
        examples=escaped_examples,
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
    prompt: str,
    examples_list: list[dict[str, str]] = por.EXAMPLES_LIST,
    save_logs: bool = False,
    save_path: str = ".",
) -> dict:
    full_query = make_query(prompt, examples_list=examples_list)
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": full_query},
                {"role": "user", "content": prompt},
            ],
        )
        output = response["message"]["content"]

        if save_logs:
            utils.save_logs(
                ["user: " + str(prompt), "assistant:\n" + str(output)],
                save_path,
            )

        return clean_output(output)
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


def get_relevant_sample_asks(
    prompt: str, k: int = 3
) -> tuple[list[dict[str, str]], float]:
    """
    Retorna uma lista de exemplos relevantes para a pergunta do usuário.
    """
    vector_db = faiss_db.get_or_create_vector_db()
    docs = vector_db.similarity_search_with_score(prompt, k=k)

    samples = [
        {
            "question": doc[0].page_content,
            "answer": utils.format_answer(doc[0].metadata["output"])
            .replace("{", "{{")
            .replace("}", "}}"),
        }
        for doc in docs
    ]

    return samples, float(docs[0][1])


def make_query_and_get_url(
    prompt: str,
    threshold: float = 0.8,
    save_logs: bool = False,
    save_path: str = ".",
) -> str:
    print(OLLAMA_MODEL)
    relevant_samples = get_relevant_sample_asks(prompt)
    if relevant_samples[1] < threshold:
        raise RuntimeError(
            f"Não foi possível encontrar exemplos relevantes para a pergunta: {prompt}"
        )

    output_json = query_llm(prompt, relevant_samples[0], save_logs, save_path)
    print(output_json)
    table_filters = get_table_filters(output_json)
    return generate_api_url(table_filters)
