"""In-memory vector database for document storage and retrieval.

Provides an abstract interface (``BaseVectorStore``) and a concrete
``InMemoryVectorStore`` implementation that supports multiple search
strategies:

- **unitary**: standard cosine-similarity search over individual documents.
- **group**: searches by pre-computed collection-level embeddings.
- **named_group**: selects the best-matching named group of documents.

Documents can be organized into collections, persisted to disk via
pickle, and filtered by metadata.

Classes:
    BaseVectorStore: Abstract interface for vector stores.
    InMemoryVectorStore: NumPy-backed in-memory implementation.
"""

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.models import VectorDocument, VectorSearchResult


class BaseVectorStore(ABC):
    """Abstract interface defining the contract for vector stores."""

    @abstractmethod
    def add_documents(self, documents: List[VectorDocument]) -> None:
        """Add a list of documents to the vector store.

        Args:
            documents (List[VectorDocument]): Documents to be added.

        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 3,
        metadata_filters: Optional[Dict] = None,
        collections: Optional[List[str]] = None,
    ) -> List[VectorSearchResult]:
        """Perform a similarity search for a given query over individual documents.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top results to return. Defaults to 3.
            metadata_filters (Optional[Dict], optional): Filters to apply based on metadata. Defaults to None.
            collections (Optional[List[str]], optional): Collections to restrict the search to. Defaults to None.

        Returns:
            List[VectorSearchResult]: List of search results with similarity scores.

        """
        pass

    @abstractmethod
    def group_similarity_search(
        self,
        query: str,
        k: int = 3,
    ) -> List[VectorSearchResult]:
        """Perform a similarity search across pre-computed collection-level embeddings.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top group results to consider. Defaults to 3.

        Returns:
            List[VectorSearchResult]: Documents belonging to the top matching groups.

        """
        pass

    @abstractmethod
    def named_group_search(
        self,
        query: str,
        groups: List[List[str]],
        group_key: str = "id",
    ) -> List[VectorSearchResult]:
        """Select the best-matching named group of documents.

        Args:
            query (str): The search query text.
            groups (List[List[str]]): List of grouped metadata values.
            group_key (str, optional): Metadata key defining the groups. Defaults to "id".

        Returns:
            List[VectorSearchResult]: Documents belonging to the single best matching group.

        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[VectorSearchResult]:
        """Retrieve all documents from the vector store.

        Returns:
            List[VectorSearchResult]: All stored documents with a default score.

        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist the vector store to disk.

        Args:
            path (str): File path to save the vector store.

        """
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """Load the vector store from disk.

        Args:
            path (str): File path to load the vector store from.

        """
        pass

    @abstractmethod
    def get_documents_by_collection(
        self, collection_name: str
    ) -> List[VectorDocument]:
        """Retrieve all documents belonging to a specified collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            List[VectorDocument]: List of documents in the collection.

        """
        pass


class InMemoryVectorStore(BaseVectorStore):
    """Concrete implementation of a vector store using numpy arrays in memory."""

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        """Initialize the InMemoryVectorStore.

        Args:
            embedding_provider (BaseEmbeddingProvider): The provider used to generate vector embeddings.

        """
        self.embedding_provider = embedding_provider
        self.documents: List[VectorDocument] = []
        self.embeddings: Optional[np.ndarray] = None
        self.group_embeddings: Dict[str, np.ndarray] = {}

    def add_documents(self, documents: List[VectorDocument]) -> None:
        """Add a list of documents to the in-memory vector store and update embeddings.

        Args:
            documents (List[VectorDocument]): List of VectorDocument objects to add.

        """
        if not documents:
            return

        paired: List[Tuple[VectorDocument, List[float]]] = []
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
            self._merge_into_existing(new_docs, new_embeddings)

        affected_groups: Set[str] = set()
        for doc in new_docs:
            for group in doc.collections:
                affected_groups.add(group)

        self._update_group_embeddings(affected_groups)

    def _merge_into_existing(
        self,
        new_docs: List[VectorDocument],
        new_embeddings: np.ndarray,
    ) -> None:
        """Merge new documents into existing storage or update them if they already exist.

        Args:
            new_docs (List[VectorDocument]): List of newly added documents.
            new_embeddings (np.ndarray): Embeddings array corresponding to the new documents.

        """
        assert self.embeddings is not None
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
                doc.metadata = {**existing_doc.metadata, **doc.metadata}

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

    def _update_group_embeddings(self, groups: Set[str]):
        """Recalculate and update the embeddings for modified document groups.

        Args:
            groups (Set[str]): Set of group names that need embedding updates.

        """
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
        """Perform a standard cosine-similarity search over individual documents.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top results to return. Defaults to 3.
            metadata_filters (Optional[Dict], optional): Filters to apply based on metadata. Defaults to None.
            collections (Optional[List[str]], optional): Collections to restrict the search to. Defaults to None.

        Returns:
            List[VectorSearchResult]: Ordered list of search results.

        """
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
        """Search by finding the most similar pre-computed group collection embeddings.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top groups to retrieve. Defaults to 3.

        Returns:
            List[VectorSearchResult]: Documents belonging to the best-matching groups.

        """
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
        """Determine and return documents from the single best-matching named group.

        Args:
            query (str): The search query text.
            groups (List[List[str]]): Nested list specifying custom groups.
            group_key (str, optional): Metadata key defining the groups. Defaults to "id".

        Returns:
            List[VectorSearchResult]: Documents representing the single best group match.

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
        """Retrieve all currently stored documents with a maximum similarity score.

        Returns:
            List[VectorSearchResult]: All contents of the vector store.

        """
        return [
            VectorSearchResult(document=doc, score=1.0)
            for doc in self.documents
        ]

    def save(self, path: str) -> None:
        """Save the in-memory vector store state to a local file using pickle.

        Args:
            path (str): Destination file path for serialization.

        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        data = {
            "embeddings": self.embeddings,
            "documents": [doc.model_dump() for doc in self.documents],
            "group_embeddings": self.group_embeddings,
        }

        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str) -> None:
        """Load the vector store state from a pickled file.

        Args:
            path (str): Source file path to load from.

        Raises:
            FileNotFoundError: If the specified path does not exist.

        """
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
        """Filter and retrieve stored documents for a specific collection.

        Args:
            collection_name (str): Name of the target collection.

        Returns:
            List[VectorDocument]: Sub-list of documents matching the collection name.

        """
        return [
            doc for doc in self.documents if collection_name in doc.collections
        ]
