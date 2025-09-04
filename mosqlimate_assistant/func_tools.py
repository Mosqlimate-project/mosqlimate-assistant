import json
from typing import Any, Callable, Dict, List, Optional

from mosqlimate_assistant.muni_codes import get_municipality_code
from mosqlimate_assistant.settings import BASE_URL_API, Diseases, UFs


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
    api_key=api_key,
    disease="{disease}",
    start_date="{start}",
    end_date="{end}\""""

    if uf:
        mosqlient_example += f",\n    uf='{uf}'"

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API do InfoDengue gerada com sucesso.

**Sobre os dados**: Dados epidemiológicos semanais do projeto InfoDengue, incluindo estimativas de casos, níveis de alerta, taxas de transmissão (Rt) e variáveis climáticas para municípios brasileiros.

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
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Necessário para autenticação
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    items = data['items']  # Dados principais
    pagination = data['pagination']  # Info de paginação
    print(f"Total de itens: {{pagination['total_items']}}")
    print(f"Páginas disponíveis: {{pagination['total_pages']}}")
else:
    print(f"Erro na requisição: {{response.status_code}}")
```

**Campos retornados**: data_iniSE, SE, casos_est, casos_est_min, casos_est_max, casos, municipio_geocodigo, p_rt1, p_inc100k, nivel, Rt, municipio_nome, pop, receptivo, transmissao, nivel_inc, umidmax, umidmed, umidmin, tempmax, tempmed, tempmin, casprov, casprov_est, casconf, entre outros.
"""
    return response_text.strip()


def get_climate_data(
    start: str,
    end: str,
    uf: Optional[UFs] = None,
    city: Optional[str] = None,
    page: int = 1,
    per_page: int = 100,
) -> str:
    """
    Gera uma URL de API e um exemplo de código para consultar dados climáticos.

    Este endpoint fornece séries temporais diárias de variáveis climáticas extraídas
    dos dados de reanálise ERA5 da Copernicus para todos os municípios brasileiros.

    Args:
        start: A data de início da consulta (formato YYYY-MM-DD).
        end: A data de término da consulta (formato YYYY-MM-DD).
        uf: A sigla do estado brasileiro (opcional).
        city: O nome do município (opcional).
        page: Página a ser exibida (padrão: 1).
        per_page: Quantos itens por página, até 100 (padrão: 100).

    Returns:
        String estruturada com URL da API, parâmetros e exemplo de código.
    """
    base_url = f"{BASE_URL_API}climate/"
    params = {
        "page": page,
        "per_page": min(per_page, 100),
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
df = mosqlient.get_climate(
    api_key=api_key,
    start_date="{start}",
    end_date="{end}\""""

    if uf:
        mosqlient_example += f",\n    uf='{uf}'"
    if city and uf:
        geocode = get_municipality_code(city, uf)
        mosqlient_example += f",\n    geocode={geocode}"

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API de dados climáticos gerada com sucesso.

**Sobre os dados**: Séries temporais diárias de variáveis climáticas baseadas em dados de satélite ERA5 da Copernicus, processados e agregados no nível municipal brasileiro.

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
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Necessário para autenticação
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    items = data['items']  # Dados principais
    pagination = data['pagination']  # Info de paginação
    print(f"Total de itens: {{pagination['total_items']}}")
    print(f"Páginas disponíveis: {{pagination['total_pages']}}")
else:
    print(f"Erro na requisição: {{response.status_code}}")
```

**Campos retornados**: date, geocodigo, temp_min, temp_med, temp_max, precip_min, precip_med, precip_max, precip_tot, pressao_min, pressao_med, pressao_max, umid_min, umid_med, umid_max.
"""
    return response_text.strip()


def get_mosquito_data(
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    state: Optional[UFs] = None,
    municipality: Optional[str] = None,
    page: int = 1,
) -> str:
    """
    Gera uma URL de API e um exemplo de código para consultar dados do ContaOvos (mosquito).

    Este endpoint fornece dados de abundância de mosquitos baseados em armadilhas
    de ovos distribuídas pelo Brasil conforme protocolo do Ministério da Saúde.

    Args:
        date_start: Data de início no formato ISO (YYYY-MM-DD, opcional).
        date_end: Data de fim no formato ISO (YYYY-MM-DD, opcional).
        state: Sigla do estado brasileiro (UF, opcional).
        municipality: Nome do município (opcional).
        page: Página a ser exibida (padrão: 1).

    Returns:
        String estruturada com URL da API, parâmetros e exemplo de código.
    """
    base_url = f"{BASE_URL_API}mosquito"
    params = {}

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

    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{base_url}?{query_string}"
    else:
        full_url = base_url

    mosqlient_example = "import mosqlient\n\n# Usando a biblioteca mosqlient (recomendado)\ndf = mosqlient.get_mosquito(\n    api_key=api_key"

    if date_start:
        mosqlient_example += f',\n    date_start="{date_start}"'
    if date_end:
        mosqlient_example += f',\n    date_end="{date_end}"'
    if state:
        mosqlient_example += f',\n    state="{state}"'
    if municipality:
        mosqlient_example += f',\n    municipality="{municipality}"'

    mosqlient_example += "\n)\nprint(df.head())"

    all_pages_example = """import pandas as pd
import mosqlient

# Para buscar todas as páginas (este endpoint requer loop manual)
params = dict(
    api_key=api_key"""

    if date_start:
        all_pages_example += f',\n    date_start="{date_start}"'
    if date_end:
        all_pages_example += f',\n    date_end="{date_end}"'
    if state:
        all_pages_example += f',\n    state="{state}"'
    if municipality:
        all_pages_example += f',\n    municipality="{municipality}"'

    all_pages_example += """
)

results = []
page = 1
while True:
    df = mosqlient.get_mosquito(**params, page=page)
    if df.empty:
        break
    results.append(df)
    page += 1

result = pd.concat(results) if results else pd.DataFrame()
print(f"Total de registros: {len(result)}")"""

    response_text = f"""
Consulta para a API de dados de mosquito (ContaOvos) gerada com sucesso.

**Sobre os dados**: Dados de abundância de mosquitos do projeto ContaOvos, baseados em armadilhas de ovos distribuídas pelo Brasil. Inclui contagem de ovos, localização das armadilhas e informações temporais.

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

**Exemplo para buscar todas as páginas:**
```python
{all_pages_example}
```

**Exemplo de Código (Python com requests):**
```python
import requests

url = "{full_url}"
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Necessário para autenticação
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"Dados de mosquitos obtidos com sucesso!")
    print(f"Primeiros registros: {{data[:3] if isinstance(data, list) else data}}")
else:
    print(f"Erro na requisição: {{response.status_code}}")
```

**Campos retornados**: counting_id, date, date_collect, eggs, latitude, longitude, municipality, municipality_code, ovitrap_id, state_code, state_name, time, week, year.

**Nota**: Este endpoint não suporta busca assíncrona de todas as páginas. Use um loop while para navegar por todas as páginas conforme exemplo acima.
"""
    return response_text.strip()


def get_episcanner_data(
    disease: Diseases,
    uf: UFs,
    year: Optional[int] = None,
) -> str:
    """
    Gera uma URL de API e um exemplo de código para consultar dados do EpiScanner.

    Este endpoint fornece estimativas de parâmetros epidemiológicos em tempo real
    para cada cidade e ano no Brasil, com foco em Dengue, Zika e Chikungunya.

    Args:
        disease: A doença a ser consultada ('dengue', 'zika', 'chik').
        uf: A sigla do estado brasileiro.
        year: O ano específico (opcional, padrão: ano atual).

    Returns:
        String estruturada com URL da API, parâmetros e exemplo de código.
    """
    disease_map = {"chikungunya": "chik", "dengue": "dengue", "zika": "zika"}
    api_disease = disease_map.get(disease, disease)

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
    api_key=api_key,
    disease="{disease}",
    uf="{uf}\""""

    if year:
        mosqlient_example += f",\n    year={year}"

    mosqlient_example += "\n)\nprint(df.head())"

    response_text = f"""
Consulta para a API do EpiScanner gerada com sucesso.

**Sobre os dados**: Estimativas de parâmetros epidemiológicos do Epi-Scanner para análise de expansão de epidemias. Inclui taxa de transmissibilidade (beta), número reprodutivo básico (R0), semana do pico epidêmico e duração da epidemia.

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
headers = {{"X-UID-Key": "SUA_CHAVE_API"}}  # Necessário para autenticação
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"Dados do EpiScanner obtidos com sucesso!")
    print(f"Total de municípios: {{len(data)}}")
    # Dados são retornados diretamente como lista, sem paginação
else:
    print(f"Erro na requisição: {{response.status_code}}")
```

**Campos retornados**: disease, CID10, year, geocode, muni_name, peak_week, beta, gamma, R0, total_cases, alpha, sum_res, ep_ini, ep_end, ep_dur.

**Nota**: Este endpoint NÃO usa paginação. Todos os dados são retornados em uma única resposta.
"""
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
