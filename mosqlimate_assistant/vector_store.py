import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.models import VectorDocument, VectorSearchResult


class BaseVectorStore(ABC):

    @abstractmethod
    def add_documents(self, documents: List[VectorDocument]) -> None:
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 3,
        metadata_filters: Optional[Dict] = None,
        collections: Optional[List[str]] = None,
    ) -> List[VectorSearchResult]:
        pass

    @abstractmethod
    def group_similarity_search(
        self,
        query: str,
        k: int = 3,
    ) -> List[VectorSearchResult]:
        pass

    @abstractmethod
    def named_group_search(
        self,
        query: str,
        groups: List[List[str]],
        group_key: str = "id",
    ) -> List[VectorSearchResult]:
        """Busca por grupos customizados definidos como lista de listas.

        Cada grupo é uma lista de identificadores de documentos.
        A query é comparada com a concatenação de conteúdo de cada grupo
        e os documentos do grupo mais similar são retornados.

        Parameters
        ----------
        group_key : str
            Campo usado para identificar documentos nos grupos.
            - ``"id"`` (padrão): usa ``doc.id`` — funciona com qualquer
              fonte de documentos (CSV, URL, arquivo, etc.)
            - qualquer outra string: usa ``doc.metadata[group_key]``
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[VectorSearchResult]:
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        pass

    @abstractmethod
    def get_documents_by_collection(
        self, collection_name: str
    ) -> List[VectorDocument]:
        pass


class InMemoryVectorStore(BaseVectorStore):
    """1 embedding por doc (truncado se necessário), 1 por grupo."""

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.documents: List[VectorDocument] = []
        self.embeddings: Optional[np.ndarray] = None
        self.group_embeddings: Dict[str, np.ndarray] = {}

    def add_documents(self, documents: List[VectorDocument]) -> None:
        if not documents:
            return

        # 1 embedding por documento (truncado se necessário)
        paired: list[tuple[VectorDocument, List[float]]] = []
        for doc in documents:
            emb = self.embedding_provider.safe_embed(doc.content)
            if emb:
                paired.append((doc, emb))

        if not paired:
            return

        new_docs = [p[0] for p in paired]
        new_embeddings = np.array([p[1] for p in paired])

        if self.embeddings is None:
            self.embeddings = new_embeddings
            self.documents = list(new_docs)
        else:
            existing_ids = {doc.id: i for i, doc in enumerate(self.documents)}
            docs_to_add = []
            embeddings_to_add = []

            for i, doc in enumerate(new_docs):
                if doc.id in existing_ids:
                    idx = existing_ids[doc.id]
                    existing_doc = self.documents[idx]

                    doc.collections = list(
                        set(existing_doc.collections) | set(doc.collections)
                    )

                    merged_metadata = existing_doc.metadata.copy()
                    merged_metadata.update(doc.metadata)
                    doc.metadata = merged_metadata

                    self.documents[idx] = doc
                    self.embeddings[idx] = new_embeddings[i]
                else:
                    docs_to_add.append(doc)
                    embeddings_to_add.append(new_embeddings[i])

            if docs_to_add:
                self.documents.extend(docs_to_add)
                self.embeddings = np.vstack(
                    [self.embeddings, np.array(embeddings_to_add)]
                )

        affected_groups = set()
        for doc in new_docs:
            for group in doc.collections:
                affected_groups.add(group)

        self._update_group_embeddings(affected_groups)

    def _update_group_embeddings(self, groups: set[str]):
        """Embeda grupos concatenando conteúdo."""
        for group in groups:
            group_docs = [
                doc for doc in self.documents if group in doc.collections
            ]

            if not group_docs:
                self.group_embeddings.pop(group, None)
                continue

            full_text = "\n\n".join([doc.content for doc in group_docs])
            emb = self.embedding_provider.safe_embed(full_text)
            if emb:
                self.group_embeddings[group] = np.array(emb)

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        metadata_filters: Optional[Dict] = None,
        collections: Optional[List[str]] = None,
    ) -> List[VectorSearchResult]:
        if self.embeddings is None or not self.documents:
            return []

        query_embedding = np.array(self.embedding_provider.embed_query(query))
        similarities = np.dot(self.embeddings, query_embedding)

        valid_indices = list(range(len(self.documents)))

        if collections is not None:
            valid_indices = [
                i
                for i in valid_indices
                if any(c in self.documents[i].collections for c in collections)
            ]

        if metadata_filters:
            valid_indices = [
                i
                for i in valid_indices
                if all(
                    self.documents[i].metadata.get(key) == value
                    for key, value in metadata_filters.items()
                )
            ]

        if not valid_indices:
            return []

        valid_similarities = [(i, similarities[i]) for i in valid_indices]
        valid_similarities.sort(key=lambda x: x[1], reverse=True)
        top_k = valid_similarities[:k]

        return [
            VectorSearchResult(
                document=self.documents[idx], score=float(score)
            )
            for idx, score in top_k
        ]

    def group_similarity_search(
        self,
        query: str,
        k: int = 3,
    ) -> List[VectorSearchResult]:
        if not self.group_embeddings:
            return []

        query_embedding = np.array(self.embedding_provider.embed_query(query))

        group_scores = [
            (group, float(np.dot(embedding, query_embedding)))
            for group, embedding in self.group_embeddings.items()
        ]
        group_scores.sort(key=lambda x: x[1], reverse=True)

        top_groups = group_scores[:k]

        results = []
        for group, score in top_groups:
            group_docs = [
                doc for doc in self.documents if group in doc.collections
            ]
            for doc in group_docs:
                results.append(VectorSearchResult(document=doc, score=score))

        return results

    def named_group_search(
        self,
        query: str,
        groups: List[List[str]],
        group_key: str = "id",
    ) -> List[VectorSearchResult]:
        """Busca pelo grupo mais similar à query.

        Para cada grupo (lista de identificadores), concatena o conteúdo de
        todos os seus documentos e embeda o resultado. Retorna os documentos
        do grupo que mais se aproxima da query.

        Parameters
        ----------
        group_key : str
            ``"id"`` (padrão) → compara com ``doc.id`` (universal para
            CSV, URL, arquivo, qualquer fonte).
            Qualquer outra string → compara com ``doc.metadata[group_key]``.
        """
        if not self.documents or not groups:
            return []

        query_embedding = np.array(self.embedding_provider.embed_query(query))

        def _doc_key(doc: "VectorDocument") -> str:  # type: ignore[name-defined]
            return (
                doc.id
                if group_key == "id"
                else (doc.metadata.get(group_key) or "")
            )

        best_score = -1.0
        best_group_ids: List[str] = []

        for group_ids in groups:
            group_docs = [
                doc for doc in self.documents if _doc_key(doc) in group_ids
            ]
            if not group_docs:
                continue

            full_text = "\n\n".join(doc.content for doc in group_docs)
            group_emb = self.embedding_provider.safe_embed(full_text)
            if not group_emb:
                continue

            score = float(np.dot(np.array(group_emb), query_embedding))
            if score > best_score:
                best_score = score
                best_group_ids = group_ids

        if not best_group_ids:
            return []

        winner_docs = [
            doc for doc in self.documents if _doc_key(doc) in best_group_ids
        ]
        return [
            VectorSearchResult(document=doc, score=best_score)
            for doc in winner_docs
        ]

    def get_all_documents(self) -> List[VectorSearchResult]:
        return [
            VectorSearchResult(document=doc, score=1.0)
            for doc in self.documents
        ]

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        data = {
            "embeddings": self.embeddings,
            "documents": [doc.model_dump() for doc in self.documents],
            "group_embeddings": self.group_embeddings,
        }

        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str) -> None:
        if not Path(path).exists():
            raise FileNotFoundError(f"Vector store não encontrado: {path}")

        with open(path, "rb") as f:
            data = pickle.load(f)

        self.embeddings = data["embeddings"]
        self.documents = [VectorDocument(**doc) for doc in data["documents"]]
        self.group_embeddings = data.get("group_embeddings", {})

    def get_documents_by_collection(
        self, collection_name: str
    ) -> List[VectorDocument]:
        return [
            doc for doc in self.documents if collection_name in doc.collections
        ]
