"""Pre-configured pipelines for the Mosqlimate AI Assistant.

Provides ready-to-use functions that build a fully wired multi-agent
assistant with documentation, code, and IMDC agents — each backed by
its own vector store and reference CSV.

Functions:
    build_mosqlimate_assistant: Constructs the full ``Assistant`` with
        three specialized agents and their vector stores.
    docs_pipeline: One-call convenience — builds the assistant and
        queries the docs agent.
    assistant_pipeline: Thin wrapper around ``docs_pipeline`` with
        sensible defaults.

Module-level constants define the default document groups, fallback
thresholds, and CSV paths used by the pipelines.
"""

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
DOCS_EN_CSV = str(_DATA_DIR / "docs_en_references.csv")
CODE_CSV = str(_DATA_DIR / "code_references.csv")
IMDC_CSV = str(_DATA_DIR / "imdc_references.csv")

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
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
        "datastore_infodengue",
        "datastore_episcanner",
        "datastore_climate",
        "datastore_climate_weekly",
        "datastore_mosquito",
    ],
    [
        "registry_base",
        "registry_models_get",
        "registry_models_post",
        "registry_predictions_get",
        "registry_predictions_post",
    ],
    [
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
        "Tutorial - Model Scoring",
        "Reference - Score",
        "Tutorial - Using from R",
    ],
    [
        "Tutorial - Simple forecast model",
        "Tutorial - Ensemble predictions",
        "Reference - Baseline Arima",
        "Reference - Ensemble",
        "Reference - Prediction optimize",
    ],
]

IMDC_GROUPS: List[List[str]] = [
    ["home", "about", "registration"],
    ["home", "sprint-2025", "instructions-2025", "registration"],
    ["home", "data-2025", "results-2025"],
]

DOCS_FALLBACK_THRESHOLD = 0.75
CODE_FALLBACK_THRESHOLD = 0.5
IMDC_FALLBACK_THRESHOLD = 0.5


def build_mosqlimate_assistant(
    google_api_key: str,
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_base_url: Optional[str] = None,
    docs_search_mode: SearchMode = "total",
    code_search_mode: SearchMode = "total",
    imdc_search_mode: SearchMode = "total",
    docs_search_scope: Literal["metadata", "content", "both"] = "both",
    code_search_scope: Literal["metadata", "content", "both"] = "both",
    imdc_search_scope: Literal["metadata", "content", "both"] = "both",
    docs_named_groups: Optional[List[List[str]]] = None,
    code_named_groups: Optional[List[List[str]]] = None,
    imdc_named_groups: Optional[List[List[str]]] = None,
    group_key: str = "id",
    id_key: str = "name",
    lang: Literal["en", "pt"] = "pt",
    **kwargs,
) -> Tuple[
    Assistant, InMemoryVectorStore, InMemoryVectorStore, InMemoryVectorStore
]:
    """Construct a full Mosqlimate AI multi-agent assistant instance.

    Reads CSV definitions, initializes separate InMemoryVectorStores for docs,
    code, and imdc agents natively. Registers each agent onto the central Orchestrator.

    Args:
        google_api_key (str): Provider execution secrets.
        gemini_model (str, optional): The Gemini backend host ID. Defaults to DEFAULT_GEMINI_MODEL.
        embedding_model (str, optional): Used for vector representations. Defaults to DEFAULT_EMBEDDING_MODEL.
        ollama_base_url (Optional[str], optional): Override URL host for embeddings. Defaults to None.
        docs_search_mode (SearchMode, optional): Retrieval approach for docs agent. Defaults to "total".
        code_search_mode (SearchMode, optional): Retrieval approach for code agent. Defaults to "total".
        imdc_search_mode (SearchMode, optional): Retrieval approach for imdc agent. Defaults to "total".
        docs_search_scope (Literal["metadata", "content", "both"], optional): Scope for docs search. Defaults to "both".
        code_search_scope (Literal["metadata", "content", "both"], optional): Scope for code search. Defaults to "both".
        imdc_search_scope (Literal["metadata", "content", "both"], optional): Scope for imdc search. Defaults to "both".
        docs_named_groups (Optional[List[List[str]]], optional): Custom query groups for docs search. Defaults to None.
        code_named_groups (Optional[List[List[str]]], optional): Custom query groups for code search. Defaults to None.
        imdc_named_groups (Optional[List[List[str]]], optional): Custom query groups for imdc search. Defaults to None.
        group_key (str, optional): Lookup variable to identify the groups. Defaults to "id".
        id_key (str, optional): Key identifier used. Defaults to "name".
        lang (Literal["en", "pt"], optional): System prompts locale mapping. Defaults to "pt".
        **kwargs: Additional keyword arguments.

    Returns:
        Tuple[Assistant, InMemoryVectorStore, InMemoryVectorStore, InMemoryVectorStore]: Assembled assistant and underlying stores.

    """
    _docs_groups = docs_named_groups or DOCS_GROUPS
    _code_groups = code_named_groups or CODE_GROUPS
    _imdc_groups = imdc_named_groups or IMDC_GROUPS

    docs_csv = DOCS_EN_CSV if lang == "en" else DOCS_CSV

    embedding_provider = OllamaEmbeddingProvider(
        model=embedding_model,
        base_url=ollama_base_url,
    )

    safe_model_name = embedding_model.replace(":", "_").replace("/", "_")
    store_dir = _DATA_DIR / "vector_stores" / safe_model_name
    store_dir.mkdir(parents=True, exist_ok=True)

    docs_store_path = store_dir / f"docs_{lang}.pkl"
    code_store_path = store_dir / "code.pkl"
    imdc_store_path = store_dir / "imdc.pkl"

    docs_store = InMemoryVectorStore(embedding_provider)
    if docs_store_path.exists():
        docs_store.load(str(docs_store_path))
    else:
        docs_manager = DocumentManager(docs_store)
        docs_manager.add_consumer(CSVLinkConsumer(docs_csv, "markdown_link"))
        docs_manager.fetch_and_index_all(collections=["docs"], id_key=id_key)
        docs_store.save(str(docs_store_path))

    code_store = InMemoryVectorStore(embedding_provider)
    if code_store_path.exists():
        code_store.load(str(code_store_path))
    else:
        code_manager = DocumentManager(code_store)
        code_manager.add_consumer(CSVLinkConsumer(CODE_CSV, "markdown_link"))
        code_manager.fetch_and_index_all(collections=["code"], id_key=id_key)
        code_store.save(str(code_store_path))

    imdc_store = InMemoryVectorStore(embedding_provider)
    if imdc_store_path.exists():
        imdc_store.load(str(imdc_store_path))
    else:
        imdc_manager = DocumentManager(imdc_store)
        imdc_manager.add_consumer(CSVLinkConsumer(IMDC_CSV, "markdown_link"))
        imdc_manager.fetch_and_index_all(collections=["imdc"], id_key=id_key)
        imdc_store.save(str(imdc_store_path))

    asst = Assistant(
        provider_type=ProviderType.GEMINI,
        provider_config={
            "api_key": google_api_key,
            "model": gemini_model,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        },
        embedding_provider=embedding_provider,
    )

    code_desc = (
        "Specialist in generating mosqlient code examples"
        if lang == "en"
        else "Especialista em gerar exemplos de código do mosqlient"
    )
    code_card = AgentCard(
        name="code_agent",
        description=code_desc,
        search_mode=code_search_mode,
        search_scope=code_search_scope,
        named_groups=_code_groups,
        group_key=group_key,
        target_groups=["code"],
        fallback_docs="code",
        fallback_threshold=CODE_FALLBACK_THRESHOLD,
    )
    code_card.set_prompt_function(lambda: get_coder_agent_prompt(lang=lang))
    asst.register_agent("code_agent", code_card, vector_store=code_store)

    imdc_desc = (
        "Specialist in the Infodengue-Mosqlimate Dengue Challenge (IMDC/Dengue Sprint)"
        if lang == "en"
        else "Especialista no Infodengue-Mosqlimate Dengue Challenge (IMDC/Sprint de Dengue)"
    )
    imdc_card = AgentCard(
        name="imdc_agent",
        description=imdc_desc,
        search_mode=imdc_search_mode,
        search_scope=imdc_search_scope,
        named_groups=_imdc_groups,
        group_key=group_key,
        target_groups=["imdc"],
        fallback_docs="imdc",
        fallback_threshold=IMDC_FALLBACK_THRESHOLD,
    )
    imdc_card.set_prompt_function(lambda: get_imdc_agent_prompt(lang=lang))
    asst.register_agent("imdc_agent", imdc_card, vector_store=imdc_store)

    docs_desc = (
        "Specialist in Mosqlimate platform documentation"
        if lang == "en"
        else "Especialista em documentação da plataforma Mosqlimate"
    )
    docs_card = AgentCard(
        name="docs_agent",
        description=docs_desc,
        search_mode=docs_search_mode,
        search_scope=docs_search_scope,
        named_groups=_docs_groups if docs_search_mode == "group" else [],
        group_key=group_key,
        target_groups=["docs"],
        fallback_docs="docs",
        fallback_threshold=DOCS_FALLBACK_THRESHOLD,
        tools=[code_card.agent_to_tool, imdc_card.agent_to_tool],
    )
    docs_card.set_prompt_function(lambda: get_base_docs_prompt(lang=lang))
    asst.register_agent(
        "docs_agent", docs_card, vector_store=docs_store, is_default=True
    )

    return asst, docs_store, code_store, imdc_store


def docs_pipeline(
    question: str,
    google_api_key: str,
    search_mode: SearchMode = "total",
    search_scope: Literal["metadata", "content", "both"] = "both",
    docs_named_groups: Optional[List[List[str]]] = None,
    code_named_groups: Optional[List[List[str]]] = None,
    imdc_named_groups: Optional[List[List[str]]] = None,
    group_key: str = "id",
    id_key: str = "name",
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_base_url: Optional[str] = None,
    message_history: Optional[List[ChatMessage]] = None,
    lang: Literal["en", "pt"] = "pt",
    **kwargs,
) -> str:
    """Route specific prompt questions through the assistant pipeline.

    Args:
        question (str): Main user phrase instruction.
        google_api_key (str): Gemini API Key.
        search_mode (SearchMode, optional): Retrieval approach for docs search. Defaults to "total".
        search_scope (Literal["metadata", "content", "both"], optional): Scope for search. Defaults to "both".
        docs_named_groups (Optional[List[List[str]]], optional): Custom query groups for docs search. Defaults to None.
        code_named_groups (Optional[List[List[str]]], optional): Custom query groups for code search. Defaults to None.
        imdc_named_groups (Optional[List[List[str]]], optional): Custom query groups for imdc search. Defaults to None.
        group_key (str, optional): Lookup variable to identify the groups. Defaults to "id".
        id_key (str, optional): Key identifier used. Defaults to "name".
        gemini_model (str, optional): The Gemini backend host ID. Defaults to DEFAULT_GEMINI_MODEL.
        embedding_model (str, optional): Used for vector representations. Defaults to DEFAULT_EMBEDDING_MODEL.
        ollama_base_url (Optional[str], optional): Override URL host for embeddings. Defaults to None.
        message_history (Optional[List[ChatMessage]], optional): Array of preceding messages. Defaults to None.
        lang (Literal["en", "pt"], optional): System prompts locale mapping. Defaults to "pt".
        **kwargs: Additional keyword arguments.

    Returns:
        str: Assistant text response to the input query.

    """
    asst, _, _, _ = build_mosqlimate_assistant(
        google_api_key=google_api_key,
        gemini_model=gemini_model,
        embedding_model=embedding_model,
        ollama_base_url=ollama_base_url,
        docs_search_mode=search_mode,
        docs_search_scope=search_scope,
        docs_named_groups=docs_named_groups,
        code_named_groups=code_named_groups,
        imdc_named_groups=imdc_named_groups,
        group_key=group_key,
        id_key=id_key,
        lang=lang,
        **kwargs,
    )
    result = asst.query(
        question,
        agent_name="docs_agent",
        message_history=message_history,
        search_scope=search_scope,
    )
    return result["content"]


def assistant_pipeline(
    question: str,
    google_api_key: str,
    message_history: Optional[List[ChatMessage]] = None,
    lang: Literal["en", "pt"] = "pt",
    **kwargs,
) -> str:
    """Expose a simplified wrapper for generating responses via the main pipeline.

    Args:
        question (str): User instruction or question.
        google_api_key (str): Provider execution credential token.
        message_history (Optional[List[ChatMessage]], optional): Array of preceding messages. Defaults to None.
        lang (Literal["en", "pt"], optional): Preferred fallback execution language mappings standard rule. Defaults to "pt".
        **kwargs: Additional keyword arguments passed to the underlying pipeline.

    Returns:
        str: Final text response generated by the pipeline.

    """
    return docs_pipeline(
        question=question,
        google_api_key=google_api_key,
        message_history=message_history,
        lang=lang,
        **kwargs,
    )
