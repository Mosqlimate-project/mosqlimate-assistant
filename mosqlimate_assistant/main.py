from mosqlimate_assistant import assistant, vector_db
from mosqlimate_assistant.prompts import por


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
    relevant_docs, docs_scores = vector_db.get_relevant_docs(question, k=k_num)
    similar_docs = [
        doc for doc, score in zip(relevant_docs, docs_scores) if score > 0.5
    ]
    if len(similar_docs) < 2:
        similar_docs += [
            doc for doc in por.DEFAULT_DOCS_LIST if doc not in similar_docs
        ]
    return docs_pipeline(question, similar_docs)
