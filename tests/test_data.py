import langchain_community.vectorstores
import os

def test_load_municipalities():
    from mosqlimate_assistant.utils import read_municipalities
    municipalities = read_municipalities()
    assert isinstance(municipalities, list)

def test_check_municipality():
    from mosqlimate_assistant.utils import read_municipalities
    municipalities = read_municipalities()
    for m in municipalities:
        assert isinstance(m, dict)
        assert "Municipality" in m
        assert "UF" in m
        assert "Code" in m

# def test_create_vector_store():
#     from mosqlimate_assistant.input_validator import create_vector_store
#     vector_store = create_vector_store()
#     print(type(vector_store))
#     assert isinstance(vector_store, langchain_community.vectorstores.FAISS)

def test_load_local_db():
    from mosqlimate_assistant.input_validator import load_local_db
    current_dir = os.path.dirname(__file__)
    print(current_dir)
    vector_store = load_local_db(current_dir + "/../data/asks_db")
    assert isinstance(vector_store, langchain_community.vectorstores.FAISS)

def test_load_asks():
    from mosqlimate_assistant.input_validator import load_asks
    asks = load_asks()
    assert isinstance(asks, dict)


