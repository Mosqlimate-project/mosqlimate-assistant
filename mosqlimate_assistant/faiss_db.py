from typing import Dict

import faiss  # type: ignore
import pandas as pd  # type: ignore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from mosqlimate_assistant.settings import ASKS_PATH, EMBEDDING_MODEL


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
            metadata={"table": row["Tabela"]},
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
    embedding = OllamaEmbeddings(model=embedding_model)

    vector_store = FAISS.load_local(
        folder_path=db_path,
        embeddings=embedding,
        allow_dangerous_deserialization=True,
    )

    return vector_store


# vector_db = create_vector_store()
# asks = load_asks()

# save_asks_local_db(vector_db, asks, "asks_db")
# vector_db2 = load_local_db("asks_db")
