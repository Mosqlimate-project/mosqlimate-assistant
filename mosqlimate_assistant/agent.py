"""Single-agent orchestration for tool-driven Mosqlimate answers.

This module contains the LangChain-based runtime that converts message
history into prompts, exposes document-block retrieval tools, calls the
chat model, and normalizes the final response payload returned by the
assistant.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

from mosqlimate_assistant.knowledge_base import (
    DocumentBlockConfig,
    MosqlimateKnowledgeBase,
)
from mosqlimate_assistant.models import (
    AgentRunResult,
    ChatMessage,
    ProviderConfig,
    ProviderType,
    TokenUsage,
    ToolCallRecord,
)
from mosqlimate_assistant.monitoring import (
    elapsed_seconds,
    extract_langchain_response_metadata,
    extract_langchain_usage,
    get_monitor_logger,
    log_event,
    preview_text,
)
from mosqlimate_assistant.prompts import get_single_agent_prompt


class BlockSearchInput(BaseModel):
    """Input schema shared by all document-block tools."""

    question: str = Field(
        ...,
        description=(
            "Pergunta ou subconsulta a ser buscada neste bloco documental."
        ),
    )


class BatchBlockSearchItem(BaseModel):
    """One block search request inside a batch call."""

    block_key: str = Field(
        ...,
        description="Chave do bloco documental que deve ser consultado.",
    )
    question: str = Field(
        ...,
        description="Pergunta ou subconsulta específica para esse bloco.",
    )


class BatchBlockSearchInput(BaseModel):
    """Input schema for searching multiple blocks in one tool call."""

    requests: List[BatchBlockSearchItem] = Field(
        ...,
        description=(
            "Lista de buscas por bloco. Use quando precisar consultar vários "
            "blocos documentais em uma única chamada."
        ),
        min_length=2,
        max_length=6,
    )


class ChatMessageAdapter:
    """Convert external chat messages to LangChain message objects."""

    @staticmethod
    def history_to_messages(
        message_history: Optional[List[ChatMessage]],
    ) -> List[BaseMessage]:
        converted: List[BaseMessage] = []
        for msg in message_history or []:
            if msg.role == "assistant":
                converted.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                converted.append(SystemMessage(content=msg.content))
            else:
                converted.append(HumanMessage(content=msg.content))
        return converted

    @staticmethod
    def stringify_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            return "\n".join(parts).strip()
        return str(content)


class ToolCatalog:
    """Build tool definitions from block configurations."""

    def __init__(self, knowledge_base: MosqlimateKnowledgeBase) -> None:
        self.knowledge_base = knowledge_base
        self.logger = get_monitor_logger("tools")

    def build_tools(
        self,
        blocks: List[DocumentBlockConfig],
    ) -> List[StructuredTool]:
        tools: List[StructuredTool] = []
        for block in blocks:

            def _run(question: str, *, _block_key: str = block.key) -> str:
                start = perf_counter()
                result = self.knowledge_base.format_block_context(
                    _block_key, question
                )
                log_event(
                    self.logger,
                    "tool_executed",
                    tool_name=_block_key,
                    question_preview=preview_text(question),
                    elapsed_seconds=elapsed_seconds(start),
                    result_preview=preview_text(result),
                )
                return result

            tools.append(
                StructuredTool.from_function(
                    func=_run,
                    name=block.key,
                    description=block.description,
                    args_schema=BlockSearchInput,
                )
            )

        available_block_keys = {block.key for block in blocks}

        def _run_batch(requests: List[BatchBlockSearchItem]) -> str:
            start = perf_counter()
            parts: List[str] = []
            requested_blocks: List[str] = []

            for item in requests:
                if item.block_key not in available_block_keys:
                    raise ValueError(
                        f"Unknown block key in batch search: {item.block_key}"
                    )
                requested_blocks.append(item.block_key)
                parts.append(
                    self.knowledge_base.format_block_context(
                        item.block_key,
                        item.question,
                    )
                )

            result = "\n\n".join(parts)
            log_event(
                self.logger,
                "batch_tool_executed",
                tool_name="batch_document_search",
                block_keys=requested_blocks,
                request_count=len(requests),
                elapsed_seconds=elapsed_seconds(start),
                result_preview=preview_text(result),
            )
            return result

        tools.append(
            StructuredTool.from_function(
                func=_run_batch,
                name="batch_document_search",
                description=(
                    "Consulta varios blocos documentais em uma unica chamada. "
                    "Use quando a pergunta exigir combinar evidencias de mais de "
                    "um bloco, dominio ou contexto."
                ),
                args_schema=BatchBlockSearchInput,
            )
        )
        return tools


class ChatModelFactory:
    """Create the chat model used by the single-agent flow."""

    @staticmethod
    def create(
        provider_type: ProviderType,
        provider_config: ProviderConfig,
    ) -> ChatOpenAI:
        if provider_type not in {
            ProviderType.OPENAI,
            ProviderType.GEMINI,
            ProviderType.NVIDIA,
            ProviderType.DEEPSEEK,
        }:
            raise NotImplementedError(
                "The LangChain single-agent flow currently supports only "
                "OpenAI-compatible providers."
            )

        base_url_by_provider = {
            ProviderType.OPENAI: provider_config.base_url
            or "https://api.openai.com/v1",
            ProviderType.GEMINI: provider_config.base_url
            or "https://generativelanguage.googleapis.com/v1beta/openai/",
            ProviderType.NVIDIA: provider_config.base_url
            or "https://integrate.api.nvidia.com/v1",
            ProviderType.DEEPSEEK: provider_config.base_url
            or "https://api.deepseek.com",
        }

        return ChatOpenAI(
            api_key=SecretStr(provider_config.api_key),
            model=provider_config.model,
            base_url=base_url_by_provider[provider_type],
            temperature=0,
            extra_body={"thinking": {"type": "disabled"}},
        )


class LangChainToolAgent:
    """Run a single tool-calling agent over block-scoped retrieval tools."""

    def __init__(
        self,
        knowledge_base: MosqlimateKnowledgeBase,
        provider_type: ProviderType,
        provider_config: ProviderConfig | Dict[str, Any],
        lang: Literal["en", "pt"] = "pt",
        max_tool_iterations: int = 5,
        chat_model: Optional[Any] = None,
    ) -> None:
        self.knowledge_base = knowledge_base
        self.provider_type = provider_type
        self.provider_config = ProviderConfig.model_validate(provider_config)
        self.lang = lang
        self.max_tool_iterations = max_tool_iterations
        self.message_adapter = ChatMessageAdapter()
        self.tools = ToolCatalog(knowledge_base).build_tools(
            knowledge_base.available_blocks()
        )
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.chat_model = chat_model or ChatModelFactory.create(
            provider_type=self.provider_type,
            provider_config=self.provider_config,
        )
        self.logger = get_monitor_logger("agent")

    def _build_initial_messages(
        self,
        user_query: str,
        message_history: Optional[List[ChatMessage]],
    ) -> List[BaseMessage]:
        """Build the initial prompt messages for one run."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", get_single_agent_prompt(self.lang)),
                MessagesPlaceholder("history"),
                ("human", "{question}"),
            ]
        )
        return prompt.format_messages(
            history=self.message_adapter.history_to_messages(message_history),
            question=user_query,
        )

    @staticmethod
    def _merge_usage(
        total_usage: TokenUsage,
        usage: Optional[Dict[str, int]],
    ) -> None:
        """Accumulate token usage into the running totals."""
        total_usage.merge(usage)

    def _build_result_payload(
        self,
        *,
        content: str,
        tool_calls_history: List[ToolCallRecord],
        retrieved_blocks: List[str],
        iterations: int,
        total_usage: TokenUsage,
        provider_metadata: Dict[str, Any],
        run_start: float,
    ) -> Dict[str, Any]:
        """Build the normalized result dictionary returned by the agent."""
        return AgentRunResult(
            content=content,
            tool_calls=tool_calls_history,
            retrieved_blocks=retrieved_blocks,
            iterations=iterations,
            usage=total_usage,
            provider_cost=provider_metadata.get("cost"),
            provider_metadata=provider_metadata,
            elapsed_seconds=elapsed_seconds(run_start),
        ).to_payload()

    @staticmethod
    def _extend_retrieved_blocks(
        retrieved_blocks: List[str],
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> None:
        """Track which blocks were retrieved by a tool call."""
        if tool_name == "batch_document_search":
            retrieved_blocks.extend(
                [
                    request["block_key"]
                    for request in arguments.get("requests", [])
                    if request.get("block_key")
                ]
            )
            return
        retrieved_blocks.append(tool_name)

    def run(
        self,
        user_query: str,
        message_history: Optional[List[ChatMessage]] = None,
    ) -> Dict[str, Any]:
        """Execute the single-agent retrieval loop."""
        messages = self._build_initial_messages(user_query, message_history)

        tool_enabled_model = self.chat_model.bind_tools(self.tools)
        tool_calls_history: List[ToolCallRecord] = []
        retrieved_blocks: List[str] = []
        total_usage = TokenUsage()
        run_start = perf_counter()

        log_event(
            self.logger,
            "agent_run_started",
            question_preview=preview_text(user_query),
            history_messages=len(message_history or []),
            available_tools=len(self.tools),
            max_tool_iterations=self.max_tool_iterations,
        )

        for iteration in range(self.max_tool_iterations):
            response = tool_enabled_model.invoke(messages)
            provider_metadata = extract_langchain_response_metadata(response)
            usage = extract_langchain_usage(response)
            self._merge_usage(total_usage, usage)
            tool_calls = getattr(response, "tool_calls", None) or []
            log_event(
                self.logger,
                "llm_response_received",
                iteration=iteration,
                usage=usage,
                provider_metadata=provider_metadata,
                tool_calls_count=len(tool_calls),
                finish_reason=(
                    getattr(response, "response_metadata", {}) or {}
                ).get("finish_reason"),
            )
            if not tool_calls:
                return self._build_result_payload(
                    content=self.message_adapter.stringify_content(
                        response.content
                    ),
                    tool_calls_history=tool_calls_history,
                    retrieved_blocks=retrieved_blocks,
                    iterations=iteration,
                    total_usage=total_usage,
                    provider_metadata=provider_metadata,
                    run_start=run_start,
                )

            messages.append(response)

            for call in tool_calls:
                tool = self.tool_map[call["name"]]
                result = tool.invoke(call["args"])
                tool_calls_history.append(
                    ToolCallRecord(
                        tool=call["name"],
                        arguments=call["args"],
                        result=result,
                    )
                )
                self._extend_retrieved_blocks(
                    retrieved_blocks=retrieved_blocks,
                    tool_name=call["name"],
                    arguments=call["args"],
                )
                log_event(
                    self.logger,
                    "tool_call_selected",
                    iteration=iteration,
                    tool_name=call["name"],
                    arguments=call["args"],
                )
                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=call["id"],
                    )
                )

        force_reply_instruction = (
            "Tool limit reached. Answer now using only the retrieved context and "
            "the conversation so far. Do not call tools again. If information is "
            "missing, say that clearly."
            if self.lang == "en"
            else "O limite de ferramentas foi atingido. Responda agora usando "
            "apenas o contexto recuperado e a conversa até aqui. Não chame "
            "ferramentas novamente. Se faltar informação, diga isso claramente."
        )
        force_reply_messages = [
            *messages,
            HumanMessage(content=force_reply_instruction),
        ]
        final_response = self.chat_model.invoke(force_reply_messages)
        final_provider_metadata = extract_langchain_response_metadata(
            final_response
        )
        final_usage = extract_langchain_usage(final_response)
        self._merge_usage(total_usage, final_usage)
        forced_content = self.message_adapter.stringify_content(
            final_response.content
        ).strip()
        if not forced_content:
            forced_content = (
                "Maximum tool iterations reached and the model returned no final answer."
                if self.lang == "en"
                else "O limite de ferramentas foi atingido e o modelo não retornou uma resposta final."
            )
        log_event(
            self.logger,
            "forced_final_response_after_tool_limit",
            iteration=self.max_tool_iterations,
            usage=final_usage,
            provider_metadata=final_provider_metadata,
            content_preview=preview_text(forced_content),
        )
        return self._build_result_payload(
            content=forced_content,
            tool_calls_history=tool_calls_history,
            retrieved_blocks=retrieved_blocks,
            iterations=self.max_tool_iterations,
            total_usage=total_usage,
            provider_metadata=final_provider_metadata,
            run_start=run_start,
        )
