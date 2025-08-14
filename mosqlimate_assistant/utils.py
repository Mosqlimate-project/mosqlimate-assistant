import json
import os
from typing import Any, Dict, List

from mosqlimate_assistant.docs_consumer import (
    get_mosqlimate_authors_docs,
    get_mosqlimate_climate_docs,
    get_mosqlimate_climate_weekly_docs,
    get_mosqlimate_data_platform_docs,
    get_mosqlimate_datastore_base_docs,
    get_mosqlimate_episcanner_docs,
    get_mosqlimate_infodengue_docs,
    get_mosqlimate_models_docs,
    get_mosqlimate_mosquito_docs,
    get_mosqlimate_ovicounter_docs,
    get_mosqlimate_post_models_docs,
    get_mosqlimate_post_predictions_docs,
    get_mosqlimate_predictions_docs,
    get_mosqlimate_project_docs,
    get_mosqlimate_registry_docs,
    get_mosqlimate_uid_key_docs,
)


def save_logs(logs: list[str], save_path: str = ".") -> None:
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    save_file = os.path.join(save_path, "prompt_logs.txt")
    with open(save_file, "a") as file:
        for log in logs:
            file.write(log)
            file.write("\n")
        file.write("\n\n")


def format_answer(answer: str) -> str:
    ans_dict = json.loads(answer)
    answer = "```json\n"
    answer += json.dumps(ans_dict, indent=2) + "\n```"

    return answer


# Mapeamento de documentações com palavras-chave e categorias
DOCS_KEYWORDS_MAP: Dict[str, Dict[str, Any]] = {
    "project_main": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Mosqlimate-project.github.io/refs/heads/main/pages/index.pt.md
        "link": "https://mosqlimate.org/pt/",
        "function": get_mosqlimate_project_docs,
        "keywords": [
            "o que é mosqlimate",
            "sobre o mosqlimate",
            "mosqlimate projeto",
            "descrição do projeto",
            "para que serve",
            "objetivo do projeto",
            "finalidade",
            "dengue",
            "zika",
            "chikungunya",
            "aedes aegypti",
            "arboviroses",
            "doenças transmitidas por mosquitos",
            "clima e doença",
            "mudanças climáticas",
            "brasil",
            "vigilância epidemiológica",
            "infodengue",
            "team",
            "equipe",
        ],
        "category": "project",
        "description": "Documentação principal do projeto Mosqlimate",
    },
    "project_ovicounter": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Mosqlimate-project.github.io/refs/heads/main/pages/egg-dataset.pt.md
        "link": "https://mosqlimate.org/pt/egg-dataset/",
        "function": get_mosqlimate_ovicounter_docs,
        "keywords": [
            "ovicounter",
            "dataset de ovos",
            "imagens de ovos",
            "contagem de ovos",
            "aedes aegypti ovos",
            "ovitrampa",
            "armadilha de ovos",
            "monitoramento de mosquitos",
            "dados de campo",
            "coleta de dados",
            "conta ovos",
            "como baixar dataset",
            "eggs dataset",
            "mosquito eggs dataset",
        ],
        "category": "ovicounter",
        "description": "Documentação do Ovicounter (dataset de ovos de mosquito)",
    },
    "data_platform": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/index.pt.md
        "link": "https://api.mosqlimate.org/docs/",
        "function": get_mosqlimate_data_platform_docs,
        "keywords": [
            "como usar a api",
            "modo de usar",
            "começar com mosqlimate",
            "api documentation",
            "datastore",
            "plataforma de dados",
            "model registry",
            "previsões",
            "forecasting",
            "modelos",
            "dados de doença",
            "dados climáticos",
            "como registrar modelo",
            "github",
            "conta na plataforma",
            "mosqlient",
            "python client",
            "dashboard",
            "comparar modelos",
        ],
        "category": "platform",
        "description": "Documentação da plataforma de dados",
    },
    "datastore_base": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/index.pt.md
        "link": "https://api.mosqlimate.org/docs/datastore/",
        "function": get_mosqlimate_datastore_base_docs,
        "keywords": [
            "datastore",
            "como acessar dados",
            "plataforma de dados",
            "dados disponíveis",
            "notificação de doenças",
            "séries temporais climáticas",
            "api endpoints",
            "dados epidemiológicos",
            "dados meteorológicos",
        ],
        "category": "datastore",
        "description": "Documentação base do datastore",
    },
    "registry_base": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/index.pt.md
        "link": "https://api.mosqlimate.org/docs/registry/",
        "function": get_mosqlimate_registry_docs,
        "keywords": [
            "registry",
            "repositório de modelos",
            "como registrar modelo",
            "model registry",
            "usuários registrados",
            "código no github",
            "metadados do modelo",
            "previsões",
            "forecasts",
            "dashboard de previsões",
            "comparar modelos",
            "upload de forecasts",
            "modelos open source",
            "machine learning",
            "modelos de previsão",
            "modelos estatísticos",
            "conta necessária",
        ],
        "category": "registry",
        "description": "Documentação do registry (repositório de modelos)",
    },
    "uid_key": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/uid-key.pt.md
        "link": "https://api.mosqlimate.org/docs/uid-key/",
        "function": get_mosqlimate_uid_key_docs,
        "keywords": [
            "api key",
            "chave da api",
            "como obter chave",
            "autenticação github",
            "x-uid-key",
            "perfil do usuário",
            "token",
            "autorização",
            "headers da requisição",
            "api demo",
            "authorize",
            "login",
            "acesso",
            "credenciais",
            "username",
        ],
        "category": "authentication",
        "description": "Documentação sobre chaves UID e autenticação",
    },
    "datastore_infodengue": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/infodengue.pt.md
        "link": "https://api.mosqlimate.org/docs/datastore/GET/infodengue/",
        "function": get_mosqlimate_infodengue_docs,
        "keywords": [
            "dados infodengue",
            "infodengue",
            "infodengue api",
            "infodengue dados",
            "dengue",
            "zika",
            "chikungunya",
            "dados de transmissão",
            "casos estimados",
            "semana epidemiológica",
            "alertas",
            "nível de alerta",
            "incidência",
            "transmissão",
            "municípios brasileiros",
            "temperatura",
            "umidade",
            "casos prováveis",
            "vigilância",
        ],
        "category": "datastore",
        "description": "Documentação do endpoint GET infodengue",
    },
    "datastore_episcanner": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/episcanner.pt.md
        "link": "https://api.mosqlimate.org/docs/datastore/GET/episcanner/",
        "function": get_mosqlimate_episcanner_docs,
        "keywords": [
            "episcanner",
            "scanner epidemiológico",
            "surtos de dengue",
            "dados de epidemias",
            "epidemiologia",
            "monitoramento",
            "monitoramento automático",
            "monitoramento epidemiológico",
            "detecção de surtos",
            "alertas automáticos",
            "vigilância",
            "scanneamento",
            "detecção precoce",
        ],
        "category": "datastore",
        "description": "Documentação do endpoint GET episcanner",
    },
    "datastore_climate": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/climate.pt.md
        "link": "https://api.mosqlimate.org/docs/datastore/GET/climate/",
        "function": get_mosqlimate_climate_docs,
        "keywords": [
            "dados climáticos",
            "temperatura diária",
            "precipitação",
            "umidade",
            "pressão atmosférica",
            "copernicus era5",
            "municípios brasileiros",
            "escala diária",
            "mínima máxima temperatura",
            "chuva",
            "tempo",
            "meteorologia",
            "clima brasil",
        ],
        "category": "datastore",
        "description": "Documentação do endpoint GET climate",
    },
    "datastore_climate_weekly": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/climate-weekly.pt.md
        "link": "https://api.mosqlimate.org/docs/datastore/GET/climate-weekly/",
        "function": get_mosqlimate_climate_weekly_docs,
        "keywords": [
            "dados climáticos semanais",
            "temperatura semanal",
            "precipitação semanal",
            "agregação semanal",
            "resumo semanal",
            "dados agrupados por semana",
            "médias semanais",
            "clima por semana",
            "meteorologia semanal",
        ],
        "category": "datastore",
        "description": "Documentação do endpoint GET climate weekly",
    },
    "datastore_mosquito": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/datastore/GET/mosquito.pt.md
        "link": "https://api.mosqlimate.org/docs/datastore/GET/mosquito/",
        "function": get_mosqlimate_mosquito_docs,
        "keywords": [
            "dados de mosquitos",
            "abundância de mosquitos",
            "contaovos",
            "ovitrampa",
            "contagem de ovos",
            "monitoramento de vetores",
            "monitoramento de agentes",
            "aedes aegypti",
            "ministério da saúde",
            "design de monitoramento",
            "latitude longitude",
            "municípios",
            "coleta de ovos",
            "dados entomológicos",
        ],
        "category": "datastore",
        "description": "Documentação do endpoint GET mosquito",
    },
    "registry_predictions_get": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/GET/predictions.pt.md
        "link": "https://api.mosqlimate.org/docs/registry/GET/predictions/",
        "function": get_mosqlimate_predictions_docs,
        "keywords": [
            "consultar previsões",
            "buscar predições",
            "previsões de modelos",
            "forecasts",
            "resultados de modelos",
            "predições por modelo",
            "autor das predições",
            "nível administrativo",
            "resolução temporal",
            "dia semana mês ano",
            "data da predição",
            "commit",
            "mosqlient",
            "python examples",
        ],
        "category": "registry",
        "description": "Documentação do endpoint GET predictions",
    },
    "registry_models_get": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/GET/models.pt.md
        "link": "https://api.mosqlimate.org/docs/registry/GET/models/",
        "function": get_mosqlimate_models_docs,
        "keywords": [
            "consultar modelos",
            "listar modelos",
            "buscar modelos",
            "repositório de modelos",
            "metadados do modelo",
            "versões do modelo",
            "autor do modelo",
            "instituição",
            "linguagem de implementação",
            "github repository",
            "modelo temporal",
            "modelo categórico",
            "machine learning models",
        ],
        "category": "registry",
        "description": "Documentação do endpoint GET models",
    },
    "registry_authors_get": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/GET/authors.pt.md
        "link": "https://api.mosqlimate.org/docs/registry/GET/authors/",
        "function": get_mosqlimate_authors_docs,
        "keywords": [
            "consultar autores",
            "lista de autores",
            "instituições",
            "contatos",
            "responsáveis pelos modelos",
            "criadores de modelos",
            "créditos",
            "quem desenvolveu",
        ],
        "category": "registry",
        "description": "Documentação do endpoint GET authors",
    },
    "registry_predictions_post": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/POST/predictions.pt.md
        "link": "https://api.mosqlimate.org/docs/registry/POST/predictions/",
        "function": get_mosqlimate_post_predictions_docs,
        "keywords": [
            "enviar previsões",
            "submeter predições",
            "upload de forecasts",
            "publicar resultados",
            "adicionar predições",
            "como enviar predições",
            "salvar forecasts",
            "contribuir com previsões",
            "inserir previsões",
            "post predictions",
            "envio de resultados",
        ],
        "category": "registry",
        "description": "Documentação do endpoint POST predictions",
    },
    "registry_models_post": {
        # Link: https://raw.githubusercontent.com/Mosqlimate-project/Data-platform/refs/heads/main/mkdocs/docs/registry/POST/models.pt.md
        "link": "https://api.mosqlimate.org/docs/registry/POST/models/",
        "function": get_mosqlimate_post_models_docs,
        "keywords": [
            "registrar modelo",
            "enviar modelo",
            "submeter modelo",
            "como adicionar modelo",
            "publicar modelo",
            "upload de modelo",
            "deploy do modelo",
            "contribuir com modelo",
            "adicionar ao registry",
            "deployment",
            "como registrar",
        ],
        "category": "registry",
        "description": "Documentação do endpoint POST models",
    },
}


DOCS_BLOCKS_MAP = {
    "project_intro_block": ["project_main", "data_platform", "datastore_base"],
    "uid_key_block": ["project_main", "data_platform", "uid_key"],
    "ovicounter_block": ["project_main", "project_ovicounter"],
    "infodengue_block": [
        "project_main",
        "data_platform",
        "datastore_infodengue",
    ],
    "climate_block": [
        "project_main",
        "data_platform",
        "datastore_climate",
    ],
    "climate_week_block": [
        "project_main",
        "data_platform",
        "datastore_climate_weekly",
    ],
    "mosquito_block": ["project_main", "data_platform", "datastore_mosquito"],
    "episcanner_block": [
        "project_main",
        "data_platform",
        "datastore_episcanner",
    ],
    "models_query_block": [
        "project_main",
        "registry_models_get",
        "registry_authors_get",
    ],
    "models_register_block": [
        "project_main",
        "registry_base",
        "registry_models_post",
    ],
    "predictions_query_block": ["project_main", "registry_predictions_get"],
    "predictions_submit_block": ["project_main", "registry_predictions_post"],
    "registry_overview_block": ["project_main", "registry_base"],
}


def get_formated_keywords_docs_map() -> dict:
    formatted_map = dict()
    for key, value in DOCS_KEYWORDS_MAP.items():
        keywords_list: List[str] = value["keywords"]
        formatted_map[key] = {
            "keywords": ", ".join(keywords_list),
            "category": value["category"],
            "description": value["description"],
        }
    return formatted_map
