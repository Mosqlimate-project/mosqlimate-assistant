import json
from typing import Any, Dict, List, Optional

from mosqlimate_assistant.agent_cards import AgentCard, BaseTool
from mosqlimate_assistant.models import ChatMessage, VectorSearchResult
from mosqlimate_assistant.providers import BaseProvider
from mosqlimate_assistant.vector_store import BaseVectorStore


class AgentExecutor:

    def __init__(
        self,
        agent_card: AgentCard,
        provider: BaseProvider,
        vector_store: Optional[BaseVectorStore] = None,
        tools: Optional[List[BaseTool]] = None,
    ):
        self.agent_card = agent_card
        self.provider = provider
        self.vector_store = vector_store
        self.tools = {tool.name: tool for tool in (tools or [])}

    def search_relevant_docs(self, query: str, k: int = 3):
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
                # Grupos customizados: List[List[str]] de valores de metadata
                results = self.vector_store.named_group_search(
                    query, groups=named_groups, group_key=group_key
                )
            else:
                # Fallback: grupos por collection
                results = self.vector_store.group_similarity_search(query, k=k)
        else:
            results = self.vector_store.similarity_search(
                query, k=k, collections=groups if groups else None
            )

        should_fallback = not results or results[0].score < 0.75

        if should_fallback and fallback_collection:
            fallback_docs = self.vector_store.get_documents_by_collection(
                fallback_collection
            )
            if fallback_docs:
                results = [
                    VectorSearchResult(document=doc, score=0.5)
                    for doc in fallback_docs
                ]

        return results

    def build_messages(
        self,
        user_query: str,
        system_prompt: Optional[str] = None,
        message_history: Optional[List[ChatMessage]] = None,
        retrieved_docs: Optional[List[Any]] = None,
    ) -> List[ChatMessage]:
        messages = []

        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))

        if message_history:
            messages.extend(message_history)

        user_content = user_query
        if retrieved_docs:
            doc_parts = []
            for i, res in enumerate(retrieved_docs):
                doc = res.document if hasattr(res, "document") else res

                part = f"--- Documento {i+1} ---\n"

                metadata = doc.metadata
                if metadata:
                    ref_keys = [
                        "url_link",
                        "source_url",
                        "link",
                        "web_reference",
                        "url",
                    ]

                    link = next(
                        (
                            metadata[k]
                            for k in ref_keys
                            if k in metadata and metadata[k]
                        ),
                        None,
                    )

                    info_keys = ["name", "description", "title", "file_path"]
                    info_items = [
                        f"{k}: {metadata[k]}"
                        for k in info_keys
                        if k in metadata
                    ]

                    if link:
                        part += f"Ref Link: {link}\n"
                    if info_items:
                        part += f"Info: {', '.join(info_items)}\n"

                part += f"Conteúdo:\n{doc.content}\n"
                doc_parts.append(part)

            docs_text = "\n".join(doc_parts)
            user_content = (
                f"Use a seguinte documentação de contexto para responder à pergunta:\n\n"
                f"{docs_text}\n\n"
                f"---\n"
                f"Pergunta do Usuário: {user_query}"
            )

        messages.append(ChatMessage(role="user", content=user_content))

        return messages

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            raise ValueError(f"Ferramenta não encontrada: {tool_name}")

        tool = self.tools[tool_name]
        return tool.execute(**arguments)

    def run(
        self,
        user_query: str,
        system_prompt: Optional[str] = None,
        message_history: Optional[List[ChatMessage]] = None,
        use_rag: bool = True,
        max_tool_iterations: int = 5,
    ) -> Dict[str, Any]:
        if system_prompt is None:
            system_prompt = self.agent_card.get_prompt()

        retrieved_docs = None
        if use_rag and self.vector_store:
            retrieved_docs = self.search_relevant_docs(user_query)

        messages = self.build_messages(
            user_query, system_prompt, message_history, retrieved_docs
        )

        tool_calls_history: List[Dict[str, Any]] = []
        iterations = 0

        while iterations < max_tool_iterations:
            tool_schemas = None
            if self.tools and self.provider.supports_tools():
                tool_schemas = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args_schema.model_json_schema(),
                    }
                    for tool in self.tools.values()
                ]

            response = self.provider.chat_completion(
                messages, tools=tool_schemas
            )

            if not response.tool_calls:
                return {
                    "content": response.content,
                    "tool_calls": tool_calls_history,
                    "retrieved_docs": retrieved_docs,
                    "iterations": iterations,
                }

            for tool_call in response.tool_calls:
                tool_result = self.execute_tool(
                    tool_call["name"], json.loads(tool_call["arguments"])
                )
                tool_calls_history.append(
                    {
                        "tool": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": tool_result,
                    }
                )

                messages.append(
                    ChatMessage(
                        role="assistant",
                        content=f"Chamei a ferramenta {tool_call['name']}",
                    )
                )
                messages.append(
                    ChatMessage(
                        role="user",
                        content=f"Resultado da ferramenta: {tool_result}",
                    )
                )

            iterations += 1

        return {
            "content": "Máximo de iterações de ferramentas atingido.",
            "tool_calls": tool_calls_history,
            "retrieved_docs": retrieved_docs,
            "iterations": iterations,
        }


class AgentOrchestrator:

    def __init__(self):
        self.agents: Dict[str, AgentExecutor] = {}
        self.default_agent: Optional[str] = None

    def register_agent(
        self, name: str, agent: AgentExecutor, is_default: bool = False
    ):
        self.agents[name] = agent
        agent.agent_card.set_executor_callback(
            lambda q, ctx, _a=agent: _a.run(q, system_prompt=ctx)
        )
        if is_default or not self.default_agent:
            self.default_agent = name

    def route(
        self, user_query: str, agent_name: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        target_agent = agent_name or self.default_agent

        if not target_agent or target_agent not in self.agents:
            raise ValueError(f"Agente não encontrado: {target_agent}")

        return self.agents[target_agent].run(user_query, **kwargs)
