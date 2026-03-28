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
from typing import Dict, List, Literal, Optional, Set

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
        search_mode: Literal["metadata", "content", "both"] = "both",
    ) -> List[VectorSearchResult]:
        """Perform a similarity search for a given query over individual documents.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top results to return. Defaults to 3.
            metadata_filters (Optional[Dict], optional): Filters to apply based on metadata. Defaults to None.
            collections (Optional[List[str]], optional): Collections to restrict the search to. Defaults to None.
            search_mode (Literal["metadata", "content", "both"], optional):
                "metadata" limits search to the first chunk (keywords/title).
                "content" ignores the first chunk.
                "both" considers all chunks. Defaults to "both".

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
    """Concrete implementation of a vector store using numpy arrays in memory.

    Internally, each document is split into chunks and each chunk gets its
    own embedding row. The ``chunk_to_doc_idx`` list maps every embedding
    row back to its parent document index in ``self.documents``.
    """

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        """Initialize the InMemoryVectorStore.

        Args:
            embedding_provider (BaseEmbeddingProvider): The provider used to generate vector embeddings.

        """
        self.embedding_provider = embedding_provider
        self.documents: List[VectorDocument] = []
        self.embeddings: Optional[np.ndarray] = None
        self.chunk_to_doc_idx: List[int] = []
        self.group_embeddings: Dict[str, np.ndarray] = {}

    def _embed_doc_chunks(self, doc: VectorDocument) -> List[List[float]]:
        """Embed each chunk of a document, falling back to full content.

        Args:
            doc (VectorDocument): Document whose chunks to embed.

        Returns:
            List of embedding vectors (one per successfully embedded chunk).

        """
        chunks = doc.chunks if doc.chunks else [doc.content]
        embeddings: List[List[float]] = []
        for chunk in chunks:
            emb = self.embedding_provider.safe_embed(chunk)
            if emb:
                embeddings.append(emb)
        return embeddings

    def add_documents(self, documents: List[VectorDocument]) -> None:
        """Add a list of documents to the in-memory vector store and update embeddings.

        Each document's chunks are individually embedded. The flat embedding
        matrix maps back to parent documents via ``chunk_to_doc_idx``.

        Args:
            documents (List[VectorDocument]): List of VectorDocument objects to add.

        """
        if not documents:
            return

        if self.embeddings is not None and self.documents:
            self._merge_into_existing(documents)
        else:
            all_embs: List[List[float]] = []
            valid_docs: List[VectorDocument] = []
            chunk_map: List[int] = []

            for doc in documents:
                chunk_embs = self._embed_doc_chunks(doc)
                if chunk_embs:
                    doc_idx = len(valid_docs)
                    valid_docs.append(doc)
                    for emb in chunk_embs:
                        all_embs.append(emb)
                        chunk_map.append(doc_idx)

            if not all_embs:
                return

            self.documents = valid_docs
            self.embeddings = np.array(all_embs)
            self.chunk_to_doc_idx = chunk_map

        affected_groups: Set[str] = set()
        for doc in documents:
            for group in doc.collections:
                affected_groups.add(group)

        self._update_group_embeddings(affected_groups)

    def _merge_into_existing(
        self,
        new_docs: List[VectorDocument],
    ) -> None:
        """Merge new documents into existing storage, handling chunk-level rows.

        For updated documents, old chunk rows are removed and new ones inserted.
        For new documents, chunk rows are appended.

        Args:
            new_docs (List[VectorDocument]): List of newly added documents.

        """
        assert self.embeddings is not None
        existing_ids = {doc.id: i for i, doc in enumerate(self.documents)}

        # Collect indices of chunk rows to remove (for updated docs)
        rows_to_remove: List[int] = []
        updated_doc_indices: List[int] = []

        for doc in new_docs:
            if doc.id in existing_ids:
                doc_idx = existing_ids[doc.id]
                updated_doc_indices.append(doc_idx)
                rows_to_remove.extend(
                    r
                    for r, d in enumerate(self.chunk_to_doc_idx)
                    if d == doc_idx
                )

        # Remove old chunk rows
        if rows_to_remove:
            keep_mask = np.ones(len(self.chunk_to_doc_idx), dtype=bool)
            keep_mask[rows_to_remove] = False
            self.embeddings = self.embeddings[keep_mask]
            self.chunk_to_doc_idx = [
                d for r, d in enumerate(self.chunk_to_doc_idx) if keep_mask[r]
            ]

        # Process each new doc
        embs_to_add: List[List[float]] = []
        map_to_add: List[int] = []

        for doc in new_docs:
            if doc.id in existing_ids:
                idx = existing_ids[doc.id]
                existing_doc = self.documents[idx]

                doc.collections = list(
                    set(existing_doc.collections) | set(doc.collections)
                )
                doc.metadata = {**existing_doc.metadata, **doc.metadata}

                self.documents[idx] = doc
                target_idx = idx
            else:
                target_idx = len(self.documents)
                self.documents.append(doc)

            chunk_embs = self._embed_doc_chunks(doc)
            for emb in chunk_embs:
                embs_to_add.append(emb)
                map_to_add.append(target_idx)

        if embs_to_add:
            new_emb_arr = np.array(embs_to_add)
            if self.embeddings is not None and len(self.embeddings) > 0:
                self.embeddings = np.vstack([self.embeddings, new_emb_arr])
            else:
                self.embeddings = new_emb_arr
            self.chunk_to_doc_idx.extend(map_to_add)

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
        search_mode: Literal["metadata", "content", "both"] = "both",
    ) -> List[VectorSearchResult]:
        """Perform a max-pooling similarity search over document chunks.

        Computes cosine similarity for every chunk, then groups scores by
        parent document and keeps only the maximum chunk score per document.

        Args:
            query (str): The search query text.
            k (int, optional): Number of top results to return. Defaults to 3.
            metadata_filters (Optional[Dict], optional): Filters to apply based on metadata. Defaults to None.
            collections (Optional[List[str]], optional): Collections to restrict the search to. Defaults to None.
            search_mode (Literal["metadata", "content", "both"], optional):
                Define which chunks to consider. Defaults to "both".

        Returns:
            List[VectorSearchResult]: Ordered list of search results.

        """
        if self.embeddings is None or not self.documents:
            return []

        query_embedding = np.array(self.embedding_provider.embed_query(query))
        chunk_similarities = np.dot(self.embeddings, query_embedding)

        # Apply search_mode filtering via chunk mapping
        # Chunk 0 of each document is meta, others are content.
        # We need to find which chunk indices correspond to chunk position in document.
        valid_chunk_mask = np.ones(len(self.chunk_to_doc_idx), dtype=bool)

        if search_mode != "both":
            current_doc_id = -1
            current_chunk_pos = -1
            for i, doc_idx in enumerate(self.chunk_to_doc_idx):
                if doc_idx != current_doc_id:
                    current_doc_id = doc_idx
                    current_chunk_pos = 0
                else:
                    current_chunk_pos += 1

                if search_mode == "metadata" and current_chunk_pos != 0:
                    valid_chunk_mask[i] = False
                elif search_mode == "content" and current_chunk_pos == 0:
                    valid_chunk_mask[i] = False

        # Max-pooling: group chunk scores by parent document
        doc_max_scores: Dict[int, float] = {}
        for chunk_idx, score in enumerate(chunk_similarities):
            if not valid_chunk_mask[chunk_idx]:
                continue

            doc_idx = self.chunk_to_doc_idx[chunk_idx]
            if (
                doc_idx not in doc_max_scores
                or score > doc_max_scores[doc_idx]
            ):
                doc_max_scores[doc_idx] = float(score)

        # Apply filters
        valid_indices = set(doc_max_scores.keys())

        if collections is not None:
            valid_indices = {
                i
                for i in valid_indices
                if any(c in self.documents[i].collections for c in collections)
            }

        if metadata_filters:
            valid_indices = {
                i
                for i in valid_indices
                if all(
                    self.documents[i].metadata.get(key) == value
                    for key, value in metadata_filters.items()
                )
            }

        if not valid_indices:
            return []

        scored = [(idx, doc_max_scores[idx]) for idx in valid_indices]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_k = scored[:k]

        return [
            VectorSearchResult(document=self.documents[idx], score=score)
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

        def _doc_key(doc: "VectorDocument") -> str:  # type: ignore[name-defined]
            return (
                doc.id
                if group_key == "id"
                else (doc.metadata.get(group_key) or "")
            )

        best_group_ids: List[str] = []
        best_scores: List[float] = []  # Top scores for tie-breaking

        # Get individual doc similarities first to avoid repeated work
        doc_similarities: Dict[str, float] = {}
        # We reuse similarity_search logic (max-pooling) but for all docs
        all_results = self.similarity_search(
            query, k=len(self.documents), search_mode="both"
        )
        for res in all_results:
            doc_similarities[res.document.id] = res.score

        for group_ids in groups:
            # Get scores of all docs in this group that actually exist in store
            group_doc_scores = sorted(
                [
                    doc_similarities[did]
                    for did in group_ids
                    if did in doc_similarities
                ],
                reverse=True,
            )

            if not group_doc_scores:
                continue

            # Compare this group with the current best group
            is_better = False
            if not best_scores:
                is_better = True
            else:
                # Compare step by step: best doc, then 2nd best, etc.
                for s1, s2 in zip(group_doc_scores, best_scores):
                    if s1 > s2 + 1e-6:  # Tolerance for float comparison
                        is_better = True
                        break
                    elif s2 > s1 + 1e-6:
                        break
                else:
                    # If all existing scores are equal, group with more documents wins
                    if len(group_doc_scores) > len(best_scores):
                        is_better = True

            if is_better:
                best_group_ids = group_ids
                best_scores = group_doc_scores
                best_score = group_doc_scores[0]

        if not best_group_ids:
            return []

        # Return documents that are actually in the winning group
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
            "chunk_to_doc_idx": self.chunk_to_doc_idx,
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
        self.chunk_to_doc_idx = data.get("chunk_to_doc_idx", [])

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
