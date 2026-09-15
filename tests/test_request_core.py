from __future__ import annotations

from typing import Any

import pytest
import requests

from edgarparser import (
    EdgarAPIError,
    EdgarAuthError,
    EdgarClient,
    EdgarError,
    EdgarNotFoundError,
    EdgarRateLimitError,
    EdgarTimeoutError,
    EdgarTransportError,
    EdgarValidationError,
    __version__,
)


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        payload: Any = None,
        text: str = "",
        headers: dict[str, str] | None = None,
        url: str = "https://api.example.com/api/test",
        json_error: bool = False,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.text = text
        self.headers = headers or {}
        self.url = url
        self.json_error = json_error

    def json(self) -> Any:
        if self.json_error:
            raise ValueError("not json")
        return self.payload


class FakeSession:
    def __init__(
        self,
        response: FakeResponse | None = None,
        exception: requests.RequestException | None = None,
    ) -> None:
        self.response = response or FakeResponse(payload={})
        self.exception = exception
        self.calls: list[dict[str, Any]] = []
        self.closed = False

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if self.exception is not None:
            raise self.exception
        return self.response

    def close(self) -> None:
        self.closed = True


def test_request_builds_url_headers_params_body_and_timeout() -> None:
    session = FakeSession(FakeResponse(payload={"ok": True}))
    client = EdgarClient(
        api_key="secret-key",
        base_url="https://api.example.com/",
        session=session,  # type: ignore[arg-type]
        timeout=11,
    )

    payload = client._request(
        "get",
        "/api/test",
        params={"ticker": "AAPL"},
        json={"include_values": True},
        timeout=7,
    )

    assert payload == {"ok": True}
    assert session.calls == [
        {
            "method": "GET",
            "url": "https://api.example.com/api/test",
            "headers": {
                "User-Agent": f"edgarparser-sdk/{__version__}",
                "Authorization": "Bearer secret-key",
            },
            "params": {"ticker": "AAPL"},
            "json": {"include_values": True},
            "timeout": 7,
        }
    ]


def test_request_uses_default_timeout() -> None:
    session = FakeSession(FakeResponse(payload={"ok": True}))
    client = EdgarClient(api_key="x", session=session, timeout=13)  # type: ignore[arg-type]

    client._request("GET", "api/test")

    assert session.calls[0]["timeout"] == 13


def test_request_rejects_closed_client() -> None:
    client = EdgarClient(api_key="x")
    client.close()

    with pytest.raises(EdgarError, match="client is closed"):
        client._request("GET", "/api/test")


def test_request_validates_path_and_timeout() -> None:
    client = EdgarClient(api_key="x")

    with pytest.raises(ValueError, match="path"):
        client._request("GET", "")
    with pytest.raises(ValueError, match="timeout"):
        client._request("GET", "/api/test", timeout=0)


def test_success_invalid_json_raises_api_error() -> None:
    session = FakeSession(FakeResponse(status_code=200, text="not json", json_error=True))
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarAPIError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.status_code == 200
    assert exc.error_type == "invalid_json"
    assert exc.details == {"text": "not json"}


def test_api_error_payload_preserves_message_type_details_and_request_id() -> None:
    response = FakeResponse(
        status_code=502,
        payload={
            "status": "error",
            "message": "Upstream failed",
            "error_type": "upstream_failed",
            "details": {"ticker": "AAPL"},
        },
        headers={"X-Request-ID": "req-123"},
    )
    session = FakeSession(response)
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarAPIError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.status_code == 502
    assert exc.message == "Upstream failed"
    assert exc.error_type == "upstream_failed"
    assert exc.details == {"ticker": "AAPL"}
    assert exc.request_id == "req-123"


def test_api_error_payload_redacts_secret_values() -> None:
    response = FakeResponse(
        status_code=400,
        payload={
            "message": "secret-key failed",
            "details": {
                "note": "secret-key in text",
                "api_key": "secret-key",
                "nested": [{"token": "secret-key"}],
            },
        },
    )
    session = FakeSession(response)
    client = EdgarClient(api_key="secret-key", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarValidationError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.message == "<redacted> failed"
    assert exc.details == {
        "note": "<redacted> in text",
        "api_key": "<redacted>",
        "nested": [{"token": "<redacted>"}],
    }


def test_api_error_response_metadata_redacts_url_and_secret_headers() -> None:
    response = FakeResponse(
        status_code=500,
        payload={"message": "Server failed"},
        headers={
            "Set-Cookie": "session=secret-key",
            "X-Password": "secret-key",
            "X-Request-ID": "req-123",
        },
        url="https://api.example.com/api/test?api_key=secret-key",
    )
    session = FakeSession(response)
    client = EdgarClient(api_key="secret-key", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarAPIError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.response["url"] == (
        "https://api.example.com/api/test?api_key=<redacted>"
    )
    assert exc.response["headers"]["Set-Cookie"] == "<redacted>"
    assert exc.response["headers"]["X-Password"] == "<redacted>"
    assert exc.response["headers"]["X-Request-ID"] == "req-123"


def test_auth_error_mapping() -> None:
    session = FakeSession(FakeResponse(status_code=403, payload={"message": "Forbidden"}))
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarAuthError) as exc_info:
        client._request("GET", "/api/test")

    assert exc_info.value.error_type == "auth_error"


def test_not_found_error_mapping() -> None:
    session = FakeSession(FakeResponse(status_code=404, payload={"message": "Missing"}))
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarNotFoundError) as exc_info:
        client._request("GET", "/api/test")

    assert exc_info.value.error_type == "not_found"


def test_validation_detail_payload_maps_to_validation_error() -> None:
    response = FakeResponse(
        status_code=422,
        payload={
            "status": "error",
            "message": "Validation error",
            "detail": [{"loc": ["query", "ticker"], "msg": "field required"}],
        },
    )
    session = FakeSession(response)
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarValidationError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.error_type == "validation_error"
    assert exc.details == {
        "detail": [{"loc": ["query", "ticker"], "msg": "field required"}]
    }


def test_rate_limit_cta_payload_maps_to_rate_limit_error() -> None:
    response = FakeResponse(
        status_code=429,
        payload={
            "status": "error",
            "message": "You've reached your free limit.",
            "cta": {"text": "Register", "url": "https://example.com", "type": "signup"},
        },
    )
    session = FakeSession(response)
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarRateLimitError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.error_type == "rate_limit"
    assert exc.details == {
        "cta": {"text": "Register", "url": "https://example.com", "type": "signup"}
    }


def test_non_json_error_response_preserves_text() -> None:
    session = FakeSession(
        FakeResponse(status_code=500, text="nginx failure", json_error=True)
    )
    client = EdgarClient(api_key="x", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarAPIError) as exc_info:
        client._request("GET", "/api/test")

    exc = exc_info.value
    assert exc.error_type == "non_json_error"
    assert exc.message == "nginx failure"
    assert exc.details == {"text": "nginx failure"}


def test_timeout_maps_to_timeout_error_and_redacts_request_metadata() -> None:
    session = FakeSession(exception=requests.Timeout("secret-key timed out"))
    client = EdgarClient(api_key="secret-key", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarTimeoutError) as exc_info:
        client._request(
            "POST",
            "/api/test",
            params={"api_key": "secret-key", "ticker": "AAPL"},
            json={"token": "secret-key"},
        )

    exc = exc_info.value
    assert exc.request["headers"]["Authorization"] == "<redacted>"
    assert exc.request["params"]["api_key"] == "<redacted>"
    assert exc.request["json"]["token"] == "<redacted>"
    assert "secret-key" not in str(exc)


def test_transport_error_mapping_redacts_api_key() -> None:
    session = FakeSession(exception=requests.ConnectionError("secret-key failed"))
    client = EdgarClient(api_key="secret-key", session=session)  # type: ignore[arg-type]

    with pytest.raises(EdgarTransportError) as exc_info:
        client._request("GET", "/api/test")

    assert exc_info.value.message == "<redacted> failed"
    assert "secret-key" not in str(exc_info.value)
