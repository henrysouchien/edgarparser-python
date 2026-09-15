"""Pinned API contract metadata for SDK-covered EdgarParser endpoints."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SDKMethodSpec:
    sdk_method: str
    tool_name: str
    api_method: str
    api_path: str
    contract_version: str
    required_params: tuple[str, ...] = ()
    optional_params: tuple[str, ...] = ()
    path_params: tuple[str, ...] = ()
    body_params: tuple[str, ...] = ()


SDK_METHODS: tuple[SDKMethodSpec, ...] = (
    SDKMethodSpec(
        sdk_method="get_financials",
        tool_name="get_financials",
        api_method="GET",
        api_path="/api/financials",
        contract_version="2.0.0",
        required_params=("ticker", "year", "quarter"),
        optional_params=("full_year_mode", "source"),
    ),
    SDKMethodSpec(
        sdk_method="get_metric",
        tool_name="get_metric",
        api_method="GET",
        api_path="/api/metric",
        contract_version="2.0.0",
        required_params=("ticker", "year", "quarter", "metric_name"),
        optional_params=("full_year_mode", "source", "date_type", "role"),
    ),
    SDKMethodSpec(
        sdk_method="get_metric_series",
        tool_name="get_metric_series",
        api_method="GET",
        api_path="/api/metric/series",
        contract_version="2.0.0",
        required_params=("ticker", "metric_name", "end_year", "end_quarter"),
        optional_params=(
            "periods",
            "full_year_mode",
            "source",
            "date_type",
            "include_equivalents",
            "cached_only",
            "role",
            "axis_key",
        ),
    ),
    SDKMethodSpec(
        sdk_method="list_metrics",
        tool_name="list_metrics",
        api_method="GET",
        api_path="/api/financials/list_metrics",
        contract_version="1.1.0",
        required_params=("ticker", "year", "quarter"),
        optional_params=(
            "full_year_mode",
            "source",
            "date_type",
            "limit",
            "include_values",
        ),
    ),
    SDKMethodSpec(
        sdk_method="search_metrics",
        tool_name="search_metrics",
        api_method="GET",
        api_path="/api/financials/search_metrics",
        contract_version="1.1.0",
        required_params=("ticker", "year", "quarter", "query"),
        optional_params=(
            "full_year_mode",
            "source",
            "date_type",
            "role",
            "limit",
            "include_values",
        ),
    ),
    SDKMethodSpec(
        sdk_method="get_statement",
        tool_name="get_statement",
        api_method="GET",
        api_path="/api/statement",
        contract_version="2.0.0",
        required_params=("ticker", "statement"),
        optional_params=(
            "year",
            "quarter",
            "full_year_mode",
            "period_from",
            "period_to",
            "source",
            "date_type",
        ),
    ),
    SDKMethodSpec(
        sdk_method="get_filings",
        tool_name="get_filings",
        api_method="GET",
        api_path="/api/filings",
        contract_version="1.0.0",
        required_params=("ticker", "year", "quarter"),
        optional_params=("source",),
    ),
    SDKMethodSpec(
        sdk_method="get_filing_document",
        tool_name="get_filing_document",
        api_method="GET",
        api_path="/api/filing/document",
        contract_version="1.1.0",
        optional_params=(
            "ticker",
            "year",
            "quarter",
            "source",
            "accession",
            "cik",
            "form_type",
            "primary_document",
            "sections",
            "char_start",
            "char_end",
            "max_chars",
        ),
    ),
    SDKMethodSpec(
        sdk_method="search_filing_text",
        tool_name="search_filing_text",
        api_method="GET",
        api_path="/api/filing/text/search",
        contract_version="1.1.0",
        required_params=("ticker", "year", "quarter", "query"),
        optional_params=("source",),
    ),
    SDKMethodSpec(
        sdk_method="warm_metric_cache",
        tool_name="warm_metric_cache",
        api_method="POST",
        api_path="/api/warm",
        contract_version="1.0.0",
        body_params=("items",),
    ),
    SDKMethodSpec(
        sdk_method="warm_metric_cache_status",
        tool_name="warm_metric_cache_status",
        api_method="GET",
        api_path="/api/warm/{job_id}",
        contract_version="1.0.0",
        path_params=("job_id",),
    ),
)

SDK_METHODS_BY_NAME = {spec.sdk_method: spec for spec in SDK_METHODS}
