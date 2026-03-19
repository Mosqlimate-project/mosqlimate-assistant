"""Pydantic data models used across the mosqlimate-assistant package.

Defines the core data structures for messages, provider responses,
vector documents, and search results that flow between the different
layers of the system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    """Enum of supported LLM provider backends.

    Attributes:
        OPENAI: OpenAI API provider.
        GEMINI: Google Gemini provider using the newer google-genai library in python.
        OLLAMA: Local Ollama provider.
        GOOGLE_GENAI: Google GenAI API provider.
        NVIDIA: NVIDIA NIM API provider.
        DEEPSEEK: DeepSeek API provider.
        OLLAMA_CLOUD: Ollama Cloud API provider.

    """

    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    GOOGLE_GENAI = "google_genai"
    NVIDIA = "nvidia"
    DEEPSEEK = "deepseek"
    OLLAMA_CLOUD = "ollama_cloud"


class ChatMessage(BaseModel):
    """Single message in a conversation.

    Attributes:
        role (str): Role of the message (system, user, assistant).
        content (str): Textual content of the message.

    """

    role: str = Field(
        ..., description="Role of the message (system, user, assistant)"
    )
    content: str = Field(..., description="Content of the message")


class ProviderResponse(BaseModel):
    """Structured response from an LLM provider.

    Attributes:
        content (str): Textual content of the response.
        raw_response (Any): Raw original response returned by the provider.
        tool_calls (Optional[List[Dict[str, Any]]]): List of tool calls requested by the model.

    """

    content: str = Field(..., description="Content of the response")
    raw_response: Any = Field(..., description="Raw provider response")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tool calls requested by the model",
    )


class VectorDocument(BaseModel):
    """Document stored in the vector database with embeddings.

    Attributes:
        id (str): Unique identifier of the document.
        content (str): Textual content of the document.
        metadata (Dict[str, Any]): Additional key-value metadata of the document.
        collections (List[str]): List of collections or groups the document belongs to.

    """

    id: str = Field(..., description="Unique document identifier")
    content: str = Field(..., description="Textual content of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional document metadata"
    )
    collections: List[str] = Field(
        default_factory=list,
        description="List of collections/groups the document belongs to",
    )


class VectorSearchResult(BaseModel):
    """A document paired with its similarity score.

    Attributes:
        document (VectorDocument): The document retrieved from the store.
        score (float): Similarity score ranging from 0 to 1 (higher is more similar).

    """

    document: VectorDocument = Field(..., description="Found document")
    score: float = Field(..., description="Similarity score (0-1)")


class SourceDocument(BaseModel):
    """Raw document fetched from an external source before indexing.

    Attributes:
        content (str): Raw text of the document.
        source_type (str): Type of the source from which it was extracted (e.g., url, csv, file, text).
        source_identifier (str): Unique identifier of the source resource (e.g., URL, file path).
        metadata (Dict[str, Any]): Additional metadata extracted from the source.

    """

    content: str = Field(..., description="Content of the document")
    source_type: str = Field(
        ..., description="Type of the source (url, csv, file, etc)"
    )
    source_identifier: str = Field(
        ..., description="Source identifier (URL, path, etc)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional source metadata"
    )
