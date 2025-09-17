import json
from typing import Any, Callable, Dict, List, Optional

from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.settings import BASE_URL_API, Diseases, UFs
from mosqlimate_assistant.utils import DOCS_KEYWORDS_MAP


def get_infodengue_data(
    disease: Diseases,
    start: str,
    end: str,
    uf: Optional[UFs] = None,
    city: Optional[str] = None,
    page: int = 1,
    per_page: int = 100,
) -> str:
    disease_map = {"chikungunya": "chik", "dengue": "dengue", "zika": "zika"}
    api_disease = disease_map.get(disease, disease)

    infodengue_link = DOCS_KEYWORDS_MAP.get("datastore_infodengue", {}).get(
        "link", ""
    )

    base_url = f"{BASE_URL_API}infodengue/"
    params = {
        "page": page,
        "per_page": min(per_page, 100),
        "disease": api_disease,
        "start": start,
        "end": end,
    }

    if uf:
        params["uf"] = uf
    if city and uf:
        geocode = get_municipality_code(city, uf)
        params["geocode"] = geocode

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"

    mosqlient_example = f"""import mosqlient

# Usando a biblioteca mosqlient (recomendado)
df = mosqlient.get_infodengue(
    api_key="SUA_CHAVE_API", # Substitua pela sua chave de API
    disease="{disease}",
    start_date="{start}",
    end_date="{end}\""""

    if uf:
        mosqlient_example += f",\n    uf='{uf}'"

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API do InfoDengue:

**URL da API:**
```
{full_url}
```

**Parâmetros Utilizados:**
```json
{json.dumps(params, indent=2, ensure_ascii=False)}
```

**Exemplo de Código (Python com mosqlient):**
```python
{mosqlient_example}
```

**Exemplo de Código (Python com requests):**
```python
import requests

url = "{full_url}"
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Substitua pela sua chave de API
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data['items'][:3])  # Exibe os primeiros 3 registros
else:
    print(f"Erro na requisição: {{response.status_code}}")
```
"""
    if infodengue_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial do InfoDengue: {infodengue_link}"""
    return response_text.strip()


def get_climate_data(
    start: str,
    end: str,
    uf: Optional[UFs] = None,
    city: Optional[str] = None,
    page: int = 1,
    per_page: int = 100,
) -> str:
    base_url = f"{BASE_URL_API}climate/"
    params = {
        "page": page,
        "per_page": min(per_page, 100),
        "start": start,
        "end": end,
    }

    climate_link = DOCS_KEYWORDS_MAP.get("datastore_climate", {}).get("link", "")

    if uf:
        params["uf"] = uf
    if city and uf:
        geocode = get_municipality_code(city, uf)
        params["geocode"] = geocode

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"

    mosqlient_example = f"""import mosqlient

# Usando a biblioteca mosqlient (recomendado)
df = mosqlient.get_climate(
    api_key="SUA_CHAVE_API", # Substitua pela sua chave de API
    start_date="{start}",
    end_date="{end}\""""

    if uf:
        mosqlient_example += f",\n    uf='{uf}'"
    if city and uf:
        geocode = get_municipality_code(city, uf)
        mosqlient_example += f",\n    geocode={geocode}"

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API de dados climáticos gerada:

**URL da API:**
```
{full_url}
```

**Parâmetros Utilizados:**
```json
{json.dumps(params, indent=2, ensure_ascii=False)}
```

**Exemplo de Código (Python com mosqlient):**
```python
{mosqlient_example}
```

**Exemplo de Código (Python com requests):**
```python
import requests

url = "{full_url}"
headers = {{"X-UID-Key": "SUA_CHAVE_API"}} # Substitua pela sua chave de API
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data['items'][:3])  # Exibe os primeiros 3 registros
else:
    print(f"Erro na requisição: {{response.status_code}}")
```
"""
    if climate_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial de dados climáticos: {climate_link}"""
    return response_text.strip()


def get_mosquito_data(
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    state: Optional[UFs] = None,
    municipality: Optional[str] = None,
    page: int = 1,
) -> str:
    base_url = f"{BASE_URL_API}mosquito/"
    params = {}

    mosquito_link = DOCS_KEYWORDS_MAP.get("datastore_mosquito", {}).get("link", "")

    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end
    if state:
        params["state"] = state
    if municipality:
        params["municipality"] = municipality
    if page > 1:
        params["page"] = str(page)

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}" if params else base_url

    mosqlient_example = f"""import mosqlient

# Usando a biblioteca mosqlient (recomendado)
df = mosqlient.get_mosquito(
    api_key="SUA_CHAVE_API",  # Substitua pela sua chave de API"""

    if date_start:
        mosqlient_example += f',\n    date_start="{date_start}"'
    if date_end:
        mosqlient_example += f',\n    date_end="{date_end}"'
    if state:
        mosqlient_example += f',\n    state="{state}"'
    if municipality:
        mosqlient_example += f',\n    municipality="{municipality}"'

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API de dados de mosquito gerada:

**URL da API:**
```
{full_url}
```

**Parâmetros Utilizados:**
```json
{json.dumps(params, indent=2, ensure_ascii=False) if params else "{}"}
```

**Exemplo de Código (Python com mosqlient):**
```python
{mosqlient_example}
```

**Exemplo de Código (Python com requests):**
```python
import requests

url = "{full_url}"
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Substitua pela sua chave de API
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data['items'][:3])  # Exibe os primeiros 3 registros
else:
    print(f"Erro na requisição: {{response.status_code}}")
```
"""
    if mosquito_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial do ContaOvos: {mosquito_link}"""
    return response_text.strip()


def get_episcanner_data(
    disease: Diseases,
    uf: UFs,
    year: Optional[int] = None,
) -> str:
    disease_map = {"chikungunya": "chik", "dengue": "dengue", "zika": "zika"}
    api_disease = disease_map.get(disease, disease)

    episcanner_link = DOCS_KEYWORDS_MAP.get("datastore_episcanner", {}).get(
        "link", ""
    )

    base_url = f"{BASE_URL_API}episcanner/"
    params = {
        "disease": api_disease,
        "uf": uf,
    }

    if year:
        params["year"] = str(year)

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"

    mosqlient_example = f"""import mosqlient

# Usando a biblioteca mosqlient (recomendado)
df = mosqlient.get_episcanner(
    api_key="SUA_CHAVE_API", # Substitua pela sua chave de API
    disease="{disease}",
    uf="{uf}\""""

    if year:
        mosqlient_example += f",\n    year={year}"

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API do EpiScanner gerada:

**URL da API:**
```
{full_url}
```

**Parâmetros Utilizados:**
```json
{json.dumps(params, indent=2, ensure_ascii=False)}
```

**Exemplo de Código (Python com mosqlient):**
```python
{mosqlient_example}
```

**Exemplo de Código (Python com requests):**
```python
import requests

url = "{full_url}"
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Substitua pela sua chave de API
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data['items'][:3])  # Exibe os primeiros 3 registros
else:
    print(f"Erro na requisição: {{response.status_code}}")
```
"""
    if episcanner_link:
        response_text += f"""\nPara mais detalhes, consulte a documentação oficial do EpiScanner: {episcanner_link}"""
    return response_text.strip()


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "get_infodengue_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados epidemiológicos do InfoDengue sobre doenças transmitidas por mosquitos (dengue, zika, chikungunya). Fornece dados semanais com estimativas de casos, níveis de alerta e variáveis climáticas.",
        "parameters": {
            "type": "object",
            "properties": {
                "disease": {
                    "type": "string",
                    "enum": ["dengue", "zika", "chikungunya"],
                    "description": "A doença a ser consultada: 'dengue', 'zika' ou 'chikungunya'",
                },
                "start": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de início da consulta (formato YYYY-MM-DD, semana epidemiológica)",
                },
                "end": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de término da consulta (formato YYYY-MM-DD, semana epidemiológica)",
                },
                "uf": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "A sigla do estado brasileiro (duas letras), ex: SP",
                },
                "city": {
                    "type": "string",
                    "description": "O nome do município",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Página a ser exibida (padrão: 1)",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Quantos itens por página, até 100 (padrão: 100)",
                },
            },
            "required": ["disease", "start", "end"],
        },
    },
    {
        "name": "get_climate_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados climáticos diários da API Mosqlimate. Fornece séries temporais de variáveis climáticas baseadas em dados de satélite ERA5 da Copernicus.",
        "parameters": {
            "type": "object",
            "properties": {
                "start": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de início da consulta (formato YYYY-MM-DD)",
                },
                "end": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "A data de término da consulta (formato YYYY-MM-DD)",
                },
                "uf": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "A sigla do estado brasileiro (duas letras), ex: SP",
                },
                "city": {
                    "type": "string",
                    "description": "O nome do município",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Página a ser exibida (padrão: 1)",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Quantos itens por página, até 100 (padrão: 100)",
                },
            },
            "required": ["start", "end"],
        },
    },
    {
        "name": "get_mosquito_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados do ContaOvos (monitoramento de mosquitos). Fornece dados de abundância de mosquitos baseados em armadilhas de ovos distribuídas pelo Brasil.",
        "parameters": {
            "type": "object",
            "properties": {
                "date_start": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Data de início no formato ISO (YYYY-MM-DD, opcional)",
                },
                "date_end": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Data de fim no formato ISO (YYYY-MM-DD, opcional)",
                },
                "state": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "Sigla do estado brasileiro (UF, opcional)",
                },
                "municipality": {
                    "type": "string",
                    "description": "Nome do município (opcional)",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Página a ser exibida (padrão: 1)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_episcanner_data",
        "description": "Gera uma URL de API e um exemplo de código para consultar dados do EpiScanner sobre parâmetros epidemiológicos e expansão de epidemias. Fornece estimativas de R0, taxa de transmissibilidade e duração de epidemias.",
        "parameters": {
            "type": "object",
            "properties": {
                "disease": {
                    "type": "string",
                    "enum": ["dengue", "zika", "chikungunya"],
                    "description": "A doença a ser consultada: 'dengue', 'zika' ou 'chikungunya'",
                },
                "uf": {
                    "type": "string",
                    "enum": [
                        "AC",
                        "AL",
                        "AP",
                        "AM",
                        "BA",
                        "CE",
                        "DF",
                        "ES",
                        "GO",
                        "MA",
                        "MT",
                        "MS",
                        "MG",
                        "PA",
                        "PB",
                        "PR",
                        "PE",
                        "PI",
                        "RJ",
                        "RN",
                        "RS",
                        "RO",
                        "RR",
                        "SC",
                        "SP",
                        "SE",
                        "TO",
                    ],
                    "description": "A sigla do estado brasileiro (duas letras), ex: SP",
                },
                "year": {
                    "type": "integer",
                    "minimum": 2010,
                    "maximum": 2030,
                    "description": "O ano específico para consulta (opcional, padrão: ano atual)",
                },
            },
            "required": ["disease", "uf"],
        },
    },
]


TOOL_FUNCTIONS: Dict[str, Callable[..., str]] = {
    "get_infodengue_data": get_infodengue_data,
    "get_climate_data": get_climate_data,
    "get_mosquito_data": get_mosquito_data,
    "get_episcanner_data": get_episcanner_data,
}
