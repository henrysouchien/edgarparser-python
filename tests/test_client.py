from __future__ import annotations

import pytest

from edgarparser import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, EdgarClient


class RecordingSession:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_client_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EDGAR_API_KEY", raising=False)

    client = EdgarClient()

    assert client.base_url == DEFAULT_BASE_URL
    assert client.timeout == DEFAULT_TIMEOUT
    assert client.headers() == {"User-Agent": "edgarparser-sdk/0.1.1"}
    assert "api_key=<unset>" in repr(client)


def test_client_reads_env_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EDGAR_API_KEY", "secret-key")

    client = EdgarClient()

    assert client.headers()["Authorization"] == "Bearer secret-key"
    assert "secret-key" not in repr(client)
    assert "api_key=<set>" in repr(client)


def test_explicit_api_key_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EDGAR_API_KEY", "env-key")

    client = EdgarClient(api_key="explicit-key")

    assert client.headers()["Authorization"] == "Bearer explicit-key"
    assert "explicit-key" not in repr(client)


def test_base_url_is_normalized() -> None:
    client = EdgarClient(api_key="x", base_url="https://api.example.com/")

    assert client.base_url == "https://api.example.com"


def test_client_validates_base_url_and_timeout() -> None:
    with pytest.raises(ValueError, match="base_url"):
        EdgarClient(base_url="")
    with pytest.raises(ValueError, match="timeout"):
        EdgarClient(timeout=0)


def test_client_closes_owned_session() -> None:
    client = EdgarClient(api_key="x")
    client.close()
    client.close()

    assert client._debug_state()["closed"] is True


def test_client_does_not_close_injected_session() -> None:
    session = RecordingSession()

    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]
    client.close()

    assert session.closed is False
    assert client._debug_state()["closed"] is True


def test_context_manager_closes_owned_session() -> None:
    with EdgarClient(api_key="x") as client:
        assert client._debug_state()["closed"] is False

    assert client._debug_state()["closed"] is True
