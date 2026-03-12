from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np


class BaseEmbeddingProvider(ABC):

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

    def safe_embed(self, text: str) -> List[float]:
        current = text
        while current:
            emb = self.embed_query(current)
            if emb:
                return emb
            current = current[: len(current) // 2]
        return []


class OllamaEmbeddingProvider(BaseEmbeddingProvider):

    def __init__(
        self,
        model: str = "mxbai-embed-large:latest",
        base_url: Optional[str] = None,
        max_text_length: int = 2000,
    ):
        import ollama

        self.model = model
        self.max_text_length = max_text_length
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        arr = np.asarray(vector, dtype=float)
        norm = np.linalg.norm(arr)
        return (arr / norm).tolist() if norm > 0 else vector

    def embed_query(self, text: str) -> List[float]:
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

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model, input=[text]
        )
        return response.data[0].embedding
