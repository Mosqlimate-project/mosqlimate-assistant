"""High-level assistant wrapper around the single-agent runtime.

This module provides the user-facing ``Assistant`` class plus small
factory helpers for supported providers. It is responsible for wiring a
configured knowledge base to the tool-calling agent and exposing a
simple ``query`` interface for callers.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, List, Literal, Optional

from langchain_community.vectorstores import FAISS

from mosqlimate_assistant.agent import LangChainToolAgent
from mosqlimate_assistant.knowledge_base import MosqlimateKnowledgeBase
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


class Assistant:
    """Main runtime wrapper around the LangChain single-agent flow."""

    def __init__(
        self,
        provider_type: ProviderType,
        provider_config: ProviderConfig | Dict[str, Any],
        lang: Literal["en", "pt"] = "pt",
    ) -> None:
        self.provider_type = provider_type
        self.provider_config = ProviderConfig.model_validate(provider_config)
        self.lang = lang
        self.knowledge_base: Optional[MosqlimateKnowledgeBase] = None
        self.tool_agent: Optional[LangChainToolAgent] = None
        self.logger = get_monitor_logger("assistant")
        log_event(
            self.logger,
            "assistant_initialized",
            provider_type=str(provider_type),
            lang=lang,
        )

    def configure_tool_agent(
        self,
        knowledge_base: MosqlimateKnowledgeBase,
        max_tool_iterations: int = 5,
    ) -> None:
        """Attach the block-based knowledge base and build the agent."""
        self.knowledge_base = knowledge_base
        self.tool_agent = LangChainToolAgent(
            knowledge_base=knowledge_base,
            provider_type=self.provider_type,
            provider_config=self.provider_config,
            lang=self.lang,
            max_tool_iterations=max_tool_iterations,
        )
        log_event(
            self.logger,
            "tool_agent_configured",
            block_count=len(knowledge_base.available_blocks()),
            max_tool_iterations=max_tool_iterations,
        )

    def query(
        self,
        user_question: str,
        message_history: Optional[List[ChatMessage]] = None,
    ) -> Dict[str, Any]:
        """Run the configured single-agent flow."""
        if self.tool_agent is None:
            raise ValueError("Tool agent not configured")
        start = perf_counter()
        log_event(
            self.logger,
            "query_started",
            lang=self.lang,
            history_messages=len(message_history or []),
            question_preview=preview_text(user_question),
        )
        result = self.tool_agent.run(
            user_query=user_question,
            message_history=message_history,
        )
        log_event(
            self.logger,
            "query_completed",
            elapsed_seconds=elapsed_seconds(start),
            iterations=result.get("iterations"),
            tool_calls_count=len(result.get("tool_calls") or []),
            retrieved_blocks=result.get("retrieved_blocks") or [],
            usage=result.get("usage"),
            provider_cost=result.get("provider_cost"),
            provider_metadata=result.get("provider_metadata"),
        )
        return result

    def save_vector_store(self, path: str) -> None:
        """Persist the FAISS index to a directory path."""
        if self.knowledge_base is None:
            raise ValueError("Knowledge base not initialized")
        self.knowledge_base.vector_store.save_local(path)

    def load_vector_store(self, path: str) -> None:
        """Load the FAISS index from a directory path."""
        if self.knowledge_base is None:
            raise ValueError("Knowledge base not initialized")
        self.knowledge_base.vector_store = FAISS.load_local(
            folder_path=path,
            embeddings=self.knowledge_base.embeddings,
            allow_dangerous_deserialization=True,
        )


def _create_openai_compatible_assistant(
    provider_type: ProviderType,
    api_key: str,
    model: str,
    base_url: str,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an assistant for an OpenAI-compatible provider."""
    return Assistant(
        provider_type=provider_type,
        provider_config=ProviderConfig(
            api_key=api_key,
            model=model,
            base_url=base_url,
        ),
        lang=lang,
    )


def create_ollama_assistant(
    model: str = "llama3.2:latest",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: Optional[str] = None,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Reject unsupported Ollama chat configuration for the LangChain flow."""
    del model, embedding_model, base_url, lang
    raise NotImplementedError(
        "The LangChain single-agent flow currently supports only "
        "OpenAI-compatible chat providers. Use Gemini, OpenAI, NVIDIA, "
        "or DeepSeek for the refactored implementation."
    )


def create_openai_assistant(
    api_key: str,
    model: str = "gpt-4o-mini",
    embedding_model: str = "text-embedding-3-small",
    base_url: str = "https://api.openai.com/v1",
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant configured to use the OpenAI API."""
    del embedding_model
    return _create_openai_compatible_assistant(
        provider_type=ProviderType.OPENAI,
        api_key=api_key,
        model=model,
        base_url=base_url,
        lang=lang,
    )


def create_gemini_assistant(
    api_key: str,
    model: str = "gemini-2.5-flash",
    embedding_model: str = "text-embedding-3-small",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Configure an Assistant for Gemini via the OpenAI-compatible endpoint."""
    del embedding_model
    return _create_openai_compatible_assistant(
        provider_type=ProviderType.GEMINI,
        api_key=api_key,
        model=model,
        base_url=base_url,
        lang=lang,
    )


def create_google_genai_assistant(
    api_key: str,
    model: str = "gemini-2.5-flash",
    embedding_model: str = "text-embedding-3-small",
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Compatibility wrapper that currently configures Gemini the same way."""
    return create_gemini_assistant(
        api_key=api_key,
        model=model,
        embedding_model=embedding_model,
        lang=lang,
    )


def create_nvidia_assistant(
    api_key: str,
    model: str = "deepseek-ai/deepseek-v3.2",
    embedding_provider: Optional[object] = None,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant configured for NVIDIA's OpenAI-compatible API."""
    del embedding_provider
    return _create_openai_compatible_assistant(
        provider_type=ProviderType.NVIDIA,
        api_key=api_key,
        model=model,
        base_url="https://integrate.api.nvidia.com/v1",
        lang=lang,
    )


def create_deepseek_assistant(
    api_key: str,
    model: str = "deepseek-chat",
    embedding_provider: Optional[object] = None,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant configured for DeepSeek's OpenAI-compatible API."""
    del embedding_provider
    return _create_openai_compatible_assistant(
        provider_type=ProviderType.DEEPSEEK,
        api_key=api_key,
        model=model,
        base_url="https://api.deepseek.com",
        lang=lang,
    )
