from __future__ import annotations

from typing import Any

from edgarparser import EdgarClient


class FakeResponse:
    status_code = 200
    text = ""
    headers: dict[str, str] = {}
    url = "https://api.example.com"

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {"status": "success"}

    def json(self) -> dict[str, Any]:
        return self.payload


class RecordingSession:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        return FakeResponse({"ok": True})

    def close(self) -> None:
        pass


def _client() -> tuple[EdgarClient, RecordingSession]:
    session = RecordingSession()
    client = EdgarClient(
        api_key="x",
        base_url="https://api.example.com/",
        session=session,  # type: ignore[arg-type]
    )
    return client, session


def _call(session: RecordingSession) -> dict[str, Any]:
    assert len(session.calls) == 1
    return session.calls[0]


def test_get_financials() -> None:
    client, session = _client()

    assert client.get_financials("AAPL", year=2025, quarter=1) == {"ok": True}

    call = _call(session)
    assert call["method"] == "GET"
    assert call["url"] == "https://api.example.com/api/financials"
    assert call["params"] == {
        "ticker": "AAPL",
        "year": 2025,
        "quarter": 1,
        "full_year_mode": False,
        "source": "auto",
    }


def test_get_metric_omits_none_optional_params() -> None:
    client, session = _client()

    client.get_metric(
        "AAPL",
        "Revenue",
        year=2025,
        quarter=1,
        role="income_statement",
    )

    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "year": 2025,
        "quarter": 1,
        "metric_name": "Revenue",
        "full_year_mode": False,
        "source": "auto",
        "role": "income_statement",
    }


def test_get_metric_series_supports_equivalence_role_and_axis() -> None:
    client, session = _client()

    client.get_metric_series(
        "AAPL",
        "Revenue",
        end_year=2025,
        end_quarter=1,
        include_equivalents=True,
        role="income_statement",
        axis_key="ProductAxis",
    )

    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "metric_name": "Revenue",
        "end_year": 2025,
        "end_quarter": 1,
        "periods": 8,
        "full_year_mode": False,
        "source": "auto",
        "include_equivalents": True,
        "cached_only": False,
        "role": "income_statement",
        "axis_key": "ProductAxis",
    }


def test_list_metrics() -> None:
    client, session = _client()

    client.list_metrics(
        "AAPL",
        year=2025,
        quarter=1,
        date_type="Q",
        limit=25,
        include_values=False,
    )

    assert _call(session)["url"] == "https://api.example.com/api/financials/list_metrics"
    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "year": 2025,
        "quarter": 1,
        "full_year_mode": False,
        "source": "auto",
        "date_type": "Q",
        "limit": 25,
        "include_values": False,
    }


def test_search_metrics_supports_repeated_role_values() -> None:
    client, session = _client()

    client.search_metrics(
        "AAPL",
        "revenue",
        year=2025,
        quarter=1,
        role=("income_statement", "cash_flow_statement"),
    )

    assert _call(session)["params"]["role"] == [
        "income_statement",
        "cash_flow_statement",
    ]
    assert _call(session)["url"] == "https://api.example.com/api/financials/search_metrics"


def test_search_metrics_accepts_single_role_string() -> None:
    client, session = _client()

    client.search_metrics(
        "AAPL",
        "revenue",
        year=2025,
        quarter=1,
        role="income_statement",
    )

    assert _call(session)["params"]["role"] == "income_statement"


def test_get_statement_supports_range_mode() -> None:
    client, session = _client()

    client.get_statement(
        "AAPL",
        "income",
        period_from="FY2023",
        period_to="FY2025",
        date_type="FY",
    )

    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "statement": "income",
        "full_year_mode": False,
        "period_from": "FY2023",
        "period_to": "FY2025",
        "source": "auto",
        "date_type": "FY",
    }


def test_get_filings() -> None:
    client, session = _client()

    client.get_filings("AAPL", year=2025, quarter=1, source="auto")

    assert _call(session)["url"] == "https://api.example.com/api/filings"
    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "year": 2025,
        "quarter": 1,
        "source": "auto",
    }


def test_get_filing_document_supports_accession_and_slice_params() -> None:
    client, session = _client()

    client.get_filing_document(
        ticker="AAPL",
        accession="0000320193-25-000073",
        cik="320193",
        form_type="10-Q",
        primary_document="aapl-20250329.htm",
        sections="item_2",
        char_start=10,
        char_end=100,
    )

    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "source": "auto",
        "accession": "0000320193-25-000073",
        "cik": "320193",
        "form_type": "10-Q",
        "primary_document": "aapl-20250329.htm",
        "sections": "item_2",
        "char_start": 10,
        "char_end": 100,
        "max_chars": 200000,
    }


def test_search_filing_text() -> None:
    client, session = _client()

    client.search_filing_text("AAPL", "risk", year=2025, quarter=1)

    assert _call(session)["url"] == "https://api.example.com/api/filing/text/search"
    assert _call(session)["params"] == {
        "ticker": "AAPL",
        "year": 2025,
        "quarter": 1,
        "source": "auto",
        "query": "risk",
    }


def test_warm_metric_cache_single_item() -> None:
    client, session = _client()

    client.warm_metric_cache(ticker="AAPL", year=2025, quarter=1, full_year_mode=True)

    assert _call(session)["method"] == "POST"
    assert _call(session)["url"] == "https://api.example.com/api/warm"
    assert _call(session)["json"] == {
        "items": [
            {
                "ticker": "AAPL",
                "year": 2025,
                "quarter": 1,
                "full_year_mode": True,
            }
        ]
    }


def test_warm_metric_cache_batch_items() -> None:
    client, session = _client()

    client.warm_metric_cache(
        [
            {"ticker": "AAPL", "year": 2025, "quarter": 1, "full_year_mode": False},
            {"ticker": "MSFT", "year": 2025, "quarter": 1, "full_year_mode": False},
        ]
    )

    assert _call(session)["json"] == {
        "items": [
            {"ticker": "AAPL", "year": 2025, "quarter": 1, "full_year_mode": False},
            {"ticker": "MSFT", "year": 2025, "quarter": 1, "full_year_mode": False},
        ]
    }


def test_warm_metric_cache_requires_items_or_single_scope() -> None:
    client, _session = _client()

    try:
        client.warm_metric_cache()
    except ValueError as exc:
        assert "provide items" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_warm_metric_cache_status() -> None:
    client, session = _client()

    client.warm_metric_cache_status("job/123?x=1")

    assert _call(session)["method"] == "GET"
    assert _call(session)["url"] == (
        "https://api.example.com/api/warm/job%2F123%3Fx%3D1"
    )
    assert _call(session)["params"] == {}
