import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import ollama
import pandas as pd
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
    def __init__(self, model: str, base_url: Optional[str] = None):
        self.model = model
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        arr = np.asarray(vector, dtype=float)
        norm = np.linalg.norm(arr)
        return (arr / norm).tolist() if norm > 0 else vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [
            self._normalize(
                self.client.embeddings(model=self.model, prompt=text)[
                    "embedding"
                ]
            )
            for text in texts
        ]

    def embed_query(self, text: str) -> List[float]:
        vec = self.client.embeddings(model=self.model, prompt=text)[
            "embedding"
        ]
        return self._normalize(vec)


class VectorDB:
    def __init__(self, embedding_model: str = EMBEDDING_MODEL):
        self.embedding_model = embedding_model
        self.embedding_function = OllamaEmbeddingWrapper(
            model=embedding_model,
            base_url=os.getenv("OLLAMA_URL"),
        )
        self.embeddings: Optional[np.ndarray] = None
        self.documents: Optional[List[Document]] = None

    def _compute_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        if self.embeddings is None:
            raise ValueError("O banco de dados vetorial não foi inicializado")
        query_embedding_normalized = query_embedding / np.linalg.norm(
            query_embedding
        )
        return np.dot(self.embeddings, query_embedding_normalized)

    def add_documents(self, documents: List[Document], save_path: str) -> None:
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_function.embed_documents(texts)

        self.embeddings = np.array(embeddings)
        self.documents = documents

        Path(save_path).mkdir(parents=True, exist_ok=True)
        store_path = Path(save_path) / "vector_store.pkl"

        data = {
            "embeddings": self.embeddings,
            "docs_content": [doc.page_content for doc in documents],
            "docs_metadata": [doc.metadata for doc in documents],
        }
        pd.to_pickle(data, store_path)

    def load(self, load_path: str) -> None:
        store_path = Path(load_path) / "vector_store.pkl"

        if not store_path.exists():
            raise FileNotFoundError(
                f"Arquivo do banco de dados não encontrado: {store_path}"
            )

        try:
            data = pd.read_pickle(store_path)
            self.embeddings = data["embeddings"]
            self.documents = [
                Document(page_content=content, metadata=metadata)
                for content, metadata in zip(
                    data["docs_content"], data["docs_metadata"]
                )
            ]
        except Exception as e:
            raise IOError(
                f"Erro ao carregar o banco de dados vetorial: {str(e)}"
            )

    def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        if self.embeddings is None or self.documents is None:
            raise ValueError("O banco de dados vetorial não foi inicializado")

        query_embedding = np.array(self.embedding_function.embed_query(query))
        similarities = self._compute_similarity(query_embedding)
        top_k_idx = np.argsort(similarities)[-k:][::-1]

        results = list()
        for idx in top_k_idx:
            results.append((self.documents[idx], float(similarities[idx])))

        return results


def load_asks(asks_path: str = ASKS_PATH) -> Dict[int, Document]:
    processed_asks: Dict[int, Document] = dict()
    asks_df = pd.read_csv(asks_path)
    for index, row in asks_df.iterrows():
        ask = Document(
            page_content=row["Pergunta"],
            metadata={
                "table": row["Tabela"],
                "output": row["JSON"],
            },
        )
        processed_asks[int(str(index))] = ask
    return processed_asks


def get_or_create_vector_db(
    db_path: str = ASKS_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> VectorDB:
    vector_db = VectorDB(embedding_model)

    try:
        vector_db.load(db_path)
    except (FileNotFoundError, Exception):
        asks = load_asks()
        vector_db.add_documents(list(asks.values()), db_path)

    return vector_db


def get_relevant_sample_asks(
    prompt: str,
    k: int = 3,
    db_path: Optional[str] = None,
) -> Tuple[List[Dict[str, str]], List[float]]:
    if db_path is None:
        db_path = ASKS_DB_PATH

    vector_db = get_or_create_vector_db(db_path)
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


def load_docs_documents() -> List[Document]:
    docs_map = utils.DOCS_KEYWORDS_MAP
    documents = []
    for key, value in docs_map.items():
        # Obter o conteúdo completo do markdown
        markdown_content = value["function"]()

        doc = Document(
            page_content=markdown_content,
            metadata={
                "key": key,
                "category": value["category"],
                "description": value["description"],
                "keywords": ", ".join(value["keywords"]),
            },
        )
        documents.append(doc)
    return documents


def get_or_create_docs_vector_db(
    db_path: str = DOCS_DB_PATH, embedding_model: str = EMBEDDING_MODEL
) -> VectorDB:
    vector_db = VectorDB(embedding_model)

    try:
        vector_db.load(db_path)
    except (FileNotFoundError, Exception):
        documents = load_docs_documents()
        vector_db.add_documents(documents, db_path)

    return vector_db


def get_relevant_docs(
    prompt: str,
    k: int = 3,
    db_path: Optional[str] = None,
) -> Tuple[List[Dict[str, str]], List[float]]:
    if db_path is None:
        db_path = DOCS_DB_PATH

    vector_db = get_or_create_docs_vector_db(db_path)
    docs = vector_db.similarity_search_with_score(prompt, k=k)

    samples = [
        {
            "key": doc[0].metadata["key"],
            "category": doc[0].metadata["category"],
            "description": doc[0].metadata["description"],
            "keywords": doc[0].metadata["keywords"],
            "content": doc[0].page_content,
        }
        for doc in docs
    ]
    scores = [float(doc[1]) for doc in docs]

    return samples, scores
