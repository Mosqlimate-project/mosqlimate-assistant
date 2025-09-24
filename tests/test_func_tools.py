from mosqlimate_assistant import func_tools


def test_get_infodengue_data():
    result = func_tools.get_infodengue_data(
        disease="dengue",
        start="2023-01-01",
        end="2023-12-31",
        uf="SP",
        city="São Paulo",
    )

    assert "Consulta para a API do InfoDengue:" in result
    assert "URL da API:" in result
    assert "Parâmetros Utilizados:" in result
    assert "Exemplo de Código Python com mosqlient (Recomendado)" in result
    assert "disease=dengue" in result
    assert "start=2023-01-01" in result
    assert "end=2023-12-31" in result


def test_get_climate_data():
    result = func_tools.get_climate_data(
        start="2023-01-01", end="2023-12-31", uf="RJ"
    )

    assert "Consulta para a API de dados climáticos gerada:" in result
    assert "URL da API:" in result
    assert "Parâmetros Utilizados:" in result
    assert "Exemplo de Código Python com mosqlient (Recomendado)" in result
    assert "start=2023-01-01" in result
    assert "end=2023-12-31" in result


def test_get_mosquito_data():
    result = func_tools.get_mosquito_data(
        date_start="2024-01-01", date_end="2024-12-31", state="MG"
    )

    assert "Consulta para a API de dados de mosquito gerada:" in result
    assert "URL da API:" in result
    assert "Parâmetros Utilizados:" in result
    assert "Exemplo de Código Python com mosqlient (Recomendado)" in result
    assert "date_start=2024-01-01" in result


def test_get_episcanner_data():
    result = func_tools.get_episcanner_data(
        disease="dengue", uf="SP", year=2023
    )

    assert "Consulta para a API do EpiScanner gerada:" in result
    assert "URL da API:" in result
    assert "Parâmetros Utilizados:" in result
    assert "Exemplo de Código Python com mosqlient (Recomendado)" in result
    assert "disease=dengue" in result
    assert "uf=SP" in result
    assert "year=2023" in result


def test_tool_schemas_structure():
    schemas = func_tools.TOOL_SCHEMAS

    assert len(schemas) == 4

    for schema in schemas:
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
        assert "type" in schema["parameters"]
        assert "properties" in schema["parameters"]
        assert "required" in schema["parameters"]


def test_tool_functions_mapping():
    functions = func_tools.TOOL_FUNCTIONS

    assert "get_infodengue_data" in functions
    assert "get_climate_data" in functions
    assert "get_mosquito_data" in functions
    assert "get_episcanner_data" in functions

    assert callable(functions["get_infodengue_data"])
    assert callable(functions["get_climate_data"])
    assert callable(functions["get_mosquito_data"])
    assert callable(functions["get_episcanner_data"])


def test_infodengue_without_location():
    result = func_tools.get_infodengue_data(
        disease="zika", start="2023-06-01", end="2023-06-30"
    )

    assert "disease=zika" in result
    assert "start=2023-06-01" in result
    assert "end=2023-06-30" in result
    assert "geocode" not in result.lower()


def test_episcanner_without_year():
    result = func_tools.get_episcanner_data(disease="chikungunya", uf="MG")

    assert "disease=chik" in result
    assert "uf=MG" in result
    assert '"year"' not in result


def test_mosquito_minimal_params():
    result = func_tools.get_mosquito_data()

    assert "Consulta para a API de dados de mosquito gerada:" in result
    assert "URL da API:" in result
    assert "/mosquito" in result


def test_climate_with_pagination():
    result = func_tools.get_climate_data(
        start="2023-01-01", end="2023-01-31", page=2, per_page=50
    )

    assert "page=2" in result
    assert "per_page=50" in result
