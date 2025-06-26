import os
from typing import Dict, Optional

import faiss  # type: ignore
import numpy as np
import ollama
import pandas as pd  # type: ignore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from mosqlimate_assistant import utils
from mosqlimate_assistant.settings import (
    ASKS_DB_PATH,
    ASKS_PATH,
    DOCS_DB_PATH,
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
        """Normaliza o vetor para magnitude unitária"""
        np_vector = np.array(vector)
        norm = np.linalg.norm(np_vector)
        if norm == 0:
            return vector
        return (np_vector / norm).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            response = self.client.embeddings(model=self.model, prompt=text)
            normalized_embedding = self._normalize_vector(
                response["embedding"]
            )
            embeddings.append(normalized_embedding)
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query"""
        response = self.client.embeddings(model=self.model, prompt=text)
        return self._normalize_vector(response["embedding"])


def create_vector_store(embedding_model: str = EMBEDDING_MODEL) -> FAISS:
    ollama_url = os.getenv("OLLAMA_URL", None)

    embedding = OllamaEmbeddingWrapper(
        model=embedding_model,
        base_url=ollama_url,
    )

    docstore = InMemoryDocstore()

    index = faiss.IndexFlatIP(len(embedding.embed_query("hello")))

    vector_store = FAISS(
        embedding_function=embedding,
        index=index,
        docstore=docstore,
        index_to_docstore_id={},
    )

    return vector_store


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


def save_asks_local_db(
    vector_db: FAISS, asks: Dict[int, Document], output_path: str
) -> None:
    vector_db.add_documents(
        documents=list(asks.values()), ids=list(asks.keys())
    )
    vector_db.save_local(output_path)


def load_local_db(
    db_path: str, embedding_model: str = EMBEDDING_MODEL
) -> FAISS:
    ollama_url = os.getenv("OLLAMA_URL")

    embedding = OllamaEmbeddingWrapper(
        model=embedding_model,
        base_url=ollama_url,
    )

    vector_store = FAISS.load_local(
        folder_path=db_path,
        embeddings=embedding,
        allow_dangerous_deserialization=True,
    )

    return vector_store


def get_or_create_vector_db(
    db_path: str = ASKS_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> FAISS:
    """
    Retorna o vetor store FAISS carregado do disco, ou o cria e salva localmente se não existir.
    """
    if os.path.exists(db_path):
        return load_local_db(db_path, embedding_model)
    # cria e salva o vetor store
    asks = load_asks()
    vector_db = create_vector_store(embedding_model)
    save_asks_local_db(vector_db, asks, db_path)
    return vector_db


def get_relevant_sample_asks(
    prompt: str, k: int = 3
) -> tuple[list[dict[str, str]], list[float]]:
    vector_db = get_or_create_vector_db()
    docs = vector_db.similarity_search_with_score(prompt, k=k)
    samples = [
        {
            "question": doc[0].page_content,
            "answer": utils.format_answer(doc[0].metadata["output"]),
        }
        for doc in docs
    ]

    scores = [float(doc[1]) for doc in docs]

    return samples, scores


def load_docs_documents(
    db_path: str = DOCS_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> list[Document]:
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


def save_docs_local_db(
    vector_store: FAISS,
    db_path: str = DOCS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
) -> None:
    documents = load_docs_documents(db_path, embedding_model)
    vector_store.add_documents(documents)
    vector_store.save_local(db_path)


def get_or_create_docs_vector_db(
    db_path: str = DOCS_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> FAISS:
    if os.path.exists(db_path):
        return load_local_db(db_path, embedding_model)

    vector_db = create_vector_store(embedding_model)
    save_docs_local_db(vector_db, db_path, embedding_model)
    return vector_db


def get_relevant_docs(
    prompt: str, k: int = 3
) -> tuple[list[dict[str, str]], list[float]]:
    vector_db = get_or_create_docs_vector_db()
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

    scores = [float(doc[1]) for doc in docs]

    return samples, scores
