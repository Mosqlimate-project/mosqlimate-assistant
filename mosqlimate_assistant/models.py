"""Core Pydantic models shared across the Mosqlimate Assistant.

This module contains the package's normalized data structures for chat
messages, provider configuration, usage accounting, tool-call records,
retrieval block declarations, and source/vector documents.
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProviderType(str, Enum):
    """Enum of supported LLM provider backends.

    Attributes:
        OPENAI: OpenAI API provider.
        GEMINI: Google Gemini provider through the OpenAI-compatible endpoint.
        OLLAMA: Local Ollama provider.
        NVIDIA: NVIDIA NIM API provider.
        DEEPSEEK: DeepSeek API provider.

    """

    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    NVIDIA = "nvidia"
    DEEPSEEK = "deepseek"


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


class ProviderConfig(BaseModel):
    """Configuration for an OpenAI-compatible chat provider."""

    api_key: str = Field(..., description="Provider API key")
    model: str = Field(..., description="Provider model identifier")
    base_url: str = Field(
        default="",
        description="Provider base URL. Can be empty when the provider default should be used.",
    )


class TokenUsage(BaseModel):
    """Normalized token usage counters."""

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)

    def merge(self, usage: "TokenUsage | dict[str, int] | None") -> None:
        """Accumulate token counters in place."""
        if usage is None:
            return
        snapshot = (
            usage
            if isinstance(usage, TokenUsage)
            else TokenUsage.model_validate(usage)
        )
        self.input_tokens += snapshot.input_tokens
        self.output_tokens += snapshot.output_tokens
        self.total_tokens += snapshot.total_tokens

    def as_optional_dict(self) -> dict[str, int] | None:
        """Return usage as a dict only when there is any non-zero value."""
        return self.model_dump() if any(self.model_dump().values()) else None


class ToolCallRecord(BaseModel):
    """One executed tool call with normalized fields."""

    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: str


class AgentRunResult(BaseModel):
    """Structured result returned by the single-agent flow."""

    content: str
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    retrieved_blocks: list[str] = Field(default_factory=list)
    iterations: int = Field(default=0, ge=0)
    usage: TokenUsage | None = None
    provider_cost: float | None = None
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    elapsed_seconds: float = Field(default=0.0, ge=0.0)

    def to_payload(self) -> dict[str, Any]:
        """Return the legacy dict payload expected by current callers."""
        return {
            "content": self.content,
            "tool_calls": [record.model_dump() for record in self.tool_calls],
            "retrieved_blocks": self.retrieved_blocks,
            "iterations": self.iterations,
            "usage": self.usage.as_optional_dict() if self.usage else None,
            "provider_cost": self.provider_cost,
            "provider_metadata": self.provider_metadata,
            "elapsed_seconds": self.elapsed_seconds,
        }


class DocumentSourceConfig(BaseModel):
    """Describes a CSV-backed documentation source."""

    model_config = ConfigDict(frozen=True)

    domain: str
    csv_path: Path
    link_column: str = "markdown_link"
    id_key: str | None = "name"


class DocumentBlockConfig(BaseModel):
    """Declarative tool block configuration."""

    model_config = ConfigDict(frozen=True)

    key: str
    description: str
    domain: str
    names: frozenset[str] = Field(default_factory=frozenset)
    url_fragments: frozenset[str] = Field(default_factory=frozenset)

    def matches(self, metadata: dict[str, Any]) -> bool:
        """Return whether a document metadata entry belongs to this block."""
        if metadata.get("domain") != self.domain:
            return False

        name = metadata.get("name")
        if self.names and name in self.names:
            return True

        urls = [
            str(metadata.get(key, ""))
            for key in (
                "markdown_link",
                "url_link",
                "url",
                "source_url",
                "source_id",
                "name",
            )
        ]
        if self.url_fragments and any(
            fragment in url for fragment in self.url_fragments for url in urls
        ):
            return True

        return not self.names and not self.url_fragments


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
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional document metadata"
    )
    collections: list[str] = Field(
        default_factory=list,
        description="List of collections/groups the document belongs to",
    )
    chunks: list[str] = Field(
        default_factory=list,
        description="Recursive text chunks for granular embedding",
    )


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
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional source metadata"
    )
