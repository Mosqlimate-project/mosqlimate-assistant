from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest
from langchain_core.documents import Document

from mosqlimate_assistant.agent import ChatModelFactory
from mosqlimate_assistant.assistant import (
    Assistant,
    create_ollama_assistant,
)
from mosqlimate_assistant.embeddings import BaseEmbeddingProvider
from mosqlimate_assistant.knowledge_base import (
    DocumentBlockConfig,
    MosqlimateKnowledgeBase,
)
from mosqlimate_assistant.main import build_mosqlimate_assistant
from mosqlimate_assistant.models import ProviderType


class DummyEmbeddingProvider(BaseEmbeddingProvider):
    def embed_query(self, text: str) -> list[float]:
        lowered = text.lower()
        if "dashboard" in lowered:
            return [1.0, 0.0]
        if "registry" in lowered:
            return [0.0, 1.0]
        return [0.5, 0.5]


def _make_kb(tmp_path: Path, lang: str = "pt") -> MosqlimateKnowledgeBase:
    documents = [
        Document(
            page_content="Dashboard metrics and WIS",
            metadata={
                "domain": "docs",
                "name": "vis_dashboard_scores",
                "url_link": "https://example.org/vis",
            },
        )
    ]
    return MosqlimateKnowledgeBase.from_langchain_documents(
        documents=documents,
        embedding_provider=DummyEmbeddingProvider(),
        blocks=[
            DocumentBlockConfig(
                key="visualize",
                description="Dashboard docs",
                domain="docs",
                names=frozenset({"vis_dashboard_scores"}),
            )
        ],
        storage_path=tmp_path / f"kb-{lang}",
        lang=lang,
    )


def test_assistant_requires_configured_tool_agent():
    assistant = Assistant(
        provider_type=ProviderType.GEMINI,
        provider_config={"api_key": "test", "model": "gemini"},
    )

    with pytest.raises(ValueError, match="Tool agent not configured"):
        assistant.query("Pergunta")


@pytest.mark.parametrize(
    ("callback", "args"),
    [
        (create_ollama_assistant, ()),
        (
            ChatModelFactory.create,
            (ProviderType.OLLAMA, {"model": "llama3.2:latest"}),
        ),
    ],
)
def test_ollama_chat_entrypoints_fail_fast(callback, args):
    with pytest.raises(NotImplementedError, match="OpenAI-compatible"):
        callback(*args)


def test_format_block_context_localizes_output(tmp_path: Path):
    pt_kb = _make_kb(tmp_path, lang="pt")
    en_kb = _make_kb(tmp_path, lang="en")

    pt_result = pt_kb.format_block_context("visualize", "dashboard")
    en_result = en_kb.format_block_context("visualize", "dashboard")

    assert "Bloco: visualize" in pt_result
    assert "[Trecho 1 | Words:" in pt_result
    assert "Título:" in pt_result

    assert "Block: visualize" in en_result
    assert "[Snippet 1 | Words:" in en_result
    assert "Title:" in en_result


def test_build_mosqlimate_assistant_ignores_compatibility_kwargs(
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}
    fake_kb = object()

    class FakeEmbeddingProvider:
        def __init__(self, model: str, base_url: str | None = None) -> None:
            captured["embedding_model"] = model
            captured["embedding_base_url"] = base_url

    def fake_load_or_build(**kwargs: object):
        captured["load_or_build_kwargs"] = kwargs
        return fake_kb

    def fake_configure(
        self: Assistant, knowledge_base: object, max_tool_iterations: int
    ) -> None:
        captured["configured_kb"] = knowledge_base
        captured["max_tool_iterations"] = max_tool_iterations
        self.knowledge_base = knowledge_base  # type: ignore[assignment]
        self.tool_agent = object()  # type: ignore[assignment]

    monkeypatch.setattr(
        "mosqlimate_assistant.main.OllamaEmbeddingProvider",
        FakeEmbeddingProvider,
    )
    monkeypatch.setattr(
        "mosqlimate_assistant.main.MosqlimateKnowledgeBase.load_or_build",
        fake_load_or_build,
    )
    monkeypatch.setattr(
        "mosqlimate_assistant.main.Assistant.configure_tool_agent",
        fake_configure,
    )

    assistant, kb1, kb2, kb3 = build_mosqlimate_assistant(
        google_api_key="test",
        docs_search_mode="group",
        code_search_scope="metadata",
        max_tool_iterations=7,
        lang="en",
    )

    assert assistant.knowledge_base is fake_kb
    assert kb1 is fake_kb and kb2 is fake_kb and kb3 is fake_kb
    assert captured["embedding_model"] == "mxbai-embed-large:latest"
    assert captured["embedding_base_url"] is None
    assert captured["configured_kb"] is fake_kb
    assert captured["max_tool_iterations"] == 7

    load_kwargs = cast(
        Mapping[str, object],
        captured["load_or_build_kwargs"],
    )
    assert load_kwargs["lang"] == "en"
    assert isinstance(load_kwargs["storage_path"], Path)
    assert load_kwargs["storage_path"].name == "en"
    assert isinstance(load_kwargs["blocks"], list)
    assert len(load_kwargs["blocks"]) > 0
    assert isinstance(load_kwargs["source_configs"], list)
    assert len(load_kwargs["source_configs"]) == 3


def test_pyproject_exposes_single_runtime_package():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    data = tomllib.loads(pyproject)

    packages = data["tool"]["setuptools"]["packages"]
    assert packages == ["mosqlimate_assistant"]
