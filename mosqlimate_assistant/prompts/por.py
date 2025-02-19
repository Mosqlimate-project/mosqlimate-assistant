BASE_PROMPT = """
Seu dever é, a partir da pergunta acima, extrair os seguintes parâmetros e responder com um JSON contendo as chaves:

Primeiramente, você deve informar a tabela que deseja consultar:
- table: string ('infodengue', 'climate', 'mosquito', 'episcanner')

Para caso a pergunta seja sobre a tabela Infodengue:
- disease: string ('dengue', 'zika', 'chik', 'chikungunya')
- start: string (formato YYYY-mm-dd)
- end: string (formato YYYY-mm-dd)
- uf: string (opcional, ex: SP)
- geocode: inteiro (opcional)

Para caso a pergunta seja sobre a tabela Climate:
- start: string (formato YYYY-mm-dd)
- end: string (formato YYYY-mm-dd)
- geocode: inteiro (opcional)
- uf: string (opcional, ex: SP)

Para caso a pergunta seja sobre a tabela Mosquito:
- key: string (ContaOvos API key)

Para caso a pergunta seja sobre a tabela Episcanner:
- disease: string ('dengue', 'zika', 'chik')
- uf: string (ex: SP)
- year: inteiro (opcional)

"""


TABLE_PROMPT = """
## Infodengue:
Esta tabela contém informações sobre casos de dengue, zika e chikungunya de diversos municípios do Brasil.

| Parameter name | Required | Type                | Description |
|---------------|----------|---------------------|-------------|
| disease      | yes      | str                 | Dengue, Zika or Chik[ungunya] |
| start        | yes      | str *(YYYY-mm-dd)*  | Start date (epidemiological week) |
| end          | yes      | str *(YYYY-mm-dd)*  | End date (epidemiological week) |
| uf           | no       | str *(UF)*          | Two letters Brazilian state abbreviation. E.g: SP |
| geocode      | no       | int                 | [IBGE's](https://www.ibge.gov.br/explica/codigos-dos-municipios.php) municipality code |

---

## Climate
Esta tabela contém informações sobre séries temporais de clima de todos os municípios do Brasil.

| Parameter name | Required | Type               | Description |
|---------------|----------|--------------------|-------------|
| start        | yes      | str *(YYYY-mm-dd)* | Start date |
| end          | yes      | str *(YYYY-mm-dd)* | End date |
| geocode      | no       | int                | [IBGE's](https://www.ibge.gov.br/explica/codigos-dos-municipios.php) municipality code |
| uf           | no       | str *(UF)*         | Two-letter Brazilian state abbreviation. E.g.: SP |

---

## Mosquito
Esta tabela contém informações sobre armadilhas para capturar ovos de mosquitos em diversos municípios do Brasil.

| Parameter name | Required | Type | Description           |
|---------------|----------|------|-----------------------|
| key          | yes      | str  | ContaOvos API key    |

---

## Episcanner
Esta tabela contém informações sobre a expansão de epidemias de dengue, zika e chikungunya em diversos municípios do Brasil.

| Parameter name | Required | Type       | Description |
|---------------|----------|------------|-------------|
| disease      | yes      | str        | Specific disease. Options: dengue, zika, chik |
| uf          | yes      | str *(UF)* | Two-letter Brazilian state abbreviation. E.g.: SP |
| year        | no       | int        | Specific year. Default: current year |

"""


UF_PROMPT = """
Entre os uf válidos estão:
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO"

"""

EXAMPLE_PROMPT = """

Exemplo de resposta para dados da dengue em São Paulo de 2022-12-30 a 2023-12-30:
{{
    "table": "infodengue",
    "disease": "dengue",
    "start": "2022-12-30",
    "end": "2023-12-30",
    "uf": "SP",
    "geocode": None,
}}

ATENÇÃO: EXTRAIA OS PARÂMETROS E RESPONDA SOMENTE COM UM JSON (SEM COMENTÁRIOS) CONTENDO AS CHAVES REQUERIDAS.

"""

