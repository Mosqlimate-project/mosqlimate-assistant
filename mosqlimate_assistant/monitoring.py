"""Structured logging, usage extraction, and cost helpers.

This module provides lightweight monitoring utilities used across the
assistant runtime, including structured logs, token-usage extraction
from provider responses, and cost normalization/estimation helpers.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

_BASE_LOGGER_NAME = "mosqlimate"
_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def extract_numeric_cost(cost_info: Any) -> float | None:
    """Extract a numeric USD cost from provider-specific billing payloads."""
    if cost_info is None:
        return None
    if isinstance(cost_info, (int, float)):
        return float(cost_info)
    if isinstance(cost_info, Mapping):
        for key in (
            "total_usd",
            "cost_usd",
            "usd",
            "total",
            "amount",
            "value",
        ):
            value = cost_info.get(key)
            if isinstance(value, (int, float)):
                return float(value)
        for nested_key in ("billing", "cost", "usage", "pricing"):
            nested = cost_info.get(nested_key)
            numeric = extract_numeric_cost(nested)
            if numeric is not None:
                return numeric
    return None


def configure_monitoring_logger() -> logging.Logger:
    """Return the shared monitoring logger, configuring a default handler once."""
    logger = logging.getLogger(_BASE_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        logger.addHandler(handler)
        logger.propagate = False

    level_name = os.getenv("MOSQLIMATE_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)
    return logger


def get_monitor_logger(name: str) -> logging.Logger:
    """Return a namespaced child logger under the shared monitoring root."""
    configure_monitoring_logger()
    return logging.getLogger(f"{_BASE_LOGGER_NAME}.{name}")


def _sanitize(value: Any) -> Any:
    """Convert values to JSON-safe primitives for structured logging."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _sanitize(v) for k, v in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(k): _sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_sanitize(item) for item in value]
    if hasattr(value, "model_dump"):
        return _sanitize(value.model_dump())
    if hasattr(value, "__dict__"):
        return _sanitize(vars(value))
    return str(value)


def calculate_cost(
    model: str, input_tokens: int, output_tokens: int
) -> float | None:
    """Calculate the estimated cost for a given model and token usage."""
    if not model:
        return None

    # Prices per 1M tokens (USD).
    # DeepSeek V4 values below use cache-miss input pricing as a conservative
    # fallback when the provider does not report cache details/cost directly.
    prices: dict[str, dict[str, float]] = {
        "deepseek-v4-flash": {"input": 0.14, "output": 0.28},
        "deepseek-v4-pro": {"input": 1.74, "output": 3.48},
    }

    # Normalize model name
    model_key = model.lower()
    if "deepseek-v4-pro" in model_key or "v4-pro" in model_key:
        price = prices.get("deepseek-v4-pro")
    elif "deepseek-v4-flash" in model_key or "v4-flash" in model_key:
        price = prices.get("deepseek-v4-flash")
    elif "deepseek-chat" in model_key or "v3" in model_key:
        price = prices.get("deepseek-chat")
    elif "reasoner" in model_key:
        price = prices.get("deepseek-reasoner")
    elif "gpt-4o-mini" in model_key:
        price = prices.get("gpt-4o-mini")
    elif "gpt-4o" in model_key:
        price = prices.get("gpt-4o")
    else:
        return None
    if price is None:
        return None

    cost = (input_tokens / 1_000_000 * price["input"]) + (
        output_tokens / 1_000_000 * price["output"]
    )
    return round(cost, 6)


def log_event(
    logger: logging.Logger,
    event: str,
    level: int = logging.INFO,
    **fields: Any,
) -> None:
    """Emit one simplified telemetry event."""
    # Extração de campos chave para um log mais limpo
    elapsed = fields.get("elapsed_seconds")
    iterations = fields.get("iterations")
    usage = fields.get("usage")

    # Busca model em diferentes níveis de aninhamento
    provider_meta = fields.get("provider_metadata") or {}
    model = (
        fields.get("model")
        or fields.get("provider_model")
        or (
            provider_meta.get("model")
            if isinstance(provider_meta, dict)
            else None
        )
    )

    question = fields.get("question_preview") or fields.get("query_preview")
    tool = fields.get("tool_name")

    msg_parts = [f"EVENT: {event}"]

    if question:
        msg_parts.append(f"QUERY: {question}")
    if tool:
        msg_parts.append(f"TOOL: {tool}")
    if model:
        msg_parts.append(f"MODEL: {model}")
    if iterations is not None:
        msg_parts.append(f"ITERS: {iterations}")
    if elapsed is not None:
        time_val = (
            round(elapsed, 2) if isinstance(elapsed, (int, float)) else elapsed
        )
        msg_parts.append(f"TIME: {time_val}s")

    # Tokens e Cálculo de Custo
    input_tokens = 0
    output_tokens = 0
    reported_cost = None

    if usage and isinstance(usage, dict):
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        tokens = usage.get("total_tokens") or (input_tokens + output_tokens)
        if tokens:
            msg_parts.append(f"TOKENS: {tokens}")
    elif isinstance(provider_meta, dict) and "usage" in provider_meta:
        usage_data = provider_meta["usage"]
        if isinstance(usage_data, dict):
            input_tokens = usage_data.get("input_tokens", 0)
            output_tokens = usage_data.get("output_tokens", 0)
            tokens = usage_data.get("total_tokens")
            if tokens:
                msg_parts.append(f"TOKENS: {tokens}")

    if isinstance(provider_meta, dict):
        reported_cost = extract_numeric_cost(provider_meta.get("cost"))

    if reported_cost is not None:
        msg_parts.append(f"COST: ${reported_cost:.6f}")
    elif model and (input_tokens or output_tokens):
        estimated_cost = calculate_cost(model, input_tokens, output_tokens)
        if estimated_cost is not None:
            msg_parts.append(f"EST_COST: ${estimated_cost:.6f}")

    # Mantém o payload JSON apenas se o nível for DEBUG
    if logger.isEnabledFor(logging.DEBUG):
        payload = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **{key: _sanitize(value) for key, value in fields.items()},
        }
        message = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    else:
        message = " | ".join(msg_parts)

    logger.log(level, message)


def now_seconds() -> float:
    """Small wrapper to ease testing and keep timing calls consistent."""
    return perf_counter()


def elapsed_seconds(start: float) -> float:
    """Return rounded elapsed seconds since ``start``."""
    return round(perf_counter() - start, 6)


def preview_text(text: str, limit: int = 160) -> str:
    """Return a single-line preview for logging."""
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def extract_usage_metrics(raw_response: Any) -> dict[str, int] | None:
    """Extract token usage from common provider response shapes."""
    usage = getattr(raw_response, "usage", None)
    if usage is None and isinstance(raw_response, Mapping):
        usage = raw_response.get("usage")

    if usage is None:
        return None

    def _read(obj: Any, *keys: str) -> int | None:
        for key in keys:
            if isinstance(obj, Mapping) and key in obj:
                value = obj[key]
                return int(value) if value is not None else None
            if hasattr(obj, key):
                value = getattr(obj, key)
                return int(value) if value is not None else None
        return None

    prompt_tokens = _read(usage, "prompt_tokens", "input_tokens")
    completion_tokens = _read(usage, "completion_tokens", "output_tokens")
    total_tokens = _read(usage, "total_tokens")

    if (
        prompt_tokens is None
        and completion_tokens is None
        and total_tokens is None
    ):
        return None

    if total_tokens is None:
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

    return {
        "input_tokens": prompt_tokens or 0,
        "output_tokens": completion_tokens or 0,
        "total_tokens": total_tokens,
    }


def _mapping_from_object(value: Any) -> Mapping[str, Any] | None:
    """Best-effort conversion from provider objects to mapping-like data."""
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "model_dump"):
        dumped = value.model_dump()
        return dumped if isinstance(dumped, Mapping) else None
    if hasattr(value, "__dict__"):
        raw = vars(value)
        return raw if isinstance(raw, Mapping) else None
    return None


def extract_provider_response_metadata(raw_response: Any) -> dict[str, Any]:
    """Extract useful native metadata from a provider response object."""
    payload = _mapping_from_object(raw_response) or {}
    usage = extract_usage_metrics(raw_response)

    response_id = payload.get("id") or getattr(raw_response, "id", None)
    model = payload.get("model") or getattr(raw_response, "model", None)
    system_fingerprint = payload.get("system_fingerprint") or getattr(
        raw_response, "system_fingerprint", None
    )

    choices = payload.get("choices")
    finish_reason = None
    if isinstance(choices, list) and choices:
        first = choices[0]
        first_map = _mapping_from_object(first) or {}
        finish_reason = first_map.get("finish_reason")

    cost_candidates = [
        "cost",
        "estimated_cost",
        "total_cost",
        "request_cost",
        "response_cost",
    ]
    cost_info = None
    for key in cost_candidates:
        if key in payload:
            cost_info = payload[key]
            break

    billing = payload.get("billing")
    if cost_info is None and billing is not None:
        cost_info = billing

    return {
        "response_id": response_id,
        "model": model,
        "finish_reason": finish_reason,
        "system_fingerprint": system_fingerprint,
        "usage": usage,
        "cost": extract_numeric_cost(cost_info),
        "cost_details": cost_info,
    }


def extract_langchain_usage(message: Any) -> dict[str, int] | None:
    """Extract usage metadata from a LangChain message object."""
    usage = getattr(message, "usage_metadata", None)
    if not usage:
        response_metadata = getattr(message, "response_metadata", {}) or {}
        usage = response_metadata.get("token_usage")

    if not usage:
        return None

    input_tokens = int(
        usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0
    )
    output_tokens = int(
        usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0
    )
    total_tokens = int(
        usage.get("total_tokens", input_tokens + output_tokens) or 0
    )
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def extract_langchain_response_metadata(message: Any) -> dict[str, Any]:
    """Extract useful native metadata from a LangChain AI message."""
    response_metadata = getattr(message, "response_metadata", {}) or {}
    usage = extract_langchain_usage(message)

    cost_info = None
    for key in (
        "cost",
        "estimated_cost",
        "total_cost",
        "request_cost",
        "response_cost",
        "billing",
    ):
        if key in response_metadata:
            cost_info = response_metadata[key]
            break

    return {
        "model": response_metadata.get("model_name"),
        "finish_reason": response_metadata.get("finish_reason"),
        "response_id": response_metadata.get("id"),
        "system_fingerprint": response_metadata.get("system_fingerprint"),
        "usage": usage,
        "cost": extract_numeric_cost(cost_info),
        "cost_details": cost_info,
        "raw_response_metadata": response_metadata,
    }
