from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    GOOGLE_GENAI = "google_genai"
    NVIDIA = "nvidia"
    DEEPSEEK = "deepseek"
    OLLAMA_CLOUD = "ollama_cloud"


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="Papel da mensagem (system, user, assistant)"
    )
    content: str = Field(..., description="Conteúdo da mensagem")


class ProviderResponse(BaseModel):
    content: str = Field(..., description="Conteúdo da resposta")
    raw_response: Any = Field(..., description="Resposta bruta do provedor")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Chamadas de ferramentas solicitadas pelo modelo",
    )


class VectorDocument(BaseModel):
    id: str = Field(..., description="Identificador único do documento")
    content: str = Field(..., description="Conteúdo textual do documento")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais do documento"
    )
    collections: List[str] = Field(
        default_factory=list,
        description="Lista de coleções/grupos a que pertence o documento",
    )


class VectorSearchResult(BaseModel):
    document: VectorDocument = Field(..., description="Documento encontrado")
    score: float = Field(..., description="Score de similaridade (0-1)")


class SourceDocument(BaseModel):
    content: str = Field(..., description="Conteúdo do documento")
    source_type: str = Field(
        ..., description="Tipo da fonte (url, csv, file, etc)"
    )
    source_identifier: str = Field(
        ..., description="Identificador da fonte (URL, caminho, etc)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais da fonte"
    )
