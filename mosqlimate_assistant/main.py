from mosqlimate_assistant import assistant, vector_db
from mosqlimate_assistant.api_consumer import generate_api_url
from mosqlimate_assistant.muni_codes import get_muni_and_uf_from_code
from mosqlimate_assistant.prompts import por
from mosqlimate_assistant.schemas import ClimateFilters, InfodengueFilters


def api_pipeline(
    question: str,
    relevant_samples: list,
) -> str:
    mosqlimate_assistant = assistant.AssistantGemini()

    result = str()

    parameters = mosqlimate_assistant.query_llm(
        prompt=question,
        examples_list=relevant_samples,
    )

    table_filters = mosqlimate_assistant.get_table_filters(parameters)

    api_url = generate_api_url(table_filters)

    python_code = None
    if isinstance(table_filters, InfodengueFilters):
        python_code = mosqlimate_assistant.generate_mosqlient_infodengue_code(
            filters=table_filters
        )
    elif isinstance(table_filters, ClimateFilters):
        python_code = mosqlimate_assistant.generate_mosqlient_climate_code(
            filters=table_filters
        )

    geocode = parameters.get("geocode", None)
    city_name, uf_name = None, None
    if geocode:
        city_name, uf_name = get_muni_and_uf_from_code(geocode)

    result += "URL da API desejada:\n"
    result += f"`{api_url}`\n"
    if python_code:
        result += f"\nExemplo de código Python para obter os dados:\n```python\n{python_code}\n```\n"
    if city_name and uf_name:
        result += (
            f"\nO geocode é referente a cidade: {city_name} - {uf_name}\n"
        )

    return result


def docs_pipeline(
    question: str,
    similar_docs: list[dict[str, str]] = por.DEFAULT_DOCS_LIST,
) -> str:

    mosqlimate_assistant = assistant.AssistantGemini()

    result = mosqlimate_assistant.query_llm_docs(
        prompt=question,
        similar_docs=similar_docs,
    )

    return result["content"]


def assistant_pipeline(
    question: str,
    k_num=4,
) -> str:

    relevant_samples, scores = vector_db.get_relevant_sample_asks(
        question, k=k_num
    )

    if scores and scores[0] > 0.75:
        return api_pipeline(question, relevant_samples)

    relevant_docs, docs_scores = vector_db.get_relevant_docs(question, k=k_num)

    similar_docs = [
        doc for doc, score in zip(relevant_docs, docs_scores) if score > 0.5
    ]

    if len(similar_docs) < 2:
        similar_docs += [
            doc for doc in por.DEFAULT_DOCS_LIST if doc not in similar_docs
        ]

    return docs_pipeline(question, similar_docs)
