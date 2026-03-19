"""LLM provider abstraction layer.

Defines a unified interface (``BaseProvider``) for chat completions and
concrete implementations for each supported backend. Providers that share
the OpenAI-compatible API inherit from ``_OpenAICompatibleMixin``; Ollama-
based providers inherit from ``_OllamaCompatibleMixin``.

Supported providers:
    - OpenAI (``OpenAIProvider``)
    - Gemini via OpenAI compat layer (``GeminiProvider``)
    - Google GenAI native SDK (``GoogleGenAIProvider``)
    - Ollama local (``OllamaProvider``)
    - Ollama Cloud (``OllamaCloudProvider``)
    - NVIDIA NIM (``NvidiaProvider``)
    - DeepSeek (``DeepSeekProvider``)

Use ``ProviderFactory.create()`` to instantiate providers by ``ProviderType``.
"""

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
    """Convert ChatMessage objects to provider-compatible dictionaries.

    Args:
        messages (List[ChatMessage]): The input message objects.

    Returns:
        List[Dict[str, str]]: Mapped dictionary representation with 'role' and 'content'.

    """
    return [{"role": msg.role, "content": msg.content} for msg in messages]


def _wrap_tools_openai(
    tools: Optional[List[Dict[str, Any]]],
) -> Optional[List[Dict[str, Any]]]:
    """Wrap generic tools into the OpenAI 'function' object format.

    Args:
        tools (Optional[List[Dict[str, Any]]]): A list of generic tool schemas.

    Returns:
        Optional[List[Dict[str, Any]]]: The wrapped schemas conforming to OpenAI standard.

    """
    if not tools:
        return None
    return [{"type": "function", "function": t} for t in tools]


def _extract_tool_calls_openai(message: Any) -> Optional[List[Dict[str, str]]]:
    """Extract requested tool calls from an OpenAI-compatible message.

    Args:
        message (Any): The message object returned by the OpenAI API wrapper.

    Returns:
        Optional[List[Dict[str, str]]]: Extracted tools as dictionaries with 'name' and 'arguments'.

    """
    tcs = getattr(message, "tool_calls", None)
    if not tcs:
        return None
    return [
        {"name": tc.function.name, "arguments": tc.function.arguments}
        for tc in tcs
    ]


class BaseProvider(ABC):
    """Abstract base class for all LLM providers.

    Defines the core `chat_completion` method and capabilities like `supports_tools`.
    """

    @abstractmethod
    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Send a chat completion request to the provider.

        Args:
            messages (List[ChatMessage]): The chat history to process.
            tools (Optional[List[Dict[str, Any]]]): Functions the LLM can invoke.
            **kwargs: Extra parameters passed directly to the generation API.

        Returns:
            ProviderResponse: Standardized response object containing the result.

        """
        pass

    def supports_tools(self) -> bool:
        """Check if this provider natively supports capability tools.

        Returns:
            bool: True if tool calling is supported, False otherwise.

        """
        return False


class _OpenAICompatibleMixin(BaseProvider):
    """Fallback mixin for LLM APIs that mimic the OpenAI SDK specification.

    Handles tool bindings, completions, and schema translations transparently
    using standard OpenAI API patterns.

    Attributes:
        client (Any): An instantiated OpenAI standard client.
        model (str): Target model identifier string.

    """

    client: Any
    model: str

    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Perform a chat completion via an OpenAI-compatible interface.

        Args:
            messages (List[ChatMessage]): The chat history to process.
            tools (Optional[List[Dict[str, Any]]]): Functions the LLM can invoke.
            **kwargs: Extra arguments passed to the generation.

        Returns:
            ProviderResponse: The result holding generated text and possible tool calls.

        """
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
        """Declare that OpenAI-compliant providers uniformly support tools.

        Returns:
            bool: True.

        """
        return True


class OpenAIProvider(_OpenAICompatibleMixin):
    """Provider for authentic OpenAI API services."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the OpenAI API client.

        Args:
            api_key (str): The valid service API key.
            base_url (str): The upstream service hostname.
            model (str): Target model name (e.g., 'gpt-4').

        """
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model


class GeminiProvider(_OpenAICompatibleMixin):
    """Google Gemini completion endpoint via the OpenAI compatibility API wrapper."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    ):
        """Initialize the Gemini proxy API client.

        Args:
            api_key (str): Google platform API key.
            model (str): Gemini model identifier.
            base_url (str): Override URL, defaults to the generic openai-compatible Gemini proxy.

        """
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model


class _OllamaCompatibleMixin(BaseProvider):
    """Fallback mixin for local and cloud Ollama instances.

    Attributes:
        client (Any): An instantiated Ollama SDK client object.
        model (str): Target model valid in the target Ollama instance.

    """

    client: Any
    model: str

    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Perform a chat completion against an Ollama backend.

        Args:
            messages (List[ChatMessage]): Chat dialogue array.
            tools (Optional[List[Dict[str, Any]]]): Unsupported in this mixin yet.
            **kwargs: Extra parameters for the model generation.

        Returns:
            ProviderResponse: The standardized inference output.

        """
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
    """Local Ollama instance provider implementation."""

    def __init__(self, model: str, base_url: Optional[str] = None):
        """Initialize the local Ollama client connector.

        Args:
            model (str): Model tag available in standard Ollama pulls.
            base_url (Optional[str]): Network-hosted local endpoints.

        """
        import ollama

        self.model = model
        self.client = (
            ollama.Client(host=base_url) if base_url else ollama.Client()
        )


class OllamaCloudProvider(_OllamaCompatibleMixin):
    """Remote secure Ollama cloud implementation handling authenticated connections."""

    def __init__(
        self, api_key: str, model: str, host: str = "https://ollama.com"
    ):
        """Initialize the Ollama cloud client connector.

        Args:
            api_key (str): Auth key token for custom Ollama instance platforms.
            model (str): Model to spawn into inferencing.
            host (str): Explicit remote URL.

        """
        import ollama

        self.model = model
        self.client = ollama.Client(
            host=host,
            headers={"Authorization": f"Bearer {api_key}"},
        )


class GoogleGenAIProvider(BaseProvider):
    """Native implementation of Google GenAI backend without using OpenAI translation API wrappers.

    Attributes:
        client (genai.Client): GenAI native SDK client instance.
        model (str): Google platform model, i.e., "gemini-2.5-flash".

    """

    def __init__(self, api_key: str, model: str):
        """Initialize original Google GenAI endpoint integration.

        Args:
            api_key (str): Credential to execute generation tasks.
            model (str): Generation backend ID.

        """
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def chat_completion(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Directly map local generic arguments and ChatMessages toward a native Google GenAI backend.

        Args:
            messages (List[ChatMessage]): Uniform user messages sequence.
            tools (Optional[List[Dict[str, Any]]]): Formattable JSON-schema capabilities.
            **kwargs: Miscellaneous payload extensions.

        Returns:
            ProviderResponse: Formatted class containing results array outputs.

        """
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
        """Evaluate platform tool schema bindings check capability.

        Returns:
            bool: Always True.

        """
        return True


class NvidiaProvider(_OpenAICompatibleMixin):
    """NVIDIA NIM inference API completions backend driver handler."""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-ai/deepseek-v3.2",
    ):
        """Construct the NVIDIA remote engine provider.

        Args:
            api_key (str): Standard NVIDIA NGC validation key.
            model (str): Engine ID format mapped model.

        """
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
        )
        self.model = model


class DeepSeekProvider(_OpenAICompatibleMixin):
    """DeepSeek platform endpoint execution implementation."""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
    ):
        """Construct a DeepSeek inference host node binding.

        Args:
            api_key (str): Authenticated internal developer secret string token.
            model (str): Remote routing specific engine specifier strings.

        """
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = model


class ProviderFactory:
    """Factory interface ensuring normalized provider instantiations."""

    @staticmethod
    def create(
        provider_type: ProviderType, config: Dict[str, Any]
    ) -> BaseProvider:
        """Build an integration concrete layout representing one target provider.

        Args:
            provider_type (ProviderType): Target identity ID.
            config (Dict[str, Any]): Additional parameters passed straight out to `__init__`.

        Returns:
            BaseProvider: Object instances conforming to the generation standards layout.

        Raises:
            ValueError: On requested unsupported `ProviderType`.

        """
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
