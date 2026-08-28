"""Small, stateless client for EpidBot's asynchronous chat API."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import requests

DEFAULT_BASE_URL = "https://api.epidbot.kwar-ai.com.br"


class EpidBotError(RuntimeError):
    """Raised when EpidBot cannot answer a delegated question."""


@dataclass(frozen=True)
class EpidBotResult:
    """Validated result returned by EpidBot."""

    content: str


class EpidBotClient:
    """Submit one isolated question and poll its EpidBot job."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        max_wait_seconds: float = 60.0,
        poll_interval_seconds: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("EpidBot API key must not be empty")
        if max_wait_seconds < 0 or poll_interval_seconds < 0:
            raise ValueError("EpidBot timeouts must not be negative")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_wait_seconds = max_wait_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.sleep = sleep
        self.session = session or requests.Session()

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def ask(self, question: str, *, locale: str = "pt") -> EpidBotResult:
        """Ask a fresh EpidBot session and return its text response."""
        if not question.strip():
            raise ValueError("EpidBot question must not be empty")

        deadline = time.monotonic() + self.max_wait_seconds
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat",
                json={
                    "message": question,
                    "session_id": None,
                    "locale": locale,
                },
                headers=self._headers,
                timeout=self._request_timeout(deadline),
            )
        except requests.RequestException as exc:
            raise EpidBotError("EpidBot chat submission failed") from exc
        submitted = self._json_or_error(response, "chat submission")
        job_id = submitted.get("job_id")
        if not isinstance(job_id, str) or not job_id:
            raise EpidBotError("EpidBot submission did not return a job_id")

        while True:
            if time.monotonic() >= deadline:
                raise EpidBotError("EpidBot chat timed out")
            try:
                result_response = self.session.get(
                    f"{self.base_url}/api/v1/chat/{job_id}",
                    headers=self._headers,
                    timeout=self._request_timeout(deadline),
                )
            except requests.RequestException as exc:
                raise EpidBotError("EpidBot chat polling failed") from exc
            result = self._json_or_error(result_response, "chat polling")
            status = result.get("status")
            if status == "completed":
                return self._parse_result(result)
            if status == "failed":
                error = result.get("error") or "unknown EpidBot failure"
                raise EpidBotError(f"EpidBot job failed: {error}")
            if status not in {"processing", "pending"}:
                raise EpidBotError(
                    f"EpidBot returned unknown job status: {status}"
                )
            self.sleep(
                min(
                    self.poll_interval_seconds,
                    max(0, deadline - time.monotonic()),
                )
            )

    @staticmethod
    def _request_timeout(deadline: float) -> tuple[float, float]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise EpidBotError("EpidBot chat timed out")
        return min(5.0, remaining), min(30.0, remaining)

    @staticmethod
    def _json_or_error(response: Any, operation: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except (ValueError, TypeError) as exc:
            raise EpidBotError(
                f"EpidBot {operation} returned invalid JSON"
            ) from exc
        if response.status_code >= 400:
            detail = (
                payload.get("detail") if isinstance(payload, dict) else None
            )
            raise EpidBotError(
                f"EpidBot {operation} failed with HTTP {response.status_code}"
                + (f": {detail}" if detail else "")
            )
        if not isinstance(payload, dict):
            raise EpidBotError(
                f"EpidBot {operation} returned an invalid payload"
            )
        return payload

    @staticmethod
    def _parse_result(payload: dict[str, Any]) -> EpidBotResult:
        content = payload.get("content")
        if not isinstance(content, str):
            raise EpidBotError("EpidBot completed without textual content")
        return EpidBotResult(content=content)
