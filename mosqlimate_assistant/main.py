"""Preconfigured runtime entrypoints for the Mosqlimate Assistant.

This module exposes the default assistant-construction helpers used by
applications, scripts, and tests. It centralizes provider configuration,
knowledge-base loading, and compatibility wrappers around the current
single-agent runtime.
"""

from __future__ import annotations

import os
from logging import ERROR
from pathlib import Path
from time import perf_counter
from typing import Any, Literal, Optional, Tuple

from mosqlimate_assistant.assistant import Assistant
from mosqlimate_assistant.embeddings import OllamaEmbeddingProvider
from mosqlimate_assistant.knowledge_base import (
    DocumentSourceConfig,
    MosqlimateKnowledgeBase,
    build_default_blocks,
)
from mosqlimate_assistant.models import (
    ChatMessage,
    ProviderConfig,
    ProviderType,
)
from mosqlimate_assistant.monitoring import (
    elapsed_seconds,
    get_monitor_logger,
    log_event,
    preview_text,
)
from mosqlimate_assistant.settings import VECTORSTORE_CACHE_DIR

_DATA_DIR = Path(__file__).parent / "data"
DOCS_CSV = _DATA_DIR / "docs_references.csv"
DOCS_EN_CSV = _DATA_DIR / "docs_en_references.csv"
CODE_CSV = _DATA_DIR / "code_references.csv"
IMDC_CSV = _DATA_DIR / "imdc_references.csv"

DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_GOOGLE_MODEL = "gemini-2.5-flash"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
GOOGLE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
LOGGER = get_monitor_logger("main")


def _discard_legacy_options(options: dict[str, Any]) -> None:
    """Discard legacy multi-agent options kept only for loose compatibility."""
    legacy_keys = {
        "docs_search_mode",
        "code_search_mode",
        "imdc_search_mode",
        "docs_search_scope",
        "code_search_scope",
        "imdc_search_scope",
        "docs_named_groups",
        "code_named_groups",
        "imdc_named_groups",
        "group_key",
        "id_key",
        "search_mode",
        "search_scope",
    }
    for key in legacy_keys:
        options.pop(key, None)


def _build_source_configs(
    lang: Literal["en", "pt"],
) -> list[DocumentSourceConfig]:
    """Return the source configuration used by the assistant knowledge base."""
    docs_csv = DOCS_EN_CSV if lang == "en" else DOCS_CSV
    return [
        DocumentSourceConfig(domain="docs", csv_path=docs_csv),
        DocumentSourceConfig(domain="code", csv_path=CODE_CSV),
        DocumentSourceConfig(domain="imdc", csv_path=IMDC_CSV),
    ]


def _resolve_provider_config(
    google_api_key: str | None,
    gemini_model: str,
    kwargs: dict[str, Any],
) -> Tuple[ProviderConfig, ProviderType]:
    """Build the OpenAI-compatible provider configuration."""
    provider_api_key = (
        kwargs.pop("deepseek_api_key", None)
        or google_api_key
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )
    if not provider_api_key:
        raise ValueError(
            "API key not configured. Provide `google_api_key`/`deepseek_api_key` "
            "or set `DEEPSEEK_API_KEY`/`GOOGLE_API_KEY` environment variables."
        )

    # Detect provider by key prefix
    if provider_api_key.startswith("sk-"):
        provider_type = ProviderType.DEEPSEEK
        base_url = DEEPSEEK_BASE_URL
        default_model = DEFAULT_DEEPSEEK_MODEL
    else:
        provider_type = ProviderType.OPENAI  # Google via OpenAI-compatible API
        base_url = GOOGLE_BASE_URL
        default_model = DEFAULT_GOOGLE_MODEL

    # Manual model overrides
    provider_model = (
        kwargs.pop("deepseek_model", None)
        or (gemini_model if gemini_model != DEFAULT_DEEPSEEK_MODEL else None)
        or default_model
    )

    return (
        ProviderConfig(
            api_key=provider_api_key,
            model=provider_model,
            base_url=base_url,
        ),
        provider_type,
    )


def _build_store_path(
    embedding_model: str,
    lang: Literal["en", "pt"],
) -> Path:
    """Return the storage path used to persist the FAISS index."""
    safe_model_name = embedding_model.replace(":", "_").replace("/", "_")
    return VECTORSTORE_CACHE_DIR / safe_model_name / lang


def _build_knowledge_base(
    embedding_model: str,
    ollama_base_url: Optional[str],
    lang: Literal["en", "pt"],
    use_vector_store: bool,
) -> MosqlimateKnowledgeBase:
    """Build the shared knowledge base used by the assistant."""
    source_configs = _build_source_configs(lang)
    storage_path: Path | None = None
    try:
        if not use_vector_store:
            return MosqlimateKnowledgeBase.from_source_configs(
                blocks=build_default_blocks(lang=lang),
                source_configs=source_configs,
                lang=lang,
            )

        embedding_provider = OllamaEmbeddingProvider(
            model=embedding_model,
            base_url=ollama_base_url,
        )
        storage_path = _build_store_path(embedding_model, lang)
        return MosqlimateKnowledgeBase.load_or_build(
            storage_path=storage_path,
            embedding_provider=embedding_provider,
            blocks=build_default_blocks(lang=lang),
            source_configs=source_configs,
            lang=lang,
        )
    except Exception as exc:
        log_event(
            LOGGER,
            "knowledge_base_initialization_failed",
            level=ERROR,
            lang=lang,
            embedding_model=embedding_model,
            storage_path=str(storage_path),
            error=str(exc),
        )
        raise RuntimeError(
            "Failed to initialize the Mosqlimate knowledge base. "
            "Check whether the documentation sources are reachable and whether "
            f"the cache directory is writable: {storage_path}"
        ) from exc


def build_mosqlimate_assistant(
    google_api_key: str | None = None,
    gemini_model: str = DEFAULT_DEEPSEEK_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_base_url: Optional[str] = None,
    lang: Literal["en", "pt"] = "pt",
    max_tool_iterations: int = 5,
    use_vector_store: bool = False,
    **kwargs: Any,
) -> Tuple[
    Assistant,
    MosqlimateKnowledgeBase,
    MosqlimateKnowledgeBase,
    MosqlimateKnowledgeBase,
]:
    """Construct the single-agent Mosqlimate assistant.

    The tuple return shape is preserved for compatibility with older callers.
    """
    start = perf_counter()
    _discard_legacy_options(kwargs)
    provider_config, provider_type = _resolve_provider_config(
        google_api_key=google_api_key,
        gemini_model=gemini_model,
        kwargs=kwargs,
    )
    knowledge_base = _build_knowledge_base(
        embedding_model=embedding_model,
        ollama_base_url=ollama_base_url,
        lang=lang,
        use_vector_store=use_vector_store,
    )

    assistant = Assistant(
        provider_type=provider_type,
        provider_config=provider_config,
        lang=lang,
    )
    assistant.configure_tool_agent(
        knowledge_base=knowledge_base,
        max_tool_iterations=max_tool_iterations,
    )
    log_event(
        LOGGER,
        "assistant_pipeline_built",
        lang=lang,
        provider_model=provider_config.model,
        embedding_model=embedding_model if use_vector_store else None,
        use_vector_store=use_vector_store,
        block_count=(
            len(knowledge_base.available_blocks())
            if hasattr(knowledge_base, "available_blocks")
            else None
        ),
        elapsed_seconds=elapsed_seconds(start),
    )

    return assistant, knowledge_base, knowledge_base, knowledge_base


def docs_pipeline(
    question: str,
    google_api_key: str | None = None,
    gemini_model: str = DEFAULT_DEEPSEEK_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_base_url: Optional[str] = None,
    message_history: Optional[list[ChatMessage]] = None,
    lang: Literal["en", "pt"] = "pt",
    **kwargs: Any,
) -> str:
    """Return the assistant response using the default single-agent flow."""
    start = perf_counter()
    assistant, _, _, _ = build_mosqlimate_assistant(
        google_api_key=google_api_key,
        gemini_model=gemini_model,
        embedding_model=embedding_model,
        ollama_base_url=ollama_base_url,
        lang=lang,
        **kwargs,
    )
    result = assistant.query(
        user_question=question,
        message_history=message_history,
    )
    log_event(
        LOGGER,
        "docs_pipeline_completed",
        question_preview=preview_text(question),
        elapsed_seconds=elapsed_seconds(start),
        usage=result.get("usage"),
        provider_cost=result.get("provider_cost"),
        provider_metadata=result.get("provider_metadata"),
    )
    return result["content"]


def assistant_pipeline(
    question: str,
    google_api_key: str | None = None,
    message_history: Optional[list[ChatMessage]] = None,
    lang: Literal["en", "pt"] = "pt",
    **kwargs: Any,
) -> str:
    """Expose the default compatibility wrapper around the assistant pipeline."""
    return docs_pipeline(
        question=question,
        google_api_key=google_api_key,
        message_history=message_history,
        lang=lang,
        **kwargs,
    )
