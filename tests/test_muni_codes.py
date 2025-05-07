import pytest

from mosqlimate_assistant import muni_codes


def test_process_input():
    assert muni_codes.process_input(" AbC ") == "abc"
    assert muni_codes.process_input("São Paulo") == "são paulo"


def test_read_municipalities_returns_list():
    municipalities = muni_codes.read_municipalities()
    assert isinstance(municipalities, list)
    assert all(isinstance(m, dict) for m in municipalities)

    for m in municipalities:
        assert "Municipality" in m
        assert "UF" in m
        assert "Code" in m


def test_get_closest_match_simple():
    options = [
        {"Municipality": "abc", "UF": "XX", "Code": 1},
        {"Municipality": "abd", "UF": "YY", "Code": 2},
    ]
    match, dist = muni_codes.get_closest_match("abc", options)
    assert match["Code"] == 1
    assert dist == 0
    match2, dist2 = muni_codes.get_closest_match("abdk", options)
    assert match2["Code"] == 2
    assert dist2 == 1


def test_filter_by_uf_valid_and_invalid():
    municipalities = [
        {"Municipality": "a", "UF": "SP", "Code": 1},
        {"Municipality": "b", "UF": "RJ", "Code": 2},
    ]
    filtered = muni_codes.filter_by_uf(municipalities, "sp")
    assert filtered == [{"Municipality": "a", "UF": "SP", "Code": 1}]
    with pytest.raises(ValueError):
        muni_codes.filter_by_uf(municipalities, "XX")


def test_get_municipality_and_code_valid_and_invalid():
    name = "Abadia de Goiás"
    uf = "GO"
    expected_code = 5200050
    code = muni_codes.get_municipality_code(name, uf)
    print(f"Municipality code for {name} in {uf}: {code}")
    assert isinstance(code, int)
    assert code == expected_code

    with pytest.raises(RuntimeError):
        muni_codes.get_municipality_code("nonexistent", None)

    with pytest.raises(ValueError):
        muni_codes.get_municipality("xyznotfound", None)
