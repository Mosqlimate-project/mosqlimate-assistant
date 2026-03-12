import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from mosqlimate_assistant.models import (
    ChatMessage,
    ProviderResponse,
    ProviderType,
)


def _messages_to_dicts(
    messages: List[ChatMessage],
) -> List[Dict[str, str]]:
    return [{"role": msg.role, "content": msg.content} for msg in messages]


def _wrap_tools_openai(
    tools: Optional[List[Dict[str, Any]]],
) -> Optional[List[Dict[str, Any]]]:
    if not tools:
        return None
    return [{"type": "function", "function": t} for t in tools]


def _extract_tool_calls_openai(message: Any) -> Optional[List[Dict[str, str]]]:
    tcs = getattr(message, "tool_calls", None)
    if not tcs:
        return None
    return [
        {"name": tc.function.name, "arguments": tc.function.arguments}
        for tc in tcs
    ]


class BaseProvider(ABC):

    @abstractmethod
    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        pass

    def supports_tools(self) -> bool:
        return False


class _OpenAICompatibleMixin(BaseProvider):

    client: Any
    model: str

    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        args: Dict[str, Any] = {
            "model": self.model,
            "messages": _messages_to_dicts(messages),
            **kwargs,
        }

        wrapped = _wrap_tools_openai(tools)
        if wrapped:
            args["tools"] = wrapped
            args["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**args)
        msg = response.choices[0].message

        return ProviderResponse(
            content=msg.content or "",
            raw_response=response,
            tool_calls=_extract_tool_calls_openai(msg),
        )

    def supports_tools(self) -> bool:
        return True


class OpenAIProvider(_OpenAICompatibleMixin):

    def __init__(self, api_key: str, base_url: str, model: str):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model


class GeminiProvider(_OpenAICompatibleMixin):

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    ):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model


class _OllamaCompatibleMixin(BaseProvider):

    client: Any
    model: str

    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        response = self.client.chat(
            model=self.model,
            messages=_messages_to_dicts(messages),
            **kwargs,
        )
        return ProviderResponse(
            content=response["message"]["content"],
            raw_response=response,
            tool_calls=None,
        )


class OllamaProvider(_OllamaCompatibleMixin):

    def __init__(self, model: str, base_url: Optional[str] = None):
        import ollama

        self.model = model
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )


class OllamaCloudProvider(_OllamaCompatibleMixin):

    def __init__(
        self, api_key: str, model: str, host: str = "https://ollama.com"
    ):
        import ollama

        self.model = model
        self.client = ollama.Client(
            host=host,
            headers={"Authorization": f"Bearer {api_key}"},
        )


class GoogleGenAIProvider(BaseProvider):

    def __init__(self, api_key: str, model: str):
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        from google.genai import types

        system_instruction: Optional[str] = None
        contents: List[types.Content] = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            else:
                role = "model" if msg.role == "assistant" else "user"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg.content)],
                    )
                )

        genai_tools: Optional[List[types.Tool]] = None
        if tools:
            declarations = [types.FunctionDeclaration(**t) for t in tools]
            genai_tools = [types.Tool(function_declarations=declarations)]

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=genai_tools,  # type: ignore[arg-type]
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        tool_calls: Optional[List[Dict[str, str]]] = None
        content_text = ""

        parts = (
            response.candidates[0].content.parts
            if response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
            else []
        )

        for part in parts:
            if part.function_call:
                if tool_calls is None:
                    tool_calls = []
                fc = part.function_call
                tool_calls.append(
                    {
                        "name": fc.name or "",
                        "arguments": json.dumps(
                            dict(fc.args) if fc.args else {}
                        ),
                    }
                )
            elif part.text:
                content_text += part.text

        return ProviderResponse(
            content=content_text,
            raw_response=response,
            tool_calls=tool_calls,
        )

    def supports_tools(self) -> bool:
        return True


class NvidiaProvider(_OpenAICompatibleMixin):

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-ai/deepseek-v3.2",
    ):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
        )
        self.model = model


class DeepSeekProvider(_OpenAICompatibleMixin):

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
    ):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = model


class ProviderFactory:

    @staticmethod
    def create(
        provider_type: ProviderType, config: Dict[str, Any]
    ) -> BaseProvider:
        providers = {
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.GEMINI: GeminiProvider,
            ProviderType.OLLAMA: OllamaProvider,
            ProviderType.GOOGLE_GENAI: GoogleGenAIProvider,
            ProviderType.NVIDIA: NvidiaProvider,
            ProviderType.DEEPSEEK: DeepSeekProvider,
            ProviderType.OLLAMA_CLOUD: OllamaCloudProvider,
        }

        cls = providers.get(provider_type)
        if cls is None:
            raise ValueError(
                f"Tipo de provedor não suportado: {provider_type}"
            )
        return cls(**config)
