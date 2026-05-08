__version__ = "1.12.1"  # changed by semantic-release

from mosqlimate_assistant.agent import (
    ChatMessageAdapter,
    ChatModelFactory,
    LangChainToolAgent,
    ToolCatalog,
)
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
    ChunkingConfig,
    CSVLinkConsumer,
    DocumentManager,
    FileDocumentConsumer,
    URLDocumentConsumer,
    VectorDocumentFactory,
)
from mosqlimate_assistant.embeddings import (
    BaseEmbeddingProvider,
    OllamaEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from mosqlimate_assistant.knowledge_base import (
    DocumentBlockConfig,
    DocumentSourceConfig,
    LangChainDocumentFactory,
    LangChainEmbeddingAdapter,
    MosqlimateKnowledgeBase,
    SourceDocumentPipeline,
)
from mosqlimate_assistant.main import (
    assistant_pipeline,
    build_mosqlimate_assistant,
    docs_pipeline,
)
from mosqlimate_assistant.models import (
    AgentRunResult,
    ChatMessage,
    ProviderConfig,
    ProviderType,
    SourceDocument,
    TokenUsage,
    ToolCallRecord,
    VectorDocument,
)

__all__ = [
    "AgentRunResult",
    "ChatMessage",
    "ProviderConfig",
    "ProviderType",
    "SourceDocument",
    "TokenUsage",
    "ToolCallRecord",
    "VectorDocument",
    "BaseEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "BaseDocumentConsumer",
    "URLDocumentConsumer",
    "CSVLinkConsumer",
    "FileDocumentConsumer",
    "ChunkingConfig",
    "VectorDocumentFactory",
    "DocumentManager",
    "DocumentBlockConfig",
    "DocumentSourceConfig",
    "LangChainEmbeddingAdapter",
    "LangChainDocumentFactory",
    "SourceDocumentPipeline",
    "MosqlimateKnowledgeBase",
    "ChatMessageAdapter",
    "ChatModelFactory",
    "ToolCatalog",
    "LangChainToolAgent",
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
