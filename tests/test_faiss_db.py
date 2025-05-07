from langchain_community.vectorstores import FAISS

from mosqlimate_assistant import faiss_db
from mosqlimate_assistant.settings import ASKS_DB_PATH


def test_create_vector_store():
    vs = faiss_db.create_vector_store()

    assert isinstance(vs, FAISS)

    emb = vs.embedding_function.embed_query("hello")
    assert hasattr(vs.index, "d") and vs.index.d == len(emb)


def test_load_local_db():
    vector_store = faiss_db.load_local_db(ASKS_DB_PATH)
    assert isinstance(vector_store, FAISS)


# def test_save_and_load_local_db(tmp_path):
#     db_path = tmp_path / "test_db"

#     vs = faiss_db.create_vector_store()
#     asks = faiss_db.load_asks()
#     faiss_db.save_asks_local_db(vs, asks, str(db_path))

#     vs2 = faiss_db.load_local_db(str(db_path))

#     assert isinstance(vs2, FAISS)

#     assert len(vs2.index_to_docstore_id) == len(asks)


# def test_get_or_create_vector_db(tmp_path):
#     db_path = tmp_path / "or_create_db"

#     vs1 = faiss_db.get_or_create_vector_db(db_path=str(db_path))
#     assert isinstance(vs1, FAISS)

#     vs2 = faiss_db.get_or_create_vector_db(db_path=str(db_path))
#     assert isinstance(vs2, FAISS)

#     assert len(vs2.index_to_docstore_id) == len(vs1.index_to_docstore_id)


def test_load_asks():
    asks = faiss_db.load_asks()

    assert isinstance(asks, dict)
    assert len(asks) > 0
