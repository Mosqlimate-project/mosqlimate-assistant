from pathlib import Path
from typing import List, Literal, Optional, Tuple

from mosqlimate_assistant.agent_cards import AgentCard
from mosqlimate_assistant.assistant import Assistant
from mosqlimate_assistant.document_consumer import (
    CSVLinkConsumer,
    DocumentManager,
)
from mosqlimate_assistant.embeddings import OllamaEmbeddingProvider
from mosqlimate_assistant.models import ChatMessage, ProviderType
from mosqlimate_assistant.prompts import (
    get_base_docs_prompt,
    get_coder_agent_prompt,
    get_imdc_agent_prompt,
)
from mosqlimate_assistant.vector_store import InMemoryVectorStore

_DATA_DIR = Path(__file__).parent / "data"
DOCS_CSV = str(_DATA_DIR / "docs_references.csv")
CODE_CSV = str(_DATA_DIR / "code_references.csv")
IMDC_CSV = str(_DATA_DIR / "imdc_references.csv")

DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"

SearchMode = Literal["unitary", "group", "total"]

DOCS_GROUPS: List[List[str]] = [
    [
        "project_main",
        "uid_key",
        "datastore_base",
        "data_platform",
        "project_ovicounter",
    ],
    [
        "project_main",
        "datastore_base",
        "datastore_infodengue",
        "datastore_episcanner",
        "datastore_climate",
        "datastore_climate_weekly",
        "datastore_mosquito",
    ],
    [
        "project_main",
        "registry_base",
        "registry_models_get",
        "registry_models_post",
        "registry_predictions_get",
        "registry_predictions_post",
        "vis_dashboard_how_to_use",
        "vis_dashboard_scores",
        "vis_dashboard_details",
    ],
]

CODE_GROUPS: List[List[str]] = [
    [
        "Overview",
        "Tutorial - Datastore",
        "Reference - Infodengue data",
        "Reference - Climate data",
    ],
    [
        "Overview",
        "Tutorial - Registry",
        "Reference - Get, post and delete models",
        "Reference - Get, post and delete predictions",
    ],
    [
        "Overview",
        "Tutorial - Using from R",
        "Tutorial - Model Scoring",
        "Reference - Score",
    ],
    [
        "Overview",
        "Tutorial - Simple forecast model",
        "Tutorial - Ensemble predictions",
        "Reference - Baseline Arima",
        "Reference - Ensemble",
        "Reference - Prediction optimize",
    ],
]

IMDC_GROUPS: List[List[str]] = [
    ["home", "about", "organize", "registration"],
    ["home", "sprint-2025", "instructions-2025", "registration"],
    ["home", "about", "data-2025", "sprint-2025", "results-2025"],
]

DOCS_FALLBACK_THRESHOLD = 0.75
CODE_FALLBACK_THRESHOLD = 0.5
IMDC_FALLBACK_THRESHOLD = 0.5


def build_mosqlimate_assistant(
    google_api_key: str,
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_base_url: Optional[str] = None,
    docs_search_mode: SearchMode = "group",
    code_search_mode: SearchMode = "group",
    imdc_search_mode: SearchMode = "group",
    docs_named_groups: Optional[List[List[str]]] = None,
    code_named_groups: Optional[List[List[str]]] = None,
    imdc_named_groups: Optional[List[List[str]]] = None,
    group_key: str = "id",
    id_key: str = "name",
    **kwargs,
) -> Tuple[
    Assistant, InMemoryVectorStore, InMemoryVectorStore, InMemoryVectorStore
]:
    _docs_groups = docs_named_groups or DOCS_GROUPS
    _code_groups = code_named_groups or CODE_GROUPS
    _imdc_groups = imdc_named_groups or IMDC_GROUPS

    embedding_provider = OllamaEmbeddingProvider(
        model=embedding_model,
        base_url=ollama_base_url,
    )

    docs_store = InMemoryVectorStore(embedding_provider)
    code_store = InMemoryVectorStore(embedding_provider)
    imdc_store = InMemoryVectorStore(embedding_provider)

    docs_manager = DocumentManager(docs_store)
    docs_manager.add_consumer(CSVLinkConsumer(DOCS_CSV, "markdown_link"))
    docs_manager.fetch_and_index_all(collections=["docs"], id_key=id_key)

    code_manager = DocumentManager(code_store)
    code_manager.add_consumer(CSVLinkConsumer(CODE_CSV, "markdown_link"))
    code_manager.fetch_and_index_all(collections=["code"], id_key=id_key)

    imdc_manager = DocumentManager(imdc_store)
    imdc_manager.add_consumer(CSVLinkConsumer(IMDC_CSV, "markdown_link"))
    imdc_manager.fetch_and_index_all(collections=["imdc"], id_key=id_key)

    asst = Assistant(
        provider_type=ProviderType.GEMINI,
        provider_config={
            "api_key": google_api_key,
            "model": gemini_model,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        },
        embedding_provider=embedding_provider,
    )

    code_card = AgentCard(
        name="code_agent",
        description="Especialista em gerar exemplos de código do mosqlient",
        search_mode=code_search_mode if _code_groups else "unitary",
        named_groups=_code_groups,
        group_key=group_key,
        target_groups=["code"],
        fallback_docs="code",
        fallback_threshold=CODE_FALLBACK_THRESHOLD,
    )
    code_card.set_prompt_function(get_coder_agent_prompt)
    asst.register_agent("code_agent", code_card, vector_store=code_store)

    imdc_card = AgentCard(
        name="imdc_agent",
        description="Especialista no Infodengue-Mosqlimate Dengue Challenge (IMDC/Sprint de Dengue)",
        search_mode=imdc_search_mode if _imdc_groups else "unitary",
        named_groups=_imdc_groups,
        group_key=group_key,
        target_groups=["imdc"],
        fallback_docs="imdc",
        fallback_threshold=IMDC_FALLBACK_THRESHOLD,
    )
    imdc_card.set_prompt_function(get_imdc_agent_prompt)
    asst.register_agent("imdc_agent", imdc_card, vector_store=imdc_store)

    docs_card = AgentCard(
        name="docs_agent",
        description="Especialista em documentação da plataforma Mosqlimate",
        search_mode=docs_search_mode,
        named_groups=_docs_groups if docs_search_mode == "group" else [],
        group_key=group_key,
        target_groups=["docs"],
        fallback_docs="docs",
        fallback_threshold=DOCS_FALLBACK_THRESHOLD,
        tools=[code_card.agent_to_tool, imdc_card.agent_to_tool],
    )
    docs_card.set_prompt_function(get_base_docs_prompt)
    asst.register_agent(
        "docs_agent", docs_card, vector_store=docs_store, is_default=True
    )

    return asst, docs_store, code_store, imdc_store


def docs_pipeline(
    question: str,
    google_api_key: str,
    search_mode: SearchMode = "group",
    docs_named_groups: Optional[List[List[str]]] = None,
    code_named_groups: Optional[List[List[str]]] = None,
    imdc_named_groups: Optional[List[List[str]]] = None,
    group_key: str = "id",
    id_key: str = "name",
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_base_url: Optional[str] = None,
    message_history: Optional[List[ChatMessage]] = None,
    **kwargs,
) -> str:
    asst, _, _, _ = build_mosqlimate_assistant(
        google_api_key=google_api_key,
        gemini_model=gemini_model,
        embedding_model=embedding_model,
        ollama_base_url=ollama_base_url,
        docs_search_mode=search_mode,
        docs_named_groups=docs_named_groups,
        code_named_groups=code_named_groups,
        imdc_named_groups=imdc_named_groups,
        group_key=group_key,
        id_key=id_key,
        **kwargs,
    )
    result = asst.query(
        question, agent_name="docs_agent", message_history=message_history
    )
    return result["content"]


def assistant_pipeline(
    question: str,
    google_api_key: str,
    message_history: Optional[List[ChatMessage]] = None,
    **kwargs,
) -> str:
    return docs_pipeline(
        question=question,
        google_api_key=google_api_key,
        message_history=message_history,
        **kwargs,
    )
