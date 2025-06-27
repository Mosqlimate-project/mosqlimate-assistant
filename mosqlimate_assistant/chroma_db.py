import os
from typing import Dict, Optional

import numpy as np
import ollama
import pandas as pd  # type: ignore
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from mosqlimate_assistant import utils
from mosqlimate_assistant.settings import (
    ASKS_PATH,
    ASKS_VECTOR_DB_PATH,
    DOCS_VECTOR_DB_PATH,
    EMBEDDING_MODEL,
)


class OllamaEmbeddingWrapper(Embeddings):
    """Wrapper para usar ollama diretamente com langchain"""

    def __init__(self, model: str, base_url: Optional[str] = None):
        self.model = model
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )

    def _normalize_vector(self, vector: list[float]) -> list[float]:
        np_vector = np.array(vector)
        norm = np.linalg.norm(np_vector)
        if norm == 0:
            return vector
        return (np_vector / norm).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            response = self.client.embeddings(model=self.model, prompt=text)
            normalized_embedding = self._normalize_vector(
                response["embedding"]
            )
            embeddings.append(normalized_embedding)
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings(model=self.model, prompt=text)
        return self._normalize_vector(response["embedding"])


def load_asks(asks_path: str = ASKS_PATH) -> Dict[int, Document]:
    processed_asks: Dict[int, Document] = dict()
    asks_df = pd.read_csv(asks_path)
    for index, row in asks_df.iterrows():
        ask = Document(
            id=str(index),
            page_content=row["Pergunta"],
            metadata={
                "table": row["Tabela"],
                "output": row["JSON"],
            },
        )
        processed_asks[int(str(index))] = ask
    return processed_asks


def load_docs_documents() -> list[Document]:
    docs_map = utils.get_formated_keywords_docs_map()
    documents = list()
    for key, value in docs_map.items():
        doc = Document(
            page_content=value["keywords"],
            metadata={
                "key": key,
                "category": value["category"],
                "description": value["description"],
            },
        )
        documents.append(doc)
    return documents


def get_or_create_vector_db(
    db_path: str = ASKS_VECTOR_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> Chroma:
    embedding = OllamaEmbeddingWrapper(
        model=embedding_model, base_url=os.getenv("OLLAMA_URL")
    )
    if os.path.exists(db_path):
        return Chroma(
            persist_directory=db_path,
            embedding_function=embedding,
            collection_name=os.path.basename(db_path),
        )
    return Chroma.from_documents(
        list(load_asks().values()),
        embedding,
        persist_directory=db_path,
        collection_name=os.path.basename(db_path),
    )


def get_relevant_sample_asks(
    prompt: str,
    k: int = 3,
    db_path: Optional[str] = None,
    embedding_model: str = EMBEDDING_MODEL,
) -> tuple[list[dict[str, str]], list[float]]:
    if db_path is None:
        db_path = ASKS_VECTOR_DB_PATH
    vector_db = get_or_create_vector_db(db_path, embedding_model)
    docs = vector_db.similarity_search_with_score(prompt, k=k)
    samples = [
        {
            "question": doc[0].page_content,
            "answer": utils.format_answer(doc[0].metadata["output"]),
        }
        for doc in docs
    ]
    scores = [1.0 - float(doc[1]) for doc in docs]
    return samples, scores


def get_or_create_docs_vector_db(
    db_path: str = DOCS_VECTOR_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> Chroma:
    embedding = OllamaEmbeddingWrapper(
        model=embedding_model, base_url=os.getenv("OLLAMA_URL")
    )
    if os.path.exists(db_path):
        return Chroma(
            persist_directory=db_path,
            embedding_function=embedding,
            collection_name=os.path.basename(db_path),
        )
    return Chroma.from_documents(
        load_docs_documents(),
        embedding,
        persist_directory=db_path,
        collection_name=os.path.basename(db_path),
    )


def get_relevant_docs(
    prompt: str,
    k: int = 3,
    db_path: Optional[str] = None,
    embedding_model: str = EMBEDDING_MODEL,
) -> tuple[list[dict[str, str]], list[float]]:
    if db_path is None:
        db_path = DOCS_VECTOR_DB_PATH
    vector_db = get_or_create_docs_vector_db(db_path, embedding_model)
    docs = vector_db.similarity_search_with_score(prompt, k=k)
    samples = [
        {
            "key": doc[0].metadata["key"],
            "category": doc[0].metadata["category"],
            "description": doc[0].metadata["description"],
            "keywords": doc[0].page_content,
        }
        for doc in docs
    ]
    scores = [1.0 - float(doc[1]) for doc in docs]
    return samples, scores
