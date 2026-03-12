from typing import Any, Dict, List, Optional

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

    def __init__(
        self,
        provider_type: ProviderType,
        provider_config: Dict[str, Any],
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        vector_store: Optional[BaseVectorStore] = None,
    ):
        self.provider: BaseProvider = ProviderFactory.create(
            provider_type, provider_config
        )

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

        if embedding_provider and not vector_store:
            self.vector_store = InMemoryVectorStore(embedding_provider)

        self.document_manager = (
            DocumentManager(self.vector_store) if self.vector_store else None
        )

        self.orchestrator = AgentOrchestrator()

        docs_agent_card = AgentCard(
            name="docs_agent",
            description="Agente especialista em documentação Mosqlimate",
        )
        docs_agent_card.set_prompt_function(get_base_docs_prompt)

        docs_agent = AgentExecutor(
            agent_card=docs_agent_card,
            provider=self.provider,
            vector_store=self.vector_store,
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
        agent = AgentExecutor(
            agent_card=agent_card,
            provider=provider or self.provider,
            vector_store=vector_store or self.vector_store,
        )
        self.orchestrator.register_agent(name, agent, is_default=is_default)

    def add_documents_from_urls(
        self, urls: List[str], collection: Optional[str] = None
    ) -> None:
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
        return self.orchestrator.route(
            user_question,
            agent_name=agent_name,
            message_history=message_history,
            use_rag=use_rag,
        )

    def save_vector_store(self, path: str) -> None:
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")
        self.vector_store.save(path)

    def load_vector_store(self, path: str) -> None:
        if not self.vector_store:
            raise ValueError("Vector store não inicializado")
        self.vector_store.load(path)


def create_ollama_assistant(
    model: str = "llama3.2:latest",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: Optional[str] = None,
) -> Assistant:
    return Assistant(
        provider_type=ProviderType.OLLAMA,
        provider_config={"model": model, "base_url": base_url},
        embedding_provider=OllamaEmbeddingProvider(embedding_model, base_url),
    )


def create_openai_assistant(
    api_key: str,
    model: str = "gpt-4o-mini",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: str = "https://api.openai.com/v1",
) -> Assistant:
    return Assistant(
        provider_type=ProviderType.OPENAI,
        provider_config={
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
        },
        embedding_provider=OpenAIEmbeddingProvider(api_key, embedding_model),
    )


def create_gemini_assistant(
    api_key: str,
    model: str = "gemini-2.5-flash",
    embedding_model: str = "mxbai-embed-large:latest",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
) -> Assistant:
    return Assistant(
        provider_type=ProviderType.GEMINI,
        provider_config={
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
        },
        embedding_provider=OpenAIEmbeddingProvider(api_key, embedding_model),
    )


def create_google_genai_assistant(
    api_key: str,
    model: str = "gemini-2.5-flash",
    embedding_model: str = "mxbai-embed-large:latest",
) -> Assistant:
    return Assistant(
        provider_type=ProviderType.GOOGLE_GENAI,
        provider_config={"api_key": api_key, "model": model},
        embedding_provider=OpenAIEmbeddingProvider(api_key, embedding_model),
    )


def create_nvidia_assistant(
    api_key: str,
    model: str = "deepseek-ai/deepseek-v3.2",
    embedding_provider: Optional[BaseEmbeddingProvider] = None,
) -> Assistant:
    return Assistant(
        provider_type=ProviderType.NVIDIA,
        provider_config={"api_key": api_key, "model": model},
        embedding_provider=embedding_provider,
    )


def create_deepseek_assistant(
    api_key: str,
    model: str = "deepseek-chat",
    embedding_provider: Optional[BaseEmbeddingProvider] = None,
) -> Assistant:
    return Assistant(
        provider_type=ProviderType.DEEPSEEK,
        provider_config={"api_key": api_key, "model": model},
        embedding_provider=embedding_provider,
    )
