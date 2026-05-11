"""Knowledge-base assembly and FAISS-backed retrieval helpers.

This module connects the document-ingestion pipeline to LangChain
documents and a persisted FAISS index. It also defines the document
block catalog used by the agent to search targeted slices of the
Mosqlimate documentation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter
from typing import List, Optional, Sequence

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from mosqlimate_assistant.document_consumer import (
    CSVLinkConsumer,
    DocumentManager,
)
from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.models import (
    DocumentBlockConfig,
    DocumentSourceConfig,
    VectorDocument,
)
from mosqlimate_assistant.monitoring import (
    elapsed_seconds,
    get_monitor_logger,
    log_event,
    preview_text,
)


class LangChainEmbeddingAdapter(Embeddings):
    """Wrap the existing embedding providers for LangChain vector stores."""

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embedding_provider.safe_embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self.embedding_provider.safe_embed(text)


class _CollectingVectorStore:
    """Capture VectorDocuments emitted by DocumentManager without indexing."""

    def __init__(self) -> None:
        self.documents: List[VectorDocument] = []

    def add_documents(self, documents: List[VectorDocument]) -> None:
        self.documents.extend(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        collections: Optional[List[str]] = None,
    ) -> list[VectorDocument]:
        """Satisfy the ``DocumentSink`` protocol for indexing-only pipelines."""
        del query, k, collections
        return []


class SourceDocumentPipeline:
    """Fetch and transform documents for a single configured source."""

    def __init__(self, source_config: DocumentSourceConfig) -> None:
        self.source_config = source_config
        self.logger = get_monitor_logger("knowledge_base")

    def collect_vector_documents(self) -> List[VectorDocument]:
        """Fetch source content and convert it into vector-ready documents."""
        start = perf_counter()
        collector = _CollectingVectorStore()
        manager = DocumentManager(collector)
        manager.add_consumer(
            CSVLinkConsumer(
                str(self.source_config.csv_path),
                self.source_config.link_column,
            )
        )
        manager.fetch_and_index_all(
            collections=[self.source_config.domain],
            id_key=self.source_config.id_key,
        )
        log_event(
            self.logger,
            "source_pipeline_completed",
            domain=self.source_config.domain,
            csv_path=str(self.source_config.csv_path),
            document_count=len(collector.documents),
            chunk_count=sum(len(doc.chunks) for doc in collector.documents),
            elapsed_seconds=elapsed_seconds(start),
        )
        return collector.documents


class LangChainDocumentFactory:
    """Convert ``VectorDocument`` objects into LangChain documents."""

    @staticmethod
    def from_vector_document(
        vector_doc: VectorDocument,
        domain: str,
    ) -> List[Document]:
        """Expand a vector document into one LangChain document per chunk."""
        metadata = dict(vector_doc.metadata)
        metadata["domain"] = domain
        metadata["source_id"] = vector_doc.id
        metadata["collections"] = list(vector_doc.collections)

        return [
            Document(
                page_content=chunk,
                metadata={
                    **metadata,
                    "chunk_index": idx,
                    "chunk_kind": "metadata" if idx == 0 else "content",
                },
            )
            for idx, chunk in enumerate(
                vector_doc.chunks or [vector_doc.content]
            )
        ]

    def from_vector_documents(
        self,
        vector_docs: Sequence[VectorDocument],
        domain: str,
    ) -> List[Document]:
        """Expand many vector documents into LangChain documents."""
        docs: List[Document] = []
        for vector_doc in vector_docs:
            docs.extend(self.from_vector_document(vector_doc, domain))
        return docs


class MosqlimateKnowledgeBase:
    """Shared FAISS index plus block-aware retrieval helpers."""

    def __init__(
        self,
        vector_store: FAISS,
        embeddings: LangChainEmbeddingAdapter,
        blocks: Sequence[DocumentBlockConfig],
        storage_path: Optional[Path] = None,
        lang: str = "pt",
    ) -> None:
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.storage_path = storage_path
        self.blocks = {block.key: block for block in blocks}
        self.lang = lang
        self.logger = get_monitor_logger("knowledge_base")

    @classmethod
    def from_langchain_documents(
        cls,
        documents: Sequence[Document],
        embedding_provider: BaseEmbeddingProvider,
        blocks: Sequence[DocumentBlockConfig],
        storage_path: Optional[Path] = None,
        lang: str = "pt",
    ) -> "MosqlimateKnowledgeBase":
        embeddings = LangChainEmbeddingAdapter(embedding_provider)
        vector_store = FAISS.from_documents(list(documents), embeddings)
        kb = cls(
            vector_store=vector_store,
            embeddings=embeddings,
            blocks=blocks,
            storage_path=storage_path,
            lang=lang,
        )
        if storage_path is not None:
            kb.save()
        return kb

    @classmethod
    def load_or_build(
        cls,
        storage_path: Path,
        embedding_provider: BaseEmbeddingProvider,
        blocks: Sequence[DocumentBlockConfig],
        source_configs: Sequence[DocumentSourceConfig],
        lang: str = "pt",
    ) -> "MosqlimateKnowledgeBase":
        embeddings = LangChainEmbeddingAdapter(embedding_provider)

        if cls._has_persisted_index(storage_path):
            return cls._load_existing(
                storage_path=storage_path,
                embeddings=embeddings,
                blocks=blocks,
                lang=lang,
            )

        if storage_path.exists():
            logger = get_monitor_logger("knowledge_base")
            log_event(
                logger,
                "knowledge_base_storage_incomplete",
                level=logging.WARNING,
                storage_path=str(storage_path),
            )

        return cls._build_new(
            storage_path=storage_path,
            embeddings=embeddings,
            blocks=blocks,
            source_configs=source_configs,
            lang=lang,
        )

    @classmethod
    def _load_existing(
        cls,
        storage_path: Path,
        embeddings: LangChainEmbeddingAdapter,
        blocks: Sequence[DocumentBlockConfig],
        lang: str,
    ) -> "MosqlimateKnowledgeBase":
        """Load a persisted FAISS index from disk."""
        start = perf_counter()
        vector_store = FAISS.load_local(
            folder_path=str(storage_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )
        kb = cls(
            vector_store=vector_store,
            embeddings=embeddings,
            blocks=blocks,
            storage_path=storage_path,
            lang=lang,
        )
        log_event(
            kb.logger,
            "knowledge_base_loaded",
            storage_path=str(storage_path),
            block_count=len(blocks),
            elapsed_seconds=elapsed_seconds(start),
        )
        return kb

    @classmethod
    def _build_new(
        cls,
        storage_path: Path,
        embeddings: LangChainEmbeddingAdapter,
        blocks: Sequence[DocumentBlockConfig],
        source_configs: Sequence[DocumentSourceConfig],
        lang: str,
    ) -> "MosqlimateKnowledgeBase":
        """Build a new FAISS index from configured sources."""
        start = perf_counter()
        documents = cls._build_langchain_documents(source_configs)
        if not documents:
            raise ValueError(
                "No documents were collected for the Mosqlimate knowledge "
                "base. The configured sources may be unavailable or empty."
            )
        vector_store = FAISS.from_documents(documents, embeddings)
        kb = cls(
            vector_store=vector_store,
            embeddings=embeddings,
            blocks=blocks,
            storage_path=storage_path,
            lang=lang,
        )
        kb.save()
        log_event(
            kb.logger,
            "knowledge_base_built",
            storage_path=str(storage_path),
            document_count=len(documents),
            block_count=len(blocks),
            elapsed_seconds=elapsed_seconds(start),
        )
        return kb

    @staticmethod
    def _has_persisted_index(storage_path: Path) -> bool:
        """Return whether a FAISS index looks complete on disk."""
        return (
            storage_path.is_dir()
            and (storage_path / "index.faiss").exists()
            and (storage_path / "index.pkl").exists()
        )

    @staticmethod
    def _build_langchain_documents(
        source_configs: Sequence[DocumentSourceConfig],
    ) -> List[Document]:
        factory = LangChainDocumentFactory()
        docs: List[Document] = []

        for config in source_configs:
            pipeline = SourceDocumentPipeline(config)
            vector_docs = pipeline.collect_vector_documents()
            docs.extend(
                factory.from_vector_documents(vector_docs, config.domain)
            )

        return docs

    def save(self) -> None:
        """Persist the FAISS index to disk."""
        if self.storage_path is None:
            return
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(self.storage_path))

    def search_block(
        self,
        block_key: str,
        query: str,
        k: int = 4,
        fetch_k: int = 16,
    ) -> List[Document]:
        """Search documents constrained to a single configured block."""
        if block_key not in self.blocks:
            raise ValueError(f"Unknown document block: {block_key}")

        block = self.blocks[block_key]
        start = perf_counter()
        docs = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=block.matches,
            fetch_k=max(fetch_k, k),
        )
        log_event(
            self.logger,
            "block_search_completed",
            block_key=block_key,
            query_preview=preview_text(query),
            result_count=len(docs),
            result_names=[
                doc.metadata.get("name") or doc.metadata.get("source_id")
                for doc in docs
            ],
            elapsed_seconds=elapsed_seconds(start),
        )
        return docs

    def format_block_context(
        self,
        block_key: str,
        query: str,
        k: int = 4,
    ) -> str:
        """Format retrieved block content for the agent tool response."""
        docs = self.search_block(block_key, query, k=k)
        labels = {
            "block": "Block" if self.lang == "en" else "Bloco",
            "snippet": "Snippet" if self.lang == "en" else "Trecho",
            "title": "Title" if self.lang == "en" else "Título",
            "url": "URL",
            "document": "Document" if self.lang == "en" else "Documento",
            "empty": (
                "No relevant snippets found in this block."
                if self.lang == "en"
                else "Nenhum trecho relevante encontrado neste bloco."
            ),
            "empty_generic": (
                "No relevant snippets found."
                if self.lang == "en"
                else "Nenhum trecho relevante encontrado."
            ),
        }
        if not docs:
            return labels["empty"] if block_key else labels["empty_generic"]

        parts: List[str] = [f"{labels['block']}: {block_key}"]
        for idx, doc in enumerate(docs, start=1):
            metadata = doc.metadata
            title = (
                metadata.get("name")
                or metadata.get("source_id")
                or labels["document"]
            )
            url = (
                metadata.get("url_link")
                or metadata.get("markdown_link")
                or metadata.get("url")
                or ""
            )
            word_count = len(doc.page_content.split())
            parts.append(
                "\n".join(
                    [
                        f"[{labels['snippet']} {idx} | Words: {word_count}]",
                        f"{labels['title']}: {title}",
                        f"{labels['url']}: {url}",
                        doc.page_content.strip(),
                    ]
                ).strip()
            )
        return "\n\n".join(parts)

    def available_blocks(self) -> List[DocumentBlockConfig]:
        """Return blocks in declaration order."""
        return list(self.blocks.values())


def build_default_blocks(lang: str = "pt") -> List[DocumentBlockConfig]:
    """Return the default Mosqlimate documentation block catalog."""
    descriptions = {
        "platform_overview": (
            "Visão geral institucional e funcional do projeto Mosqlimate, incluindo missão, produtos,\n"
            "equipe, OviCounter, autenticação básica e contexto geral de uso da plataforma.\n"
            "Use este bloco para perguntas introdutórias, acesso inicial e panorama amplo do ecossistema."
            if lang == "pt"
            else "Institutional and functional overview of the Mosqlimate project, including mission, products,\n"
            "team, OviCounter, basic authentication, and the platform's general context.\n"
            "Use this block for introductory questions, first access, and a broad ecosystem overview."
        ),
        "platform_epi_data": (
            "Datastore epidemiológico do Mosqlimate, cobrindo estrutura geral da plataforma de dados,\n"
            "InfoDengue, EpiScanner, variáveis, filtros, granularidade e interpretação dos dados.\n"
            "Use este bloco para perguntas sobre incidência, séries epidemiológicas e parâmetros de vigilância."
            if lang == "pt"
            else "Mosqlimate epidemiological datastore, covering the general data-platform structure,\n"
            "InfoDengue, EpiScanner, variables, filters, data granularity, and interpretation.\n"
            "Use this block for questions about incidence, epidemiological series, and surveillance parameters."
        ),
        "platform_env_data": (
            "Datastore ambiental e vetorial do Mosqlimate, cobrindo estrutura do datastore,\n"
            "clima diário/semanal, monitoramento de mosquitos e contexto do OviCounter.\n"
            "Use este bloco para clima, abundância vetorial, variáveis ambientais e filtros relacionados."
            if lang == "pt"
            else "Mosqlimate environmental and vector datastore, covering datastore structure,\n"
            "daily/weekly climate, mosquito monitoring, and OviCounter context.\n"
            "Use this block for climate, vector abundance, environmental variables, and related filters."
        ),
        "platform_registry_models": (
            "Model Registry com foco em registro e consulta de modelos, incluindo visão geral do registry,\n"
            "metadados, campos obrigatórios, endpoints relevantes e relação com previsões.\n"
            "Use este bloco para entender como descrever, registrar e consultar modelos publicados."
            if lang == "pt"
            else "Model Registry focused on model registration and querying, including registry overview,\n"
            "metadata, required fields, relevant endpoints, and relation to predictions.\n"
            "Use this block to understand how to describe, register, and query published models."
        ),
        "platform_registry_predictions": (
            "Model Registry com foco em submissão e consulta de previsões, incluindo visão geral do registry,\n"
            "formatos esperados, payloads, restrições temporais e vínculo com modelos.\n"
            "Use este bloco para perguntas sobre upload, listagem e estrutura das previsões."
            if lang == "pt"
            else "Model Registry focused on prediction submission and querying, including registry overview,\n"
            "expected formats, payloads, temporal constraints, and links to models.\n"
            "Use this block for questions about upload, listing, and prediction structure."
        ),
        "platform_visualize": (
            "Documentação consolidada dos dashboards e métricas de visualização do Mosqlimate,\n"
            "incluindo navegação, interpretação dos gráficos, relação com previsões e significado de MAE, WIS e CRPS.\n"
            "Use este bloco para leitura de rankings, gráficos, tabelas e métricas comparativas."
            if lang == "pt"
            else "Consolidated documentation for Mosqlimate dashboards and visualization metrics,\n"
            "including navigation, chart interpretation, links to predictions, and the meaning of MAE, WIS, and CRPS.\n"
            "Use this block for reading rankings, charts, tables, and comparative metrics."
        ),
        "mosqlient_getting_started": (
            "Introdução consolidada ao mosqlient com visão geral da biblioteca, CLI,\n"
            "exemplos iniciais de uso e integração com R.\n"
            "Use este bloco para onboarding, primeiros comandos e orientação geral de uso."
            if lang == "pt"
            else "Consolidated introduction to mosqlient with library overview, CLI,\n"
            "initial usage examples, and R integration.\n"
            "Use this block for onboarding, first commands, and general usage guidance."
        ),
        "mosqlient_datastore": (
            "Uso do mosqlient para consultar dados do datastore, incluindo visão geral,\n"
            "exemplos práticos, referências, CLI, Infodengue e clima.\n"
            "Use este bloco para perguntas sobre leitura de dados, parâmetros, filtros e exemplos de código."
            if lang == "pt"
            else "Using mosqlient to query datastore data, including overview,\n"
            "practical examples, references, CLI, InfoDengue, and climate.\n"
            "Use this block for questions about data reads, parameters, filters, and code examples."
        ),
        "mosqlient_registry": (
            "Uso do mosqlient para registrar modelos e enviar ou consultar previsões,\n"
            "incluindo visão geral da biblioteca, tutorial de registry e referência das operações.\n"
            "Use este bloco para fluxos programáticos de modelos, previsões e automação via cliente."
            if lang == "pt"
            else "Using mosqlient to register models and submit or query predictions,\n"
            "including library overview, registry tutorial, and operation reference.\n"
            "Use this block for programmatic model, prediction, and client automation workflows."
        ),
        "mosqlient_scoring_tutorial": (
            "Tutoriais de avaliação e scoring de previsões com mosqlient,\n"
            "conectando workflow de modelagem, comparação de modelos e interpretação.\n"
            "Use este bloco quando a pergunta pedir explicação guiada ou passo a passo de scoring."
            if lang == "pt"
            else "Tutorials for forecast evaluation and scoring with mosqlient,\n"
            "connecting modeling workflow, model comparison, and interpretation.\n"
            "Use this block when the question asks for guided or step-by-step scoring explanations."
        ),
        "mosqlient_score_reference": (
            "Referência consolidada das funções de score e métricas probabilísticas do mosqlient,\n"
            "com foco em assinaturas, parâmetros, retornos e relações entre métricas.\n"
            "Use este bloco para consultas técnicas detalhadas sobre WIS, CRPS, log score e funções afins."
            if lang == "pt"
            else "Consolidated reference for mosqlient scoring functions and probabilistic metrics,\n"
            "focusing on signatures, parameters, returns, and relations across metrics.\n"
            "Use this block for detailed technical questions about WIS, CRPS, log score, and related functions."
        ),
        "mosqlient_forecast_baseline": (
            "Tutoriais e referências para modelos base de previsão com mosqlient,\n"
            "incluindo forecast simples, baseline ARIMA e apoio de otimização de predições.\n"
            "Use este bloco para exemplos de modelagem inicial, construção de baseline e ajustes práticos."
            if lang == "pt"
            else "Tutorials and references for baseline forecasting models with mosqlient,\n"
            "including simple forecasting, ARIMA baselines, and prediction-optimization support.\n"
            "Use this block for starter modeling examples, baseline construction, and practical tuning."
        ),
        "mosqlient_ensemble": (
            "Tutoriais e referências para construção de ensembles com mosqlient,\n"
            "incluindo composição de modelos, avaliação comparativa e interpretação de resultados.\n"
            "Use este bloco para perguntas sobre combinação de previsões e leitura de desempenho conjunto."
            if lang == "pt"
            else "Tutorials and references for building ensembles with mosqlient,\n"
            "including model composition, comparative evaluation, and result interpretation.\n"
            "Use this block for questions about combining forecasts and reading joint performance."
        ),
        "mosqlient_prediction_optimize": (
            "Referência de otimização de predições com mosqlient,\n"
            "apoiada por material de forecast e scoring relacionado.\n"
            "Use este bloco para tuning técnico, pós-processamento e refinamento das saídas do modelo."
            if lang == "pt"
            else "Prediction optimization reference with mosqlient,\n"
            "supported by related forecasting and scoring material.\n"
            "Use this block for technical tuning, post-processing, and model-output refinement."
        ),
        "imdc_overview": (
            "Visão geral robusta do IMDC/Sprint 2025, cobrindo contexto, regras, cronograma,\n"
            "instruções, registro, organização e páginas públicas de resultados.\n"
            "Use este bloco para participação no desafio, visão geral operacional e perguntas de alto nível."
            if lang == "pt"
            else "Robust overview of the 2025 IMDC/Sprint, covering context, rules, schedule,\n"
            "instructions, registration, organization, and public results pages.\n"
            "Use this block for challenge participation, operational overview, and high-level questions."
        ),
        "imdc_data": (
            "Datasets, variáveis-alvo e documentação técnica de dados do IMDC/Sprint 2025,\n"
            "com apoio das instruções e do sprint quando necessário para interpretar o uso dos dados.\n"
            "Use este bloco para bases, alvos, formato das previsões e requisitos técnicos do desafio."
            if lang == "pt"
            else "Datasets, target variables, and technical data documentation for the 2025 IMDC/Sprint,\n"
            "supported by instructions and sprint context when needed to interpret data usage.\n"
            "Use this block for datasets, targets, forecast format, and technical challenge requirements."
        ),
    }

    return [
        DocumentBlockConfig(
            key="platform_overview",
            description=descriptions["platform_overview"],
            domain="docs",
            names=frozenset(
                {
                    "project_main",
                    "project_ovicounter",
                    "project_products",
                    "project_team",
                    "data_platform",
                    "uid_key",
                }
            ),
        ),
        DocumentBlockConfig(
            key="platform_epi_data",
            description=descriptions["platform_epi_data"],
            domain="docs",
            names=frozenset(
                {
                    "data_platform",
                    "datastore_base",
                    "datastore_infodengue",
                    "datastore_episcanner",
                }
            ),
        ),
        DocumentBlockConfig(
            key="platform_env_data",
            description=descriptions["platform_env_data"],
            domain="docs",
            names=frozenset(
                {
                    "data_platform",
                    "datastore_climate",
                    "datastore_climate_weekly",
                    "datastore_mosquito",
                    "project_ovicounter",
                }
            ),
        ),
        DocumentBlockConfig(
            key="platform_registry_models",
            description=descriptions["platform_registry_models"],
            domain="docs",
            names=frozenset(
                {
                    "registry_base",
                    "registry_models_get",
                    "registry_models_post",
                    "registry_predictions_get",
                }
            ),
        ),
        DocumentBlockConfig(
            key="platform_registry_predictions",
            description=descriptions["platform_registry_predictions"],
            domain="docs",
            names=frozenset(
                {
                    "registry_base",
                    "registry_models_get",
                    "registry_predictions_get",
                    "registry_predictions_post",
                }
            ),
        ),
        DocumentBlockConfig(
            key="platform_visualize",
            description=descriptions["platform_visualize"],
            domain="docs",
            names=frozenset(
                {
                    "vis_dashboard_how_to_use",
                    "vis_dashboard_scores",
                    "vis_dashboard_details",
                    "registry_predictions_get",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_getting_started",
            description=descriptions["mosqlient_getting_started"],
            domain="code",
            names=frozenset(
                {
                    "Overview",
                    "Reference - CLI",
                    "Tutorial - Datastore",
                    "Tutorial - Using from R",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_datastore",
            description=descriptions["mosqlient_datastore"],
            domain="code",
            names=frozenset(
                {
                    "Overview",
                    "Tutorial - Datastore",
                    "Reference - Infodengue data",
                    "Reference - Climate data",
                    "Reference - CLI",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_registry",
            description=descriptions["mosqlient_registry"],
            domain="code",
            names=frozenset(
                {
                    "Overview",
                    "Tutorial - Registry",
                    "Reference - Get, post and delete models",
                    "Reference - Get, post and delete predictions",
                    "Reference - CLI",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_scoring_tutorial",
            description=descriptions["mosqlient_scoring_tutorial"],
            domain="code",
            names=frozenset(
                {
                    "Tutorial - Model Scoring",
                    "Tutorial - Simple forecast model",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_score_reference",
            description=descriptions["mosqlient_score_reference"],
            domain="code",
            names=frozenset(
                {
                    "Tutorial - Model Scoring",
                    "Reference - Score",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_forecast_baseline",
            description=descriptions["mosqlient_forecast_baseline"],
            domain="code",
            names=frozenset(
                {
                    "Tutorial - Simple forecast model",
                    "Reference - Baseline Arima",
                    "Reference - Prediction optimize",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_ensemble",
            description=descriptions["mosqlient_ensemble"],
            domain="code",
            names=frozenset(
                {
                    "Tutorial - Model Scoring",
                    "Tutorial - Ensemble predictions",
                    "Reference - Ensemble",
                    "Reference - Score",
                }
            ),
        ),
        DocumentBlockConfig(
            key="mosqlient_prediction_optimize",
            description=descriptions["mosqlient_prediction_optimize"],
            domain="code",
            names=frozenset(
                {
                    "Reference - Baseline Arima",
                    "Reference - Score",
                    "Reference - Prediction optimize",
                }
            ),
        ),
        DocumentBlockConfig(
            key="imdc_overview",
            description=descriptions["imdc_overview"],
            domain="imdc",
            url_fragments=frozenset(
                {
                    "/content/_index.md",
                    "/content/about/index.md",
                    "/content/calendar/index.md",
                    "/content/sprint/2025/index.md",
                    "/content/instructions/_index.md",
                    "/content/instructions/2025/index.md",
                    "/content/registration/index.md",
                    "/content/organize/index.md",
                    "/content/results/2025/index.md",
                    "/content/publications/index.md",
                }
            ),
        ),
        DocumentBlockConfig(
            key="imdc_data",
            description=descriptions["imdc_data"],
            domain="imdc",
            url_fragments=frozenset(
                {
                    "/content/calendar/index.md",
                    "/content/data/_index.md",
                    "/content/data/2025/index.md",
                    "/content/instructions/2025/index.md",
                    "/content/sprint/2025/index.md",
                }
            ),
        ),
    ]
