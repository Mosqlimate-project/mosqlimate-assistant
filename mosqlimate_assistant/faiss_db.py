from typing import Dict
import os

import faiss  # type: ignore
import pandas as pd  # type: ignore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from mosqlimate_assistant.settings import ASKS_PATH, EMBEDDING_MODEL, ASKS_DB_PATH


def create_vector_store(embedding_model: str = EMBEDDING_MODEL) -> FAISS:
    embedding = OllamaEmbeddings(model=embedding_model)
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
    vector_db.add_documents(documents=list(asks.values()), ids=list(asks.keys()))
    vector_db.save_local(output_path)


def load_local_db(db_path: str, embedding_model: str = EMBEDDING_MODEL) -> FAISS:
    embedding = OllamaEmbeddings(model=embedding_model)

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
