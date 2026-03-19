"""Text embedding providers for the vector store.

Provides an abstract interface (``BaseEmbeddingProvider``) and concrete
implementations for generating vector embeddings from text, which are
used by the vector store for similarity search.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np


class BaseEmbeddingProvider(ABC):
    """Abstract base class for all embedding providers.

    This class defines the interface for creating text embeddings. Valid
    providers must implement the `embed_query` method.
    """

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for the given text.

        Args:
            text (str): The input text to embed.

        Returns:
            List[float]: The generated embedding vector.

        """
        pass

    def safe_embed(self, text: str) -> List[float]:
        """Safely generate an embedding, falling back to truncated text if it fails.

        Args:
            text (str): The input text to embed.

        Returns:
            List[float]: The generated embedding vector, or an empty list if all attempts fail.

        """
        current = text
        while current:
            emb = self.embed_query(current)
            if emb:
                return emb
            current = current[: len(current) // 2]
        return []


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Local embeddings provider via Ollama.

    This provider uses a local Ollama instance to generate embeddings. It is the
    default provider used in the system.

    Attributes:
        model (str): The name of the Ollama model to use.
        max_text_length (int): The maximum length of text allowed per embedding call.
        client (ollama.Client): The Ollama client instance.

    """

    def __init__(
        self,
        model: str = "mxbai-embed-large:latest",
        base_url: Optional[str] = None,
        max_text_length: int = 2000,
    ):
        """Initialize the Ollama embedding provider.

        Args:
            model (str, optional): The Ollama model. Defaults to "mxbai-embed-large:latest".
            base_url (str, optional): The base URL of the Ollama API. Defaults to None.
            max_text_length (int, optional): The max allowed length. Defaults to 2000.

        """
        import ollama

        self.model = model
        self.max_text_length = max_text_length
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        """Normalize an embedding vector to unit length.

        Args:
            vector (List[float]): The input vector.

        Returns:
            List[float]: The normalized vector.

        """
        arr = np.asarray(vector, dtype=float)
        norm = np.linalg.norm(arr)
        return (arr / norm).tolist() if norm > 0 else vector

    def embed_query(self, text: str) -> List[float]:
        """Generate a normalized embedding for the given text using Ollama.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The normalized embedding vector. Returns an empty list on error.

        """
        safe_text = (
            text[: self.max_text_length]
            if len(text) > self.max_text_length
            else text
        )
        try:
            response = self.client.embeddings(
                model=self.model, prompt=safe_text
            )
            return self._normalize(response["embedding"])
        except Exception:
            return []


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Cloud embeddings provider via the OpenAI API.

    Attributes:
        client (openai.OpenAI): The OpenAI client instance.
        model (str): The OpenAI embedding model to use.

    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """Initialize the OpenAI embedding provider.

        Args:
            api_key (str): The OpenAI API key.
            model (str, optional): The OpenAI embedding model. Defaults to "text-embedding-3-small".

        """
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for the given text using OpenAI.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The generated embedding vector.

        """
        response = self.client.embeddings.create(
            model=self.model, input=[text]
        )
        return response.data[0].embedding
