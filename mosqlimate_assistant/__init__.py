__version__ = "2.0.0"

from mosqlimate_assistant.agent_cards import AgentCard, BaseTool
from mosqlimate_assistant.agents import AgentExecutor, AgentOrchestrator
from mosqlimate_assistant.assistant import (
    Assistant,
    create_deepseek_assistant,
    create_gemini_assistant,
    create_google_genai_assistant,
    create_nvidia_assistant,
    create_ollama_assistant,
    create_openai_assistant,
)
from mosqlimate_assistant.document_consumer import (
    BaseDocumentConsumer,
    CSVLinkConsumer,
    DocumentManager,
    FileDocumentConsumer,
    URLDocumentConsumer,
)
from mosqlimate_assistant.embeddings import (
    BaseEmbeddingProvider,
    OllamaEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from mosqlimate_assistant.main import (
    assistant_pipeline,
    build_mosqlimate_assistant,
    docs_pipeline,
)
from mosqlimate_assistant.models import (
    ChatMessage,
    ProviderResponse,
    ProviderType,
    SourceDocument,
    VectorDocument,
    VectorSearchResult,
)
from mosqlimate_assistant.providers import (
    BaseProvider,
    DeepSeekProvider,
    GeminiProvider,
    GoogleGenAIProvider,
    NvidiaProvider,
    OllamaProvider,
    OpenAIProvider,
    ProviderFactory,
)
from mosqlimate_assistant.vector_store import (
    BaseVectorStore,
    InMemoryVectorStore,
)

__all__ = [
    "ChatMessage",
    "ProviderResponse",
    "ProviderType",
    "SourceDocument",
    "VectorDocument",
    "VectorSearchResult",
    "BaseProvider",
    "OpenAIProvider",
    "DeepSeekProvider",
    "GeminiProvider",
    "GoogleGenAIProvider",
    "NvidiaProvider",
    "OllamaProvider",
    "ProviderFactory",
    "BaseEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "BaseVectorStore",
    "InMemoryVectorStore",
    "BaseDocumentConsumer",
    "URLDocumentConsumer",
    "CSVLinkConsumer",
    "FileDocumentConsumer",
    "DocumentManager",
    "BaseTool",
    "AgentCard",
    "AgentExecutor",
    "AgentOrchestrator",
    "Assistant",
    "create_ollama_assistant",
    "create_openai_assistant",
    "create_gemini_assistant",
    "create_google_genai_assistant",
    "create_nvidia_assistant",
    "create_deepseek_assistant",
    "build_mosqlimate_assistant",
    "docs_pipeline",
    "assistant_pipeline",
]
