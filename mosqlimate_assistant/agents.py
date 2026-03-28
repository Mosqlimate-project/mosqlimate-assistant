"""Agent execution and orchestration layer.

Contains the runtime components that bring agent cards to life:

- ``AgentExecutor`` binds an ``AgentCard`` to an LLM provider and an
  optional vector store. It handles RAG document retrieval, prompt
  construction, tool execution loops, and response generation.
  Includes context-limited fallback (max 3 docs) to prevent LLM
  flooding and ``[Doc doc_id]`` labeling for citation grounding.

- ``AgentOrchestrator`` manages a registry of named agents and routes
  user queries to the appropriate executor.

The execution flow is:
    1. Search relevant documents from the vector store (RAG).
    2. Build a message list (system prompt → docs context → history → query).
    3. Call the LLM provider, optionally iterating on tool calls.
    4. Return the final response with metadata.
"""

import json
from typing import Any, Dict, List, Literal, Optional

from mosqlimate_assistant.agent_cards import AgentCard, BaseTool
from mosqlimate_assistant.models import ChatMessage, VectorSearchResult
from mosqlimate_assistant.providers import BaseProvider
from mosqlimate_assistant.vector_store import BaseVectorStore

_URL_METADATA_KEYS = ["url_link", "source_url", "link", "web_reference", "url"]
_INFO_METADATA_KEYS = ["name", "description", "title", "file_path"]


class AgentExecutor:
    """Binds an agent definition to execution resources.

    This class handles the core logic of running an agent: retrieving documents,
    building conversational prompts, querying the LLM provider, and handling
    tool loop integrations.

    Attributes:
        agent_card (AgentCard): The data structure defining agent rules and tools.
        provider (BaseProvider): The configured LLM provider wrapper class.
        vector_store (Optional[BaseVectorStore]): The database to query context from.
        tools (Dict[str, BaseTool]): A mapping of tool names to their instances.
        lang (Literal["en", "pt"]): Language code for localized messages.

    """

    def __init__(
        self,
        agent_card: AgentCard,
        provider: BaseProvider,
        vector_store: Optional[BaseVectorStore] = None,
        tools: Optional[List[BaseTool]] = None,
        lang: Literal["en", "pt"] = "pt",
    ):
        """Initialize the agent executor.

        Args:
            agent_card (AgentCard): The agent's definition and strategy settings.
            provider (BaseProvider): The LLM engine.
            vector_store (Optional[BaseVectorStore], optional): Where to retrieve context. Defaults to None.
            tools (Optional[List[BaseTool]], optional): Active tools assigned to this agent execution. Defaults to None.
            lang (Literal["en", "pt"], optional): Agent response language default. Defaults to "pt".

        """
        self.agent_card = agent_card
        self.provider = provider
        self.vector_store = vector_store
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.lang = lang

    def _apply_fallback(
        self,
        results: List[VectorSearchResult],
        fallback_collection: Optional[str],
    ) -> List[VectorSearchResult]:
        """Apply fallback retrieval if initial search fails to cross thresholds.

        Returns at most 3 documents from the fallback collection to avoid
        flooding the LLM context with irrelevant content.

        Args:
            results (List[VectorSearchResult]): The original retrieved matches.
            fallback_collection (Optional[str]): Target collection to pull as fallback.

        Returns:
            List[VectorSearchResult]: Original results, or a limited array of fallback hits.
        """
        if not self.vector_store or not fallback_collection:
            return results
        fallback_docs = self.vector_store.get_documents_by_collection(
            fallback_collection
        )
        if fallback_docs:
            return [
                VectorSearchResult(document=doc, score=0.5)
                for doc in fallback_docs[:3]
            ]
        return results

    def search_relevant_docs(self, query: str, k: int = 3):
        """Perform semantic search dynamically matching the agent's mode layout.

        Args:
            query (str): The search phrase.
            k (int, optional): Max documents to retrieve. Defaults to 3.

        Returns:
            Optional[List[VectorSearchResult]]: Ordered hits or None.

        """
        if not self.vector_store:
            return None

        mode = self.agent_card.search_mode.lower()
        groups = self.agent_card.target_groups
        named_groups = self.agent_card.named_groups
        group_key = self.agent_card.group_key
        fallback_collection = self.agent_card.fallback_docs

        if mode == "total":
            results = self.vector_store.get_all_documents()
        elif mode == "group":
            if named_groups:
                results = self.vector_store.named_group_search(
                    query, groups=named_groups, group_key=group_key
                )
            else:
                results = self.vector_store.group_similarity_search(query, k=k)
        else:
            results = self.vector_store.similarity_search(
                query,
                k=k,
                collections=groups if groups else None,
                search_mode=self.agent_card.search_scope,
            )

        if not results:
            results = self._apply_fallback(results, fallback_collection)

        return results

    def _format_docs_context(self, retrieved_docs: List[Any]) -> str:
        """Stringify vector database entries.

        Args:
            retrieved_docs (List[Any]): Document match objects to parse.

        Returns:
            str: Pretty printed representation for prompt inclusion.

        """
        en = self.lang == "en"
        content_label = "Content" if en else "Conteúdo"

        doc_parts = []
        for i, res in enumerate(retrieved_docs):
            doc = res.document if hasattr(res, "document") else res

            part = f"[Doc {doc.id}] (score: {res.score:.2f})\n"

            metadata = doc.metadata
            if metadata:
                link = next(
                    (
                        metadata[k]
                        for k in _URL_METADATA_KEYS
                        if k in metadata and metadata[k]
                    ),
                    None,
                )

                info_items = [
                    f"{k}: {metadata[k]}"
                    for k in _INFO_METADATA_KEYS
                    if k in metadata
                ]

                if link:
                    part += f"Ref Link: {link}\n"
                if info_items:
                    part += f"Info: {', '.join(info_items)}\n"

            part += f"{content_label}:\n{doc.content}\n"
            doc_parts.append(part)

        return "\n".join(doc_parts)

    def build_messages(
        self,
        user_query: str,
        system_prompt: Optional[str] = None,
        message_history: Optional[List[ChatMessage]] = None,
        retrieved_docs: Optional[List[Any]] = None,
    ) -> List[ChatMessage]:
        """Construct the full message stack to be forwarded into the active LLM context.

        Args:
            user_query (str): The initial prompt submitted by user targeting the tool.
            system_prompt (Optional[str], optional): The overriding contextual role assignment strings. Defaults to None.
            message_history (Optional[List[ChatMessage]], optional): Preceding back-and-forth turns list. Defaults to None.
            retrieved_docs (Optional[List[Any]], optional): Knowledge base fragments text hits list. Defaults to None.

        Returns:
            List[ChatMessage]: Complimented messages payload properly ranked.

        """
        messages = []

        # 1) System prompt: instruções do agente (prioridade máxima)
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))

        # 2) Documentação: contexto informacional separado
        #    Enviado como system message com papel de "informação de referência",
        #    NÃO como instruções. O LLM prioriza o prompt de sistema acima.
        if retrieved_docs:
            docs_text = self._format_docs_context(retrieved_docs)
            if self.lang == "en":
                docs_context_msg = (
                    "Below is the retrieved reference documentation. "
                    "Use ONLY this information to answer. "
                    "If the answer is not found here, say you don't have enough information. "
                    "Cite documents as [URL] in your answer.\n\n"
                    f"{docs_text}"
                )
            else:
                docs_context_msg = (
                    "A seguir está a documentação de referência recuperada. "
                    "Use APENAS estas informações para responder. "
                    "Se a resposta não estiver aqui, diga que não tem informação suficiente. "
                    "Cite os documentos como [URL] na sua resposta.\n\n"
                    f"{docs_text}"
                )
            messages.append(
                ChatMessage(role="system", content=docs_context_msg)
            )

        # 3) Histórico de mensagens: preserva o fluxo da conversa
        if message_history:
            messages.extend(message_history)

        # 4) Pergunta do usuário: limpa, sem docs misturados
        messages.append(ChatMessage(role="user", content=user_query))

        return messages

    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        message_history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Call a local instance-bound capability.

        Args:
            tool_name (str): The unique string ID marking which function to apply.
            arguments (Dict[str, Any]): The mapped parameter bindings structure array.
            message_history (Optional[List[ChatMessage]], optional): Filtered
                conversation history to forward to agent-type tools so that
                sub-agents have conversational context. Defaults to None.

        Returns:
            str: The execution parsed results.

        Raises:
            ValueError: Under unknown tools target.

        """
        if tool_name not in self.tools:
            raise ValueError(f"Ferramenta não encontrada: {tool_name}")

        tool = self.tools[tool_name]
        if message_history is not None:
            return tool.execute(_message_history=message_history, **arguments)
        return tool.execute(**arguments)

    def run(
        self,
        user_query: str,
        system_prompt: Optional[str] = None,
        message_history: Optional[List[ChatMessage]] = None,
        use_rag: bool = True,
        max_tool_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Trigger an execution cycle taking over full turn progression parsing steps internally.

        Args:
            user_query (str): The main command from end human wrapper script.
            system_prompt (Optional[str], optional): Override behavior string. Defaults to None.
            message_history (Optional[List[ChatMessage]], optional): Passed history of the thread. Defaults to None.
            use_rag (bool, optional): Allows activating index lookups search functions. Defaults to True.
            max_tool_iterations (int, optional): Failsafe looping depth boundary. Defaults to 5.

        Returns:
            Dict[str, Any]: Packaged response content paired together alongside logging trace properties maps.

        """
        if system_prompt is None:
            system_prompt = self.agent_card.get_prompt()

        retrieved_docs = None
        if use_rag and self.vector_store:
            retrieved_docs = self.search_relevant_docs(user_query)

        messages = self.build_messages(
            user_query, system_prompt, message_history, retrieved_docs
        )

        # Filter history to user↔assistant messages only.
        # Tool-call internals are not relevant for sub-agents.
        filtered_history: List[ChatMessage] = [
            m
            for m in (message_history or [])
            if m.role in ("user", "assistant")
        ]

        tool_calls_history: List[Dict[str, Any]] = []
        iterations = 0

        tool_schemas = None
        if self.tools and self.provider.supports_tools():
            tool_schemas = [
                tool.schema_for_llm for tool in self.tools.values()
            ]

        while iterations < max_tool_iterations:
            response = self.provider.chat_completion(
                messages, tools=tool_schemas
            )

            if not response.tool_calls:
                return {
                    "content": response.content or "",
                    "tool_calls": tool_calls_history,
                    "retrieved_docs": retrieved_docs,
                    "iterations": iterations,
                }

            for tool_call in response.tool_calls:
                tool_result = self.execute_tool(
                    tool_call["name"],
                    json.loads(tool_call["arguments"]),
                    message_history=(
                        filtered_history if filtered_history else None
                    ),
                )
                tool_calls_history.append(
                    {
                        "tool": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": tool_result,
                    }
                )

                if self.lang == "en":
                    tool_msg = f"Called tool {tool_call['name']}"
                    result_msg = f"Tool result: {tool_result}"
                else:
                    tool_msg = f"Chamei a ferramenta {tool_call['name']}"
                    result_msg = f"Resultado da ferramenta: {tool_result}"

                messages.append(
                    ChatMessage(role="assistant", content=tool_msg)
                )
                messages.append(ChatMessage(role="user", content=result_msg))

            iterations += 1

        max_iter_msg = (
            "Maximum tool iterations reached."
            if self.lang == "en"
            else "Máximo de iterações de ferramentas atingido."
        )
        return {
            "content": max_iter_msg,
            "tool_calls": tool_calls_history,
            "retrieved_docs": retrieved_docs,
            "iterations": iterations,
        }


class AgentOrchestrator:
    """Handles the unified routing over varying AgentExecutors across pipeline systems.

    Attributes:
        agents (Dict[str, AgentExecutor]): Directory store mapping string names against configured nodes.
        default_agent (Optional[str]): Standard fallback name token ID identifier.

    """

    def __init__(self):
        """Initialize empty routing registry structures inside the orchestrator frame."""
        self.agents: Dict[str, AgentExecutor] = {}
        self.default_agent: Optional[str] = None

    def register_agent(
        self, name: str, agent: AgentExecutor, is_default: bool = False
    ):
        """Attach a configured execution handler node onto the operational map graph.

        Args:
            name (str): Path variable token tracking naming tag.
            agent (AgentExecutor): Setup structure carrying dependencies layout map object.
            is_default (bool, optional): Overwrites top-level default if chosen explicitly. Defaults to False.

        """
        self.agents[name] = agent

        def _make_callback(sub_agent: AgentExecutor) -> Any:
            """Return a callback that runs the sub-agent with its own system prompt.

            The sub-agent receives:
            - Its own base system prompt (via ``get_prompt()``).
            - The question enriched with the task context from the caller.
            - The filtered conversation history (user/assistant turns only).

            Args:
                sub_agent (AgentExecutor): The agent executor to wrap.

            Returns:
                Callable: A three-argument callback ``(user_question, task_context, message_history)``.

            """

            def callback(
                user_question: str,
                task_context: str,
                message_history: Optional[List[ChatMessage]] = None,
            ) -> Dict[str, Any]:
                if task_context:
                    prefix = (
                        "Context" if sub_agent.lang == "en" else "Contexto"
                    )
                    query = f"[{prefix}: {task_context}]\n\n{user_question}"
                else:
                    query = user_question
                return sub_agent.run(
                    user_query=query,
                    message_history=message_history,
                    # system_prompt=None → sub-agent uses its own prompt function
                )

            return callback

        agent.agent_card.set_executor_callback(_make_callback(agent))
        if is_default or not self.default_agent:
            self.default_agent = name

    def route(
        self, user_query: str, agent_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Dispatch query inputs down through the correctly pinpointed agent wrapper implementation node.

        Args:
            user_query (str): Direct string query from client frontend request.
            agent_name (Optional[str], optional): The forced explicit route choice identifier. Defaults to None.
            **kwargs: Extra parameters payload passed onward dynamically.

        Returns:
            Dict[str, Any]: Response maps containing content texts and traces.

        Raises:
            ValueError: If a route tag identifier does not natively land accurately into existing definitions registry arrays set mapped list map.

        """
        target_agent = agent_name or self.default_agent

        if not target_agent or target_agent not in self.agents:
            raise ValueError(f"Agent not found: {target_agent}")

        return self.agents[target_agent].run(user_query, **kwargs)
