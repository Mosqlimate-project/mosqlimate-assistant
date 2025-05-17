import json

from mosqlimate_assistant import docs_consumer as docs


def __format_table_parameters() -> str:
    result = ""
    __FULL_PATHS = docs.get_mosqlimate_api_paths()
    __DATA_STORE_KEYS = [
        k for k in list(__FULL_PATHS.keys()) if "datastore" in k
    ]

    __INFODENGUE_KEY = [k for k in __DATA_STORE_KEYS if "infodengue" in k][0]
    __CLIMATE_KEY = [
        k for k in __DATA_STORE_KEYS if "climate" in k and "weekly" not in k
    ][0]
    __EPISCANNER_KEY = [k for k in __DATA_STORE_KEYS if "episcanner" in k][0]
    __MOSQUITO_KEY = [k for k in __DATA_STORE_KEYS if "mosquito" in k][0]

    __INFODENGUE_PARAMETERS = docs.format_api_parameters(
        __FULL_PATHS[__INFODENGUE_KEY]["get"]
    )
    __CLIMATE_PARAMETERS = docs.format_api_parameters(
        __FULL_PATHS[__CLIMATE_KEY]["get"]
    )
    __EPISCANNER_PARAMETERS = docs.format_api_parameters(
        __FULL_PATHS[__EPISCANNER_KEY]["get"]
    )
    __MOSQUITO_PARAMETERS = docs.format_api_parameters(
        __FULL_PATHS[__MOSQUITO_KEY]["get"]
    )

    result += "## Infodengue:\n"
    result += "Esta tabela reúne informações sobre casos de dengue, zika e chikungunya registrados em diversos municípios do Brasil.\n\n"
    result += json.dumps(__INFODENGUE_PARAMETERS)
    result += "\n\n"
    result += "## Climate:\n"
    result += "Esta tabela contém séries temporais de dados climáticos para os municípios do Brasil.\n"
    result += json.dumps(__CLIMATE_PARAMETERS)
    result += "\n\n"
    result += "## Episcanner:\n"
    result += "Esta tabela apresenta dados sobre a expansão de epidemias de dengue, zika e chikungunya nos estados do Brasil.\n"
    result += "**USE ESTA TABELA APENAS QUANDO O USUÁRIO ESPECIFICAR DADOS EPIDÊMICOS**\n\n"
    result += json.dumps(__EPISCANNER_PARAMETERS)
    result += "\n\n"
    result += "## Mosquito:\n"
    result += "Esta tabela reúne informações sobre armadilhas utilizadas para a captura de ovos de mosquitos em diferentes municípios do Brasil.\n"
    result += json.dumps(__MOSQUITO_PARAMETERS)
    result += "\n\n"

    return result


BASE_PROMPT = """Você é um assistente de pesquisa de dados da api do Mosqlimate.
Seu dever é, a partir da pergunta do usuário fornecida em linguagem natural, extrair os parâmetros necessários para consultar alguma das tabelas disponíveis: 'infodengue', 'climate', 'mosquito' ou 'episcanner'.

**Instruções Gerais:**
- Interprete a pergunta do usuário para identificar a tabela e os parâmetros relevantes.
- Você deve retornar um JSON válido com pelo menos todos os parâmetros obrigatórios da tabela selecionada.
- Se o usuário fornecer o nome completo de um estado (ex.: "São Paulo"), converta para a sigla correspondente (ex.: "SP").
- As datas devem ser retornadas no formato YYYY-MM-DD.
- SE O USUÁRIO MENCIONAR UMA CIDADE, ADICIONE O ESTADO (UF).
- SE O USUÁRIO MENCIONAR APENAS O ESTADO (UF), NÃO ADICIONE A CIDADE.
- SE O USUÁRIO NÃO MENCIONAR NEM CIDADE, NEM ESTADO, NÃO ADICIONE NENHUM DOS DOIS.
- Responda SOMENTE com um JSON válido contendo as chaves específicas para a tabela selecionada, sem comentários ou texto adicional.
"""


TABLE_PROMPT = "**Detalhes das Tabelas:**\n\n"
TABLE_PROMPT += __format_table_parameters().replace("{", "{{").replace("}", "}}")


UF_PROMPT = """
**Unidades Federativas (UF) Válidas:**
- "Acre": "AC",
- "Alagoas": "AL",
- "Amapá": "AP",
- "Amazonas": "AM",
- "Bahia": "BA",
- "Ceará": "CE",
- "Distrito Federal": "DF",
- "Espírito Santo": "ES",
- "Goiás": "GO",
- "Maranhão": "MA",
- "Mato Grosso": "MT",
- "Mato Grosso do Sul": "MS",
- "Minas Gerais": "MG",
- "Pará": "PA",
- "Paraíba": "PB",
- "Paraná": "PR",
- "Pernambuco": "PE",
- "Piauí": "PI",
- "Rio de Janeiro": "RJ",
- "Rio Grande do Norte": "RN",
- "Rio Grande do Sul": "RS",
- "Rondônia": "RO",
- "Roraima": "RR",
- "Santa Catarina": "SC",
- "São Paulo": "SP",
- "Sergipe": "SE",
- "Tocantins": "TO"
"""


EXAMPLE_PROMPT = """
**Exemplos:**

Exemplo de resposta para "Quero casos de dengue na cidade de São Paulo no ano de 2023":
```json
{
  "table": "infodengue",
  "disease": "dengue",
  "start": "2023-01-01",
  "end": "2023-12-31",
  "uf": "SP",
  "city": "São Paulo"
}
```

Exemplo de resposta para "Dados climáticos de Porto Alegre em 2022":
```json
{
  "table": "climate",
  "start": "2022-01-01",
  "end": "2022-12-31",
  "city": "Porto Alegre",
  "uf": "RS"
}
```

Exemplo de resposta para "Quero dados sobre a expansão da dengue no Rio de Janeiro em 2021":
```json
{
  "table": "episcanner",
  "disease": "dengue",
  "uf": "RJ",
  "year": 2021
}
```
"""


EXAMPLES_LIST = [
    {
        "question": "Quero casos de dengue na cidade de São Paulo no ano de 2023",
        "answer": """```json
{{
  "table": "infodengue",
  "disease": "dengue",
  "start": "2023-01-01",
  "end": "2023-12-31",
  "uf": "SP",
  "city": "São Paulo"
}}
```""",
    },
    {
        "question": "Dados climáticos de Porto Alegre em 2022",
        "answer": """```json
{{
  "table": "climate",
  "start": "2022-01-01",
  "end": "2022-12-31",
  "city": "Porto Alegre",
  "uf": "RS"
}}
```""",
    },
    {
        "question": "Quero dados sobre a expansão da dengue no Rio de Janeiro em 2021",
        "answer": """```json
{{
  "table": "episcanner",
  "disease": "dengue",
  "uf": "RJ",
  "year": 2021
}}
```""",
    },
]
