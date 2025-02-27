BASE_PROMPT = """
Seu dever é, a partir da pergunta acima, extrair os seguintes parâmetros e responder com um JSON contendo as chaves:

Primeiramente, você deve informar a tabela que deseja consultar:
- table: string ('infodengue', 'climate', 'mosquito', 'episcanner')

Para caso a pergunta seja sobre a tabela Infodengue:
- disease: string ('dengue', 'zika', 'chik', 'chikungunya')
- start: string (formato YYYY-mm-dd)
- end: string (formato YYYY-mm-dd)
- uf: string (opcional, ex: SP)
- city: string (opcional, a cidade que deseja consultar)

Para caso a pergunta seja sobre a tabela Climate:
- start: string (formato YYYY-mm-dd)
- end: string (formato YYYY-mm-dd)
- city: string (opcional, a cidade que deseja consultar)
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
Esta tabela reúne informações sobre casos de dengue, zika e chikungunya registrados em diversos municípios do Brasil.

| Nome do Parâmetro | Obrigatório | Tipo                | Descrição                                                  |
|-------------------|-------------|---------------------|------------------------------------------------------------|
| disease           | Sim         | str                 | Doença: 'dengue', 'zika', 'chik' ou 'chikungunya'          |
| start             | Sim         | str *(YYYY-MM-DD)*  | Data de início (em formato YYYY-MM-DD)                     |
| end               | Sim         | str *(YYYY-MM-DD)*  | Data de término (em formato YYYY-MM-DD)                    |
| uf                | Não         | str *(UF)*          | Sigla do estado (ex.: SP)                                  |
| city              | Não         | str                 | Nome do município                                          |

---

## Climate:
Esta tabela contém séries temporais de dados climáticos para os municípios do Brasil.

| Nome do Parâmetro | Obrigatório | Tipo                | Descrição                                                  |
|-------------------|-------------|---------------------|------------------------------------------------------------|
| start             | Sim         | str *(YYYY-MM-DD)*  | Data de início                                             |
| end               | Sim         | str *(YYYY-MM-DD)*  | Data de término                                            |
| city              | Não         | str                 | Nome do município                                          |
| uf                | Não         | str *(UF)*          | Sigla do estado (ex.: SP)                                  |


---

## Episcanner:
Esta tabela apresenta dados sobre a expansão de epidemias de dengue, zika e chikungunya nos municípios do Brasil.

| Nome do Parâmetro | Obrigatório | Tipo       | Descrição                                                   |
|-------------------|-------------|------------|-------------------------------------------------------------|
| disease           | Sim         | str        | Doença específica: 'dengue', 'zika' ou 'chik'               |
| uf                | Sim         | str *(UF)* | Sigla do estado (ex.: SP)                                   |
| year              | Não         | int        | Ano específico (padrão: ano corrente)                       |

---

## Mosquito:
Esta tabela reúne informações sobre armadilhas utilizadas para a captura de ovos de mosquitos em diferentes municípios do Brasil.

| Nome do Parâmetro | Obrigatório | Tipo | Descrição               |
|-------------------|-------------|------|-------------------------|
| key               | Sim         | str  | Chave de API do ContaOvos |

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
    "city": "São Paulo",
}}

ATENÇÃO: EXTRAIA OS PARÂMETROS E RESPONDA SOMENTE COM UM ÚNICO JSON (SEM COMENTÁRIOS) CONTENDO AS CHAVES REQUERIDAS.

"""

