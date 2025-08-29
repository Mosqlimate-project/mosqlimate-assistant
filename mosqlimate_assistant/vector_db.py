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
    BLOCKS_DB_PATH,
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
    def __init__(
        self,
        embedding_model: str = EMBEDDING_MODEL,
        use_keywords: bool = False,
    ):
        self.embedding_model = embedding_model
        self.use_keywords = use_keywords
        self.embedding_function = OllamaEmbeddingWrapper(
            model=embedding_model,
            base_url=os.getenv("OLLAMA_URL"),
        )
        self.embeddings: Optional[np.ndarray] = None
        self.documents: Optional[List[Document]] = None

    def _compute_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        if self.embeddings is None:
            raise ValueError("O banco de dados vetorial não foi inicializado")
        norm = np.linalg.norm(query_embedding)
        return np.dot(
            self.embeddings,
            query_embedding if norm == 0 else query_embedding / norm,
        )

    def add_documents(self, documents: List[Document], save_path: str) -> None:
        if self.use_keywords:
            texts = [
                (
                    doc.metadata.get("keywords", "")
                    if "keywords" in doc.metadata
                    else doc.page_content
                )
                for doc in documents
            ]
        else:
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
            "use_keywords": self.use_keywords,
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
            self.use_keywords = data.get("use_keywords", False)
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
    db_path: str = ASKS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
    use_keywords: bool = False,
) -> VectorDB:
    vector_db = VectorDB(embedding_model, use_keywords=use_keywords)

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
    use_keywords: bool = False,
) -> Tuple[List[Dict[str, str]], List[float]]:
    if db_path is None:
        db_path = ASKS_DB_PATH

    vector_db = get_or_create_vector_db(db_path, use_keywords=use_keywords)
    docs = vector_db.similarity_search_with_score(prompt, k=k)

    samples = [
        {
            "ask": doc[0].page_content,
            "table": doc[0].metadata["table"],
            "output": doc[0].metadata["output"],
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

        # Estruturar o conteúdo do documento com informações organizadas
        structured_content = f"""Descrição: {value["description"]}
Palavras-chave: {", ".join(value["keywords"])}

Conteúdo do documento:
{markdown_content}"""

        doc = Document(
            page_content=structured_content,
            metadata={
                "key": key,
                "category": value["category"],
                "description": value["description"],
                "link": value["link"],
                "keywords": ", ".join(value["keywords"]),
                "raw_content": markdown_content,
            },
        )
        documents.append(doc)
    return documents


def get_or_create_docs_vector_db(
    db_path: str = DOCS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
    use_keywords: bool = False,
) -> VectorDB:
    vector_db = VectorDB(embedding_model, use_keywords=use_keywords)

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
    use_keywords: bool = False,
) -> Tuple[List[Dict[str, str]], List[float]]:
    if db_path is None:
        db_path = DOCS_DB_PATH

    vector_db = get_or_create_docs_vector_db(
        db_path, use_keywords=use_keywords
    )
    docs = vector_db.similarity_search_with_score(prompt, k=k)

    samples = [
        {
            "key": doc[0].metadata.get("key", "unknown"),
            "category": doc[0].metadata.get("category", "unknown"),
            "description": doc[0].metadata.get("description", "Sem descrição"),
            "link": doc[0].metadata.get("link", ""),
            "keywords": doc[0].metadata.get("keywords", ""),
            "content": doc[0].page_content,
            "raw_content": doc[0].metadata.get(
                "raw_content", doc[0].page_content
            ),
        }
        for doc in docs
    ]
    scores = [float(doc[1]) for doc in docs]

    return samples, scores


def load_docs_blocks() -> List[Document]:
    blocks_map = utils.DOCS_BLOCKS_MAP
    docs_map = utils.DOCS_KEYWORDS_MAP
    documents = list()

    for block_key, doc_keys in blocks_map.items():
        # Combinar conteúdos e metadados
        structured_content = f"Bloco: {block_key}\n\n"
        all_keywords = list()
        all_links = list()
        all_descriptions = list()
        combined_raw_content = ""

        for doc_key in doc_keys:
            if doc_key in docs_map:
                doc_info = docs_map[doc_key]
                content = doc_info["function"]()

                structured_content += f"""Documento: {doc_info['description']}
Palavras-chave: {", ".join(doc_info['keywords'])}

Conteúdo:
{content}

---

"""

                all_keywords.extend(doc_info["keywords"])
                all_links.append(doc_info["link"])
                all_descriptions.append(doc_info["description"])
                combined_raw_content += (
                    f"\n\n# {doc_info['description']}\n\n{content}"
                )

        doc = Document(
            page_content=structured_content.strip(),
            metadata={
                "block_key": block_key,
                "doc_keys": doc_keys,
                "links": all_links,
                "descriptions": all_descriptions,
                "keywords": ", ".join(set(all_keywords)),
                "raw_content": combined_raw_content.strip(),
            },
        )
        documents.append(doc)

    return documents


def get_or_create_blocks_vector_db(
    db_path: str = BLOCKS_DB_PATH,
    embedding_model: str = EMBEDDING_MODEL,
    use_keywords: bool = False,
) -> VectorDB:
    vector_db = VectorDB(embedding_model, use_keywords=use_keywords)

    try:
        vector_db.load(db_path)
    except (FileNotFoundError, Exception):
        documents = load_docs_blocks()
        vector_db.add_documents(documents, db_path)

    return vector_db


def get_relevant_blocks(
    prompt: str,
    k: int = 3,
    threshold: float = 0.3,
    db_path: Optional[str] = None,
    use_keywords: bool = False,
) -> Tuple[List[Dict[str, any]], List[float]]:
    if db_path is None:
        db_path = BLOCKS_DB_PATH

    vector_db = get_or_create_blocks_vector_db(
        db_path, use_keywords=use_keywords
    )
    docs_with_scores = vector_db.similarity_search_with_score(
        prompt, k=len(vector_db.documents) if vector_db.documents else k
    )

    # Verificar se scores são baixos e recomendar introdução
    best_score = docs_with_scores[0][1] if docs_with_scores else 0

    if best_score < threshold:
        intro_blocks = ["project_intro_block", "getting_started_block"]
        filtered_docs = [
            doc
            for doc in docs_with_scores
            if doc[0].metadata["block_key"] in intro_blocks
        ]
        if filtered_docs:
            docs_with_scores = filtered_docs[:1] + docs_with_scores[: k - 1]

    docs_with_scores = docs_with_scores[:k]

    samples = []
    scores = []

    for doc, score in docs_with_scores:
        samples.append(
            {
                "block_key": doc.metadata["block_key"],
                "doc_keys": doc.metadata["doc_keys"],
                "links": doc.metadata["links"],
                "descriptions": doc.metadata["descriptions"],
                "keywords": (
                    doc.metadata["keywords"][:200] + "..."
                    if len(doc.metadata["keywords"]) > 200
                    else doc.metadata["keywords"]
                ),
                "content": (
                    doc.page_content[:1000] + "..."
                    if len(doc.page_content) > 1000
                    else doc.page_content
                ),
                "raw_content": (
                    doc.metadata.get("raw_content", "")[:1000] + "..."
                    if len(doc.metadata.get("raw_content", "")) > 1000
                    else doc.metadata.get("raw_content", "")
                ),
            }
        )
        scores.append(float(score))

    return samples, scores
