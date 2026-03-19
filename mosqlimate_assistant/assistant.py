"""High-level Assistant class and provider-specific factory functions.

The ``Assistant`` class is the main entry point for creating an AI
assistant instance. It wires together an LLM provider, an embedding
provider, a vector store, and an ``AgentOrchestrator`` with a default
documentation agent.

Factory functions provide one-liner setup for each provider:
    - ``create_ollama_assistant``
    - ``create_openai_assistant``
    - ``create_gemini_assistant``
    - ``create_google_genai_assistant``
    - ``create_nvidia_assistant``
    - ``create_deepseek_assistant``
"""

from typing import Any, Dict, List, Literal, Optional

from mosqlimate_assistant.agent_cards import AgentCard
from mosqlimate_assistant.agents import AgentExecutor, AgentOrchestrator
from mosqlimate_assistant.document_consumer import DocumentManager
from mosqlimate_assistant.embeddings import (
    BaseEmbeddingProvider,
    OllamaEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from mosqlimate_assistant.models import ChatMessage, ProviderType
from mosqlimate_assistant.prompts import get_base_docs_prompt
from mosqlimate_assistant.providers import BaseProvider, ProviderFactory
from mosqlimate_assistant.vector_store import (
    BaseVectorStore,
    InMemoryVectorStore,
)


class Assistant:
    """Manages high-level interactions combining Vector Stores and language models.

    Attributes:
        provider (BaseProvider): The configured LLM engine instance.
        embedding_provider (Optional[BaseEmbeddingProvider]): The model client to generate semantic vector floats.
        vector_store (Optional[BaseVectorStore]): Information persistence retrieval DB.
        document_manager (Optional[DocumentManager]): High level data ingestion layer.
        orchestrator (AgentOrchestrator): The internal query traffic director pipeline.
        lang (Literal["en", "pt"]): Default locale applied towards agent responses.

    """

    def __init__(
        self,
        provider_type: ProviderType,
        provider_config: Dict[str, Any],
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        vector_store: Optional[BaseVectorStore] = None,
        lang: Literal["en", "pt"] = "pt",
    ):
        """Construct the Assistant controller class.

        Args:
            provider_type (ProviderType): The enumeration specifying which inference host handles generation.
            provider_config (Dict[str, Any]): Host specific token/models dictionary.
            embedding_provider (Optional[BaseEmbeddingProvider], optional): Text chunk conversion provider mapping tool. Defaults to None.
            vector_store (Optional[BaseVectorStore], optional): Underlying storage instance lookup indexing node. Defaults to None.
            lang (Literal["en", "pt"], optional): Preferred fallback execution language mappings standard rule. Defaults to "pt".

        """
        self.provider: BaseProvider = ProviderFactory.create(
            provider_type, provider_config
        )

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.lang = lang

        if embedding_provider and not vector_store:
            self.vector_store = InMemoryVectorStore(embedding_provider)

        self.document_manager = (
            DocumentManager(self.vector_store) if self.vector_store else None
        )

        self.orchestrator = AgentOrchestrator()

        docs_desc = (
            "Specialist agent in Mosqlimate documentation"
            if lang == "en"
            else "Agente especialista em documentação Mosqlimate"
        )
        docs_agent_card = AgentCard(
            name="docs_agent",
            description=docs_desc,
        )
        docs_agent_card.set_prompt_function(
            lambda **kw: get_base_docs_prompt(lang=lang, **kw)
        )

        docs_agent = AgentExecutor(
            agent_card=docs_agent_card,
            provider=self.provider,
            vector_store=self.vector_store,
            lang=self.lang,
        )

        self.orchestrator.register_agent("docs", docs_agent, is_default=True)

    def register_agent(
        self,
        name: str,
        agent_card: AgentCard,
        vector_store: Optional[BaseVectorStore] = None,
        provider: Optional[BaseProvider] = None,
        is_default: bool = False,
    ) -> None:
        """Dynamically add an auxiliary specialist tool-handler logic loop graph.

        Args:
            name (str): Label identifier routing.
            agent_card (AgentCard): Defines capabilities sets alongside retrieval rules boundaries.
            vector_store (Optional[BaseVectorStore], optional): Sandbox knowledge index source. Defaults to None.
            provider (Optional[BaseProvider], optional): Specialized node instance handling engine processing. Defaults to None.
            is_default (bool, optional): Allows implicit invocations catching generic input payloads. Defaults to False.

        """
        agent = AgentExecutor(
            agent_card=agent_card,
            provider=provider or self.provider,
            vector_store=vector_store or self.vector_store,
            lang=self.lang,
        )
        self.orchestrator.register_agent(name, agent, is_default=is_default)

    def add_documents_from_urls(
        self, urls: List[str], collection: Optional[str] = None
    ) -> None:
        """Parse array listing targets and store their content strings automatically sorted.

        Args:
            urls (List[str]): Web addresses targeting markdown or unformatted flat sources.
            collection (Optional[str], optional): Category label string applied to these documents. Defaults to None.

        Raises:
            ValueError: Document manager initialization error.

        """
        if not self.document_manager:
            raise ValueError(
                "Document manager não inicializado (precisa de vector store)"
            )

        from mosqlimate_assistant.document_consumer import URLDocumentConsumer

        consumer = URLDocumentConsumer(urls)
        self.document_manager.add_consumer(consumer)
        collections = [collection] if collection else None
        self.document_manager.fetch_and_index_all(collections=collections)

    def add_documents_from_csv(
        self,
        csv_path: str,
        link_column: str = "markdown_link",
        collection: Optional[str] = None,
    ) -> None:
        """Automatically index batch sources listed directly across column mapped index.

        Args:
            csv_path (str): The valid target file name link.
            link_column (str, optional): The name of the reference identifier target fields. Defaults to "markdown_link".
            collection (Optional[str], optional): Overridden tag marking group collection. Defaults to None.

        Raises:
            ValueError: Vector db unavailable missing components flags.

        """
        if not self.document_manager:
            raise ValueError(
                "Document manager não inicializado (precisa de vector store)"
            )

        from mosqlimate_assistant.document_consumer import CSVLinkConsumer

        consumer = CSVLinkConsumer(csv_path, link_column)
        self.document_manager.add_consumer(consumer)
        collections = [collection] if collection else None
        self.document_manager.fetch_and_index_all(collections=collections)

    def query(
        self,
        user_question: str,
        agent_name: Optional[str] = None,
        message_history: Optional[List[ChatMessage]] = None,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """Perform a standard end-user interaction round.

        Args:
            user_question (str): The raw instruction prompt from user.
            agent_name (Optional[str], optional): Target agent name to route to. Defaults to None.
            message_history (Optional[List[ChatMessage]], optional): Arrays containing preceding messages. Defaults to None.
            use_rag (bool, optional): Explicit flag controlling datasets RAG logic. Defaults to True.

        Returns:
            Dict[str, Any]: Mapped parsed formats arrays outputs strings responses parameters.

        """
        return self.orchestrator.route(
            user_question,
            agent_name=agent_name,
            message_history=message_history,
            use_rag=use_rag,
        )

    def save_vector_store(self, path: str) -> None:
        """Serialize memory blocks items parameters towards physical targets structures.

        Args:
            path (str): Fields file pointer.

        Raises:
            ValueError: Vector store is not initialized.

        """
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")
        self.vector_store.save(path)

    def load_vector_store(self, path: str) -> None:
        """Reconstruct the previously preserved maps subsets arrays strings limits variables.

        Args:
            path (str): File path pointing to the saved states formats bounds.

        Raises:
            ValueError: Vector store is not initialized.

        """
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")
        self.vector_store.load(path)


def create_ollama_assistant(
    model: str = "llama3.2:latest",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: Optional[str] = None,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Instantiate an Assistant configured for a local Ollama backend.

    Args:
        model (str, optional): Ollama generation model. Defaults to "llama3.2:latest".
        embedding_model (str, optional): Ollama embedding model. Defaults to "mxbai-embed-large:latest".
        base_url (Optional[str], optional): The base URL for the Ollama server. Defaults to None.
        lang (Literal["en", "pt"], optional): Agent response language. Defaults to "pt".

    Returns:
        Assistant: Preconfigured Assistant instance using Ollama.

    """
    return Assistant(
        provider_type=ProviderType.OLLAMA,
        provider_config={"model": model, "base_url": base_url},
        embedding_provider=OllamaEmbeddingProvider(embedding_model, base_url),
        lang=lang,
    )


def create_openai_assistant(
    api_key: str,
    model: str = "gpt-4o-mini",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: str = "https://api.openai.com/v1",
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant configured to use the OpenAI API.

    Args:
        api_key (str): Provider execution credential token.
        model (str, optional): Target text generator model. Defaults to "gpt-4o-mini".
        embedding_model (str, optional): OpenAI embedding model to use. Defaults to "mxbai-embed-large:latest".
        base_url (str, optional): Make requests to this alternate host. Defaults to "https://api.openai.com/v1".
        lang (Literal["en", "pt"], optional): Agent response language. Defaults to "pt".

    Returns:
        Assistant: Preconfigured Assistant object setup with OpenAI.

    """
    return Assistant(
        provider_type=ProviderType.OPENAI,
        provider_config={
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
        },
        embedding_provider=OpenAIEmbeddingProvider(api_key, embedding_model),
        lang=lang,
    )


def create_gemini_assistant(
    api_key: str,
    model: str = "gemini-2.5-flash",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Configure an Assistant for using the Gemini models via OpenAI compatibility API.

    Args:
        api_key (str): authentication token for Gemini API.
        model (str, optional): The Gemini model to use. Defaults to "gemini-2.5-flash".
        embedding_model (str, optional): Embedding model to use. Defaults to "mxbai-embed-large:latest".
        base_url (str, optional): The endpoint URL compatible with OpenAI SDK. Defaults to "https://generativelanguage.googleapis.com/v1beta/openai/".
        lang (Literal["en", "pt"], optional): Agent response language. Defaults to "pt".

    Returns:
        Assistant: Initialized Assistant using the Gemini backend.

    """
    return Assistant(
        provider_type=ProviderType.GEMINI,
        provider_config={
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
        },
        embedding_provider=OpenAIEmbeddingProvider(api_key, embedding_model),
        lang=lang,
    )


def create_google_genai_assistant(
    api_key: str,
    model: str = "gemini-2.5-flash",
    embedding_model: str = "mxbai-embed-large:latest",
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant using the Google GenAI SDK backend.

    Args:
        api_key (str): The Google GenAI API key.
        model (str, optional): Text generation model. Defaults to "gemini-2.5-flash".
        embedding_model (str, optional): Embedding model to use. Defaults to "mxbai-embed-large:latest".
        lang (Literal["en", "pt"], optional): Agent response language. Defaults to "pt".

    Returns:
        Assistant: Assistant instance configured with Google GenAI.

    """
    return Assistant(
        provider_type=ProviderType.GOOGLE_GENAI,
        provider_config={"api_key": api_key, "model": model},
        embedding_provider=OpenAIEmbeddingProvider(api_key, embedding_model),
        lang=lang,
    )


def create_nvidia_assistant(
    api_key: str,
    model: str = "deepseek-ai/deepseek-v3.2",
    embedding_provider: Optional[BaseEmbeddingProvider] = None,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant configured for NVIDIA NIM APIs.

    Args:
        api_key (str): NVIDIA API key.
        model (str, optional): Generation model mapped on NVIDIA endpoints. Defaults to "deepseek-ai/deepseek-v3.2".
        embedding_provider (Optional[BaseEmbeddingProvider], optional): Configured custom embedding provider. Defaults to None.
        lang (Literal["en", "pt"], optional): Agent response language. Defaults to "pt".

    Returns:
        Assistant: Assistant instance configured for NVIDIA.

    """
    return Assistant(
        provider_type=ProviderType.NVIDIA,
        provider_config={"api_key": api_key, "model": model},
        embedding_provider=embedding_provider,
        lang=lang,
    )


def create_deepseek_assistant(
    api_key: str,
    model: str = "deepseek-chat",
    embedding_provider: Optional[BaseEmbeddingProvider] = None,
    lang: Literal["en", "pt"] = "pt",
) -> Assistant:
    """Build an Assistant utilizing DeepSeek official APIs.

    Args:
        api_key (str): The DeepSeek API key.
        model (str, optional): DeepSeek generation model. Defaults to "deepseek-chat".
        embedding_provider (Optional[BaseEmbeddingProvider], optional): Configured custom embedding provider. Defaults to None.
        lang (Literal["en", "pt"], optional): Agent response language. Defaults to "pt".

    Returns:
        Assistant: Assistant instance configured with DeepSeek parameters.

    """
    return Assistant(
        provider_type=ProviderType.DEEPSEEK,
        provider_config={"api_key": api_key, "model": model},
        embedding_provider=embedding_provider,
        lang=lang,
    )
