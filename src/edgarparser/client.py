"""Client scaffold for the hosted EdgarParser API."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from types import TracebackType
from typing import Any
from urllib.parse import quote

import requests

from .errors import (
    EdgarAPIError,
    EdgarAuthError,
    EdgarError,
    EdgarNotFoundError,
    EdgarRateLimitError,
    EdgarTimeoutError,
    EdgarTransportError,
    EdgarValidationError,
)

DEFAULT_BASE_URL = "https://www.edgarparser.com"
DEFAULT_TIMEOUT = 30.0
_REDACTED = "<redacted>"
_SECRET_FIELD_MARKERS = (
    "authorization",
    "api_key",
    "apikey",
    "cookie",
    "password",
    "token",
    "secret",
)


class EdgarClient:
    """Thin HTTP client for the hosted EdgarParser API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        if not base_url or not base_url.strip():
            raise ValueError("base_url must be a non-empty URL")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self.api_key = api_key if api_key is not None else os.getenv("EDGAR_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session if session is not None else requests.Session()
        self._owns_session = session is None
        self._closed = False

    @property
    def user_agent(self) -> str:
        from . import __version__

        return f"edgarparser-sdk/{__version__}"

    def headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.user_agent}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get_financials(
        self,
        ticker: str,
        *,
        year: int,
        quarter: int,
        full_year_mode: bool = False,
        source: str = "auto",
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/financials",
            params={
                "ticker": ticker,
                "year": year,
                "quarter": quarter,
                "full_year_mode": full_year_mode,
                "source": source,
            },
            timeout=timeout,
        )

    def get_metric(
        self,
        ticker: str,
        metric_name: str,
        *,
        year: int,
        quarter: int,
        full_year_mode: bool = False,
        source: str = "auto",
        date_type: str | None = None,
        role: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/metric",
            params=self._clean_params(
                {
                    "ticker": ticker,
                    "year": year,
                    "quarter": quarter,
                    "metric_name": metric_name,
                    "full_year_mode": full_year_mode,
                    "source": source,
                    "date_type": date_type,
                    "role": role,
                }
            ),
            timeout=timeout,
        )

    def get_metric_series(
        self,
        ticker: str,
        metric_name: str,
        *,
        end_year: int,
        end_quarter: int,
        periods: int = 8,
        full_year_mode: bool = False,
        source: str = "auto",
        date_type: str | None = None,
        include_equivalents: bool = False,
        cached_only: bool = False,
        role: str | None = None,
        axis_key: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/metric/series",
            params=self._clean_params(
                {
                    "ticker": ticker,
                    "metric_name": metric_name,
                    "end_year": end_year,
                    "end_quarter": end_quarter,
                    "periods": periods,
                    "full_year_mode": full_year_mode,
                    "source": source,
                    "date_type": date_type,
                    "include_equivalents": include_equivalents,
                    "cached_only": cached_only,
                    "role": role,
                    "axis_key": axis_key,
                }
            ),
            timeout=timeout,
        )

    def list_metrics(
        self,
        ticker: str,
        *,
        year: int,
        quarter: int,
        full_year_mode: bool = False,
        source: str = "auto",
        date_type: str | None = None,
        limit: int = 200,
        include_values: bool = True,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/financials/list_metrics",
            params=self._clean_params(
                {
                    "ticker": ticker,
                    "year": year,
                    "quarter": quarter,
                    "full_year_mode": full_year_mode,
                    "source": source,
                    "date_type": date_type,
                    "limit": limit,
                    "include_values": include_values,
                }
            ),
            timeout=timeout,
        )

    def search_metrics(
        self,
        ticker: str,
        query: str,
        *,
        year: int,
        quarter: int,
        full_year_mode: bool = False,
        source: str = "auto",
        date_type: str | None = None,
        role: str | Sequence[str] | None = None,
        limit: int = 20,
        include_values: bool = True,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/financials/search_metrics",
            params=self._clean_params(
                {
                    "ticker": ticker,
                    "year": year,
                    "quarter": quarter,
                    "query": query,
                    "full_year_mode": full_year_mode,
                    "source": source,
                    "date_type": date_type,
                    "role": self._role_values(role),
                    "limit": limit,
                    "include_values": include_values,
                }
            ),
            timeout=timeout,
        )

    def get_statement(
        self,
        ticker: str,
        statement: str,
        *,
        year: int | None = None,
        quarter: int | None = None,
        full_year_mode: bool = False,
        period_from: str | None = None,
        period_to: str | None = None,
        source: str = "auto",
        date_type: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/statement",
            params=self._clean_params(
                {
                    "ticker": ticker,
                    "statement": statement,
                    "year": year,
                    "quarter": quarter,
                    "full_year_mode": full_year_mode,
                    "period_from": period_from,
                    "period_to": period_to,
                    "source": source,
                    "date_type": date_type,
                }
            ),
            timeout=timeout,
        )

    def get_filings(
        self,
        ticker: str,
        *,
        year: int,
        quarter: int,
        source: str = "auto",
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/filings",
            params={
                "ticker": ticker,
                "year": year,
                "quarter": quarter,
                "source": source,
            },
            timeout=timeout,
        )

    def get_filing_document(
        self,
        *,
        ticker: str | None = None,
        year: int | None = None,
        quarter: int | None = None,
        source: str = "auto",
        accession: str | None = None,
        cik: str | None = None,
        form_type: str | None = None,
        primary_document: str | None = None,
        sections: str | None = None,
        char_start: int | None = None,
        char_end: int | None = None,
        max_chars: int = 200000,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/filing/document",
            params=self._clean_params(
                {
                    "ticker": ticker,
                    "year": year,
                    "quarter": quarter,
                    "source": source,
                    "accession": accession,
                    "cik": cik,
                    "form_type": form_type,
                    "primary_document": primary_document,
                    "sections": sections,
                    "char_start": char_start,
                    "char_end": char_end,
                    "max_chars": max_chars,
                }
            ),
            timeout=timeout,
        )

    def search_filing_text(
        self,
        ticker: str,
        query: str,
        *,
        year: int,
        quarter: int,
        source: str = "auto",
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/filing/text/search",
            params={
                "ticker": ticker,
                "year": year,
                "quarter": quarter,
                "source": source,
                "query": query,
            },
            timeout=timeout,
        )

    def warm_metric_cache(
        self,
        items: Sequence[Mapping[str, Any]] | None = None,
        *,
        ticker: str | None = None,
        year: int | None = None,
        quarter: int | None = None,
        full_year_mode: bool = False,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        payload_items = self._warm_items(
            items,
            ticker=ticker,
            year=year,
            quarter=quarter,
            full_year_mode=full_year_mode,
        )
        return self._request(
            "POST",
            "/api/warm",
            json={"items": payload_items},
            timeout=timeout,
        )

    def warm_metric_cache_status(
        self,
        job_id: str,
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        if not job_id or not job_id.strip():
            raise ValueError("job_id must be non-empty")
        encoded_job_id = quote(job_id.strip(), safe="")
        return self._request("GET", f"/api/warm/{encoded_job_id}", timeout=timeout)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        if self._closed:
            raise EdgarError("client is closed")
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be positive")

        normalized_method = method.upper()
        url = self._url(path)
        request_metadata = self._request_metadata(
            normalized_method,
            url,
            params=params,
            json=json,
        )

        try:
            response = self._session.request(
                normalized_method,
                url,
                headers=self.headers(),
                params=dict(params or {}),
                json=dict(json or {}) if json is not None else None,
                timeout=timeout or self.timeout,
            )
        except requests.Timeout as exc:
            raise EdgarTimeoutError(request=request_metadata) from exc
        except requests.RequestException as exc:
            message = self._redact_text(str(exc) or "Request failed")
            raise EdgarTransportError(message, request=request_metadata) from exc

        response_metadata = self._response_metadata(response)
        if response.status_code >= 400:
            raise self._api_error_from_response(
                response,
                request=request_metadata,
                response_metadata=response_metadata,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise EdgarAPIError(
                response.status_code,
                "Response was not valid JSON",
                error_type="invalid_json",
                details=self._text_details(response.text),
                request_id=response.headers.get("X-Request-ID"),
                request=request_metadata,
                response=response_metadata,
            ) from exc

    def close(self) -> None:
        if self._closed:
            return
        if self._owns_session:
            self._session.close()
        self._closed = True

    def __enter__(self) -> EdgarClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc, traceback
        self.close()

    def __repr__(self) -> str:
        key_state = "set" if self.api_key else "unset"
        return (
            f"{self.__class__.__name__}("
            f"base_url={self.base_url!r}, "
            f"timeout={self.timeout!r}, "
            f"api_key=<{key_state}>"
            ")"
        )

    def _debug_state(self) -> dict[str, Any]:
        """Return non-secret state for tests and diagnostics."""

        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "api_key_set": bool(self.api_key),
            "closed": self._closed,
            "user_agent": self.user_agent,
        }

    def _url(self, path: str) -> str:
        if not path or not path.strip():
            raise ValueError("path must be a non-empty API path")
        return f"{self.base_url}/{path.lstrip('/')}"

    def _clean_params(self, params: Mapping[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in params.items() if value is not None}

    def _warm_items(
        self,
        items: Sequence[Mapping[str, Any]] | None,
        *,
        ticker: str | None,
        year: int | None,
        quarter: int | None,
        full_year_mode: bool,
    ) -> list[dict[str, Any]]:
        if items is not None:
            if not items:
                raise ValueError("items must contain at least one warm request")
            return [dict(item) for item in items]
        if ticker is None or year is None or quarter is None:
            raise ValueError("provide items or ticker, year, and quarter")
        return [
            {
                "ticker": ticker,
                "year": year,
                "quarter": quarter,
                "full_year_mode": full_year_mode,
            }
        ]

    def _role_values(self, role: str | Sequence[str] | None) -> str | list[str] | None:
        if role is None:
            return None
        if isinstance(role, str):
            return role
        return list(role)

    def _request_metadata(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None,
        json: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "method": method,
            "url": url,
            "headers": self._redact_mapping(self.headers()),
            "params": self._redact_mapping(params or {}),
            "json": self._redact_mapping(json or {}),
        }

    def _response_metadata(self, response: requests.Response) -> dict[str, Any]:
        response_url = getattr(response, "url", None)
        return {
            "status_code": response.status_code,
            "url": (
                self._redact_text(response_url)
                if isinstance(response_url, str)
                else response_url
            ),
            "headers": self._redact_mapping(dict(response.headers)),
        }

    def _api_error_from_response(
        self,
        response: requests.Response,
        *,
        request: Mapping[str, Any],
        response_metadata: Mapping[str, Any],
    ) -> EdgarAPIError:
        payload = self._response_json(response)
        message = f"HTTP {response.status_code}"
        error_type: str | None = self._default_error_type(response.status_code)
        details: Any | None = None

        if isinstance(payload, Mapping):
            message = self._redact_text(
                str(payload.get("message") or payload.get("error") or message)
            )
            error_type = (
                str(payload["error_type"])
                if payload.get("error_type") is not None
                else error_type
            )
            details = self._redact_value(self._details_from_payload(payload))
        else:
            error_type = "non_json_error"
            text = self._redact_text(response.text.strip())
            if text:
                message = text[:300]
                details = self._text_details(text)

        error_cls = self._error_class(response.status_code)
        return error_cls(
            response.status_code,
            message,
            error_type=error_type,
            details=details,
            request_id=response.headers.get("X-Request-ID"),
            request=request,
            response=response_metadata,
        )

    def _response_json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return None

    def _details_from_payload(self, payload: Mapping[str, Any]) -> Any | None:
        details = payload.get("details")
        if details is None and "detail" in payload:
            details = {"detail": payload["detail"]}
        if "cta" not in payload:
            return details
        if details is None:
            return {"cta": payload["cta"]}
        if isinstance(details, dict):
            return {**details, "cta": payload["cta"]}
        return {"details": details, "cta": payload["cta"]}

    def _default_error_type(self, status_code: int) -> str | None:
        if status_code == 429:
            return "rate_limit"
        if status_code in {400, 422}:
            return "validation_error"
        if status_code in {401, 403}:
            return "auth_error"
        if status_code == 404:
            return "not_found"
        return None

    def _error_class(self, status_code: int) -> type[EdgarAPIError]:
        if status_code in {401, 403}:
            return EdgarAuthError
        if status_code == 429:
            return EdgarRateLimitError
        if status_code == 404:
            return EdgarNotFoundError
        if status_code in {400, 422}:
            return EdgarValidationError
        return EdgarAPIError

    def _text_details(self, text: str) -> dict[str, str] | None:
        if not text:
            return None
        return {"text": self._redact_text(text)[:500]}

    def _redact_mapping(self, value: Mapping[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if self._is_secret_key(key):
                redacted[str(key)] = _REDACTED
            else:
                redacted[str(key)] = self._redact_value(item)
        return redacted

    def _redact_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return self._redact_mapping(value)
        if isinstance(value, list):
            return [self._redact_value(item) for item in value]
        if isinstance(value, str):
            return self._redact_text(value)
        return value

    def _is_secret_key(self, key: object) -> bool:
        normalized = str(key).lower().replace("-", "_")
        return (
            normalized == "key"
            or normalized.endswith("_key")
            or any(marker in normalized for marker in _SECRET_FIELD_MARKERS)
        )

    def _redact_text(self, text: str) -> str:
        if self.api_key and len(self.api_key) >= 4:
            return text.replace(self.api_key, _REDACTED)
        return text
