from typing import Dict, List, Optional

from mosqlimate_assistant import assistant, utils, vector_db


def docs_pipeline(
    question: str,
    similar_docs: Optional[List[Dict[str, str]]] = None,
) -> str:
    mosqlimate_assistant = assistant.AssistantGemini()

    if similar_docs is None:
        similar_docs = [
            {
                "key": key,
                "category": value["category"],
                "description": value["description"],
                "link": value.get("link", ""),
            }
            for key, value in utils.DOCS_KEYWORDS_MAP.items()
        ]

    result = mosqlimate_assistant.query_llm_docs(
        prompt=question,
        similar_docs=similar_docs,
    )
    return result["content"]


def assistant_pipeline(
    question: str,
    k_num: int = 4,
    full_context: bool = False,
) -> str:
    if full_context:
        similar_docs = [
            {
                "key": key,
                "category": value["category"],
                "description": value["description"],
                "link": value.get("link", ""),
            }
            for key, value in utils.DOCS_KEYWORDS_MAP.items()
        ]
    else:
        relevant_docs, docs_scores = vector_db.get_relevant_docs(
            question, k=k_num
        )
        similar_docs = [
            doc
            for doc, score in zip(relevant_docs, docs_scores)
            if score > 0.5
        ]
    return docs_pipeline(question, similar_docs)
