from __future__ import annotations

from types import SimpleNamespace

from mosqlimate_assistant.monitoring import (
    calculate_cost,
    extract_langchain_response_metadata,
    extract_langchain_usage,
    extract_numeric_cost,
    extract_provider_response_metadata,
    extract_usage_metrics,
)


def test_extract_usage_metrics_reads_openai_like_usage() -> None:
    raw_response = SimpleNamespace(
        usage=SimpleNamespace(
            prompt_tokens=120,
            completion_tokens=30,
            total_tokens=150,
        )
    )

    usage = extract_usage_metrics(raw_response)

    assert usage == {
        "input_tokens": 120,
        "output_tokens": 30,
        "total_tokens": 150,
    }


def test_extract_langchain_usage_reads_usage_metadata() -> None:
    message = SimpleNamespace(
        usage_metadata={
            "input_tokens": 50,
            "output_tokens": 20,
            "total_tokens": 70,
        }
    )

    usage = extract_langchain_usage(message)

    assert usage == {
        "input_tokens": 50,
        "output_tokens": 20,
        "total_tokens": 70,
    }


def test_extract_provider_response_metadata_reads_native_fields() -> None:
    raw_response = SimpleNamespace(
        id="resp_123",
        model="deepseek-v4-flash",
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=25,
            total_tokens=125,
        ),
        choices=[SimpleNamespace(finish_reason="stop")],
        cost={"total_usd": 0.00042},
    )

    metadata = extract_provider_response_metadata(raw_response)

    assert metadata["response_id"] == "resp_123"
    assert metadata["model"] == "deepseek-v4-flash"
    assert metadata["finish_reason"] == "stop"
    assert metadata["usage"] == {
        "input_tokens": 100,
        "output_tokens": 25,
        "total_tokens": 125,
    }
    assert metadata["cost"] == 0.00042
    assert metadata["cost_details"] == {"total_usd": 0.00042}


def test_extract_langchain_response_metadata_reads_native_fields() -> None:
    message = SimpleNamespace(
        usage_metadata={
            "input_tokens": 50,
            "output_tokens": 20,
            "total_tokens": 70,
        },
        response_metadata={
            "model_name": "deepseek-v4-flash",
            "finish_reason": "stop",
            "id": "msg_123",
            "billing": {"total_usd": 0.00021},
        },
    )

    metadata = extract_langchain_response_metadata(message)

    assert metadata["model"] == "deepseek-v4-flash"
    assert metadata["finish_reason"] == "stop"
    assert metadata["response_id"] == "msg_123"
    assert metadata["cost"] == 0.00021
    assert metadata["cost_details"] == {"total_usd": 0.00021}


def test_extract_numeric_cost_reads_nested_billing_payloads() -> None:
    assert extract_numeric_cost(0.12) == 0.12
    assert extract_numeric_cost({"total_usd": 0.34}) == 0.34
    assert extract_numeric_cost({"billing": {"total_usd": 0.56}}) == 0.56
    assert extract_numeric_cost({"cost": {"amount": 0.78}}) == 0.78
    assert extract_numeric_cost({"unknown": "value"}) is None


def test_calculate_cost_uses_current_deepseek_v4_pricing() -> None:
    assert calculate_cost("deepseek-v4-flash", 1_000_000, 1_000_000) == 0.42
    assert calculate_cost("deepseek-v4-pro", 1_000_000, 1_000_000) == 5.22
