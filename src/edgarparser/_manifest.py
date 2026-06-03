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
    schema_fingerprint: str
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
        contract_version="1.0.0",
        schema_fingerprint="sha256:8c2b5486165eb2628dfb324c558c1148a48a46453f4102f0491e16503316b1c5",
        required_params=("ticker", "year", "quarter"),
        optional_params=("full_year_mode", "source"),
    ),
    SDKMethodSpec(
        sdk_method="get_metric",
        tool_name="get_metric",
        api_method="GET",
        api_path="/api/metric",
        contract_version="1.0.0",
        schema_fingerprint="sha256:0350ec893a5d3a2a2510dc059711a93f6ec9665a0e068b32d8c4b2d8cb8accd8",
        required_params=("ticker", "year", "quarter", "metric_name"),
        optional_params=("full_year_mode", "source", "date_type", "role"),
    ),
    SDKMethodSpec(
        sdk_method="get_metric_series",
        tool_name="get_metric_series",
        api_method="GET",
        api_path="/api/metric/series",
        contract_version="1.1.0",
        schema_fingerprint="sha256:dff62ae8bf4eb8c648776ac91e02e324c83a1cccbf3beeefcb7855272970a906",
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
        contract_version="1.0.0",
        schema_fingerprint="sha256:07341bd265a257b8c90ee99b42ecef054e6eaa16c2f341f91ffae287bfe907d8",
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
        contract_version="1.0.0",
        schema_fingerprint="sha256:381c0bf743038780d55c447b0c7103da0e22d13c33b866c73130b7265071853c",
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
        contract_version="1.0.0",
        schema_fingerprint="sha256:6da91e176e78fe536130ed3ea11cf9b8dfccf923cbbfc47483d7cb2108383986",
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
        schema_fingerprint="sha256:ffa7e669b836cbbc181bc337cb55219e55bf9a5c75ce3d27040a8aad25f8c993",
        required_params=("ticker", "year", "quarter"),
        optional_params=("source",),
    ),
    SDKMethodSpec(
        sdk_method="get_filing_document",
        tool_name="get_filing_document",
        api_method="GET",
        api_path="/api/filing/document",
        contract_version="1.0.0",
        schema_fingerprint="sha256:4d559aded5c9760ccb498944a984a128254a76349348de297da30ee338ff123a",
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
        contract_version="1.0.0",
        schema_fingerprint="sha256:be08198a156e55118e9b32a0fb41ead07906469059fb27d3010f1a1f5a9c0c8c",
        required_params=("ticker", "year", "quarter", "query"),
        optional_params=("source",),
    ),
    SDKMethodSpec(
        sdk_method="warm_metric_cache",
        tool_name="warm_metric_cache",
        api_method="POST",
        api_path="/api/warm",
        contract_version="1.0.0",
        schema_fingerprint="sha256:1636aba36d166ecf2901e72078fc8a6182f7174e541d9183561392781e8f8cbd",
        body_params=("items",),
    ),
    SDKMethodSpec(
        sdk_method="warm_metric_cache_status",
        tool_name="warm_metric_cache_status",
        api_method="GET",
        api_path="/api/warm/{job_id}",
        contract_version="1.0.0",
        schema_fingerprint="sha256:f48e0b9a707e404c640822af06d51f3523f54538fed625a24ee06dc220cb3245",
        path_params=("job_id",),
    ),
)

SDK_METHODS_BY_NAME = {spec.sdk_method: spec for spec in SDK_METHODS}
