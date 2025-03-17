from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
import faiss

EMBEDDING_MODEL = "mxbai-embed-large:latest"

embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)
docstore = InMemoryDocstore()

index = faiss.IndexFlatIP(len(embedding.embed_query("hello")))

vector_store = FAISS(
    embedding_function=embedding,
    index=index,
    docstore=docstore,
    index_to_docstore_id={},
)

