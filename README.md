# Mosqlimate Assistant

An AI-powered Retrieval-Augmented Generation (RAG) system designed to help users interact with the Mosqlimate platform. It provides expert guidance on documentation, code implementation using the `mosqlient` library, and specific information regarding the Infodengue-Mosqlimate Dengue Challenge (IMDC).

## Overview

**Mosqlimate Assistant** features a modular, multi-agent architecture capable of routing user queries to the most appropriate domain expert. It leverages an in-memory vector store for contextual document retrieval and supports multiple LLM providers.

### Key Features
- **Multi-Agent System**:
  - `docs_agent`: Expert on Mosqlimate platform documentation.
  - `code_agent`: Generates `mosqlient` Python/R code examples based on platform specs.
  - `imdc_agent`: Specialist on the Infodengue-Mosqlimate Dengue Challenge (rules, datasets, previous results).
- **Provider Abstraction**: Easily switch between LLM providers. Currently supports Gemini, OpenAI, Ollama (local/cloud), DeepSeek, and NVIDIA NIM.
- **RAG Capabilities**: Uses an in-memory vector store with **recursive chunking and max-pooling** — documents are split into small overlapping chunks for precise embedding, and the best chunk score represents each parent document during retrieval.
- **Indexing Strategies**: Supports `"content"` (default, recursive chunking) and `"keyword"` (metadata-based) indexing for flexible document ingestion.
- **Bilingual Support**: System prompts natively handle both Portuguese (`pt`) and English (`en`).
- **Caching**: HTTP responses are cached via `requests-cache` to speed up document ingestion.

## Prerequisites

- **Python**: 3.11+
- **Dependency Manager**: `uv` is recommended, though `pip` works.
- **Ollama**: Required locally if using the default `mxbai-embed-large` embedding model.

## Installation

Using `uv` (recommended):
```bash
uv sync
```

Using standard `pip`:
```bash
pip install -e .
```

## Quick Start

Generate a response using the pre-configured built-in pipeline. API keys should be set in environment variables or passed directly to the factory functions.

```python
from mosqlimate_assistant.main import assistant_pipeline

# The pipeline automatically routes to the appropriate agent (docs, code, or imdc)
answer = assistant_pipeline(
    question="O que é o projeto Mosqlimate e como posso usar seus dados?",
    google_api_key="<YOUR_GEMINI_API_KEY>",
    lang="pt" # Set to 'en' for English
)

print(answer)
```

For advanced use cases, you can construct the assistant manually with your provider of choice (e.g., using `create_openai_assistant` or `create_ollama_assistant`) and register specific agents and vector stores.

## Project Structure

- `mosqlimate_assistant/`
  - [`assistant.py`](mosqlimate_assistant/assistant.py): Primary entry point for creating configured `Assistant` instances.
  - [`agents.py`](mosqlimate_assistant/agents.py): `AgentExecutor` and `AgentOrchestrator` for RAG retrieval, context-limited fallback, and tool execution loops.
  - [`agent_cards.py`](mosqlimate_assistant/agent_cards.py): Declarative configuration for each agent, including tools, search strategy, and fallback thresholds.
  - [`main.py`](mosqlimate_assistant/main.py): Pre-configured pipelines mapping the `docs`, `code`, and `imdc` agents together.
  - [`providers.py`](mosqlimate_assistant/providers.py): LLM abstraction wrappers (OpenAI, Gemini, Ollama, DeepSeek, etc.).
  - [`embeddings.py`](mosqlimate_assistant/embeddings.py): Embedding interfaces with normalization and error handling.
  - [`vector_store.py`](mosqlimate_assistant/vector_store.py): In-memory `numpy`-backed vector database with chunk-level embeddings and max-pooling retrieval.
  - [`document_consumer.py`](mosqlimate_assistant/document_consumer.py): Document scraping, ingestion, recursive text chunking, and content enrichment pipeline.
  - [`prompts.py`](mosqlimate_assistant/prompts.py): Bilingual system prompts with strict anti-hallucination rules, document grounding, and API allowlists.
  - [`models.py`](mosqlimate_assistant/models.py): Core data structures (`VectorDocument`, `ChatMessage`, `ProviderResponse`, etc.).
  - [`settings.py`](mosqlimate_assistant/settings.py): Configuration constants for HTTP caching and default parameters.

## Development and Contribution

- **Type Hinting**: All code requires strict type hinting (`mypy`).
- **Formatting & Linting**: We use `black` for formatting, `isort` for imports, and `ruff` for linting.
- **Testing**: `pytest` for unit and integration testing.

```bash
# Run the test suite
pytest

# Auto-format and lint the codebase
black .
isort .
ruff check .
mypy .
```
