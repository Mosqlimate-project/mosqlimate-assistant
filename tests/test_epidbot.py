import pytest
import requests

import mosqlimate_assistant.epidbot as epidbot_module
from mosqlimate_assistant.epidbot import EpidBotClient, EpidBotError


class _Response:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.posts = []
        self.gets = []

    def post(self, url, *, json, headers, timeout):
        self.posts.append((url, json, headers, timeout))
        return next(self.responses)

    def get(self, url, *, headers, timeout):
        self.gets.append((url, headers, timeout))
        return next(self.responses)


def test_ask_submits_and_polls_without_reusing_session():
    session = _Session(
        [
            _Response(
                200,
                {"job_id": "job-1", "session_id": 12, "status": "processing"},
            ),
            _Response(
                200,
                {
                    "job_id": "job-1",
                    "status": "completed",
                    "content": "Resposta curta",
                    "images": ["![plot](plots/1.png)"],
                },
            ),
        ]
    )
    client = EpidBotClient(
        "secret",
        base_url="https://epidbot.test",
        poll_interval_seconds=0,
        sleep=lambda _: None,
        session=session,
    )

    result = client.ask("Quais dados de SINAN existem?", locale="pt")

    assert result.content == "Resposta curta"
    assert not hasattr(result, "images")
    assert not hasattr(result, "job_id")
    assert not hasattr(result, "session_id")
    assert session.posts[0][1] == {
        "message": "Quais dados de SINAN existem?",
        "session_id": None,
        "locale": "pt",
    }
    assert session.gets[0][0].endswith("/api/v1/chat/job-1")


def test_each_question_starts_without_a_previous_session():
    session = _Session(
        [
            _Response(200, {"job_id": "job-1", "session_id": 10}),
            _Response(
                200, {"job_id": "job-1", "status": "completed", "content": "A"}
            ),
            _Response(200, {"job_id": "job-2", "session_id": 11}),
            _Response(
                200, {"job_id": "job-2", "status": "completed", "content": "B"}
            ),
        ]
    )
    client = EpidBotClient(
        "secret",
        poll_interval_seconds=0,
        sleep=lambda _: None,
        session=session,
    )

    assert client.ask("primeira").content == "A"
    assert client.ask("segunda").content == "B"
    assert [post[1]["session_id"] for post in session.posts] == [None, None]


def test_ask_raises_provider_error_without_retrying_submission():
    session = _Session([_Response(500, {"detail": "temporary failure"})])
    client = EpidBotClient("secret", session=session)

    with pytest.raises(EpidBotError, match="HTTP 500"):
        client.ask("pergunta")

    assert len(session.posts) == 1


def test_ask_times_out_when_job_never_finishes():
    session = _Session(
        [
            _Response(200, {"job_id": "job-1", "status": "processing"}),
            _Response(200, {"job_id": "job-1", "status": "processing"}),
        ]
    )
    client = EpidBotClient(
        "secret",
        poll_interval_seconds=0,
        max_wait_seconds=0,
        sleep=lambda _: None,
        session=session,
    )

    with pytest.raises(EpidBotError, match="timed out"):
        client.ask("pergunta")


def test_ask_timeout_includes_submission_time(monkeypatch):
    session = _Session(
        [_Response(200, {"job_id": "job-1", "status": "processing"})]
    )
    clock = iter((0.0, 0.1, 1.0))
    monkeypatch.setattr(epidbot_module.time, "monotonic", lambda: next(clock))
    client = EpidBotClient("secret", max_wait_seconds=0.5, session=session)

    with pytest.raises(EpidBotError, match="timed out"):
        client.ask("pergunta")

    assert len(session.posts) == 1
    assert not session.gets


def test_ask_wraps_network_failures():
    class _BrokenSession:
        def post(self, url, **kwargs):
            del url, kwargs
            raise requests.Timeout("offline")

    client = EpidBotClient("secret", session=_BrokenSession())

    with pytest.raises(EpidBotError, match="submission failed"):
        client.ask("pergunta")
