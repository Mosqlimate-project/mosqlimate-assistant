from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
import pandas as pd
import os
import faiss

EMBEDDING_MODEL = "mxbai-embed-large:latest"
FILE_PATH = os.path.dirname(__file__)
ASKS_PATH = os.path.join(FILE_PATH, "../data/asks.csv")

def create_vector_store(EMBEDDING_MODEL:str=EMBEDDING_MODEL) -> FAISS:
    embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)
    docstore = InMemoryDocstore()

    index = faiss.IndexFlatIP(len(embedding.embed_query("hello")))

    vector_store = FAISS(
        embedding_function=embedding,
        index=index,
        docstore=docstore,
        index_to_docstore_id={},
    )
    
    return vector_store

def load_asks(ASKS_PATH:str=ASKS_PATH) -> dict[str:Document]:
    asks = pd.read_csv(ASKS_PATH)
    processed_asks = dict()

    for index, row in asks.iterrows():
        ask = Document(
            id=index,
            page_content=row["Pergunta"],
            metadata={"table": row["Tabela"]},
        )
        processed_asks[index] = ask

    return processed_asks

def save_asks_local_db(vector_db:FAISS, asks:dict[str:Document], output_path:str) -> None:
    vector_db.add_documents(documents=asks.values(), ids=asks.keys())
    vector_db.save_local(output_path)

def load_local_db(db_path:str, EMBEDDING_MODEL:str=EMBEDDING_MODEL) -> FAISS:
    embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)

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

