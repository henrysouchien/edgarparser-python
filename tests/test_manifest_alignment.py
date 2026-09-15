from __future__ import annotations

import inspect
import py_compile
from pathlib import Path
from typing import Any

import pytest

from edgarparser import EdgarClient
from edgarparser._manifest import SDK_METHODS, SDKMethodSpec

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]


def _tool_manifest_path() -> Path | None:
    manifest_path = REPO_ROOT / "docs" / "tool_manifest.yaml"
    return manifest_path if manifest_path.exists() else None


def _source_repo_app() -> Any:
    pytest.importorskip("edgar_api.main")
    from edgar_api.main import app

    return app


def _field_names(fields: list[Any]) -> set[str]:
    return {field.alias or field.name for field in fields}


def _required_field_names(fields: list[Any]) -> set[str]:
    return {
        field.alias or field.name
        for field in fields
        if field.field_info.is_required()
    }


def _optional_field_names(fields: list[Any]) -> set[str]:
    return _field_names(fields) - _required_field_names(fields)


def _route_for_spec(app: Any, spec: SDKMethodSpec) -> Any:
    routes = {
        (route.path, tuple(sorted(route.methods or ()))): route
        for route in app.routes
    }
    return routes[(spec.api_path, (spec.api_method,))]


def _signature_params(method: Any) -> dict[str, inspect.Parameter]:
    signature = inspect.signature(method)
    return {
        name: param
        for name, param in signature.parameters.items()
        if name not in {"self", "timeout"}
    }


def _required_signature_params(params: dict[str, inspect.Parameter]) -> set[str]:
    return {
        name
        for name, param in params.items()
        if param.default is inspect.Parameter.empty
    }


def _optional_signature_params(params: dict[str, inspect.Parameter]) -> set[str]:
    return set(params) - _required_signature_params(params)


def test_sdk_manifest_has_one_spec_per_sdk_method() -> None:
    names = [spec.sdk_method for spec in SDK_METHODS]

    assert len(names) == len(set(names))
    for spec in SDK_METHODS:
        assert hasattr(EdgarClient, spec.sdk_method)


def test_sdk_manifest_matches_tool_manifest_contracts() -> None:
    manifest_path = _tool_manifest_path()
    if manifest_path is None:
        pytest.skip("source repo tool manifest is not available")
    yaml = pytest.importorskip("yaml")

    manifest = yaml.safe_load(manifest_path.read_text())
    tools = {tool["name"]: tool for tool in manifest["tools"]}

    for spec in SDK_METHODS:
        tool = tools[spec.tool_name]
        assert tool["api_method"] == spec.api_method
        assert tool["api_path"] == spec.api_path
        assert tool["contract_version"] == spec.contract_version


def test_sdk_manifest_matches_fastapi_route_contracts() -> None:
    app = _source_repo_app()

    for spec in SDK_METHODS:
        route = _route_for_spec(app, spec)

        assert _field_names(route.dependant.path_params) == set(spec.path_params)
        assert _required_field_names(route.dependant.query_params) == set(
            spec.required_params
        )
        assert _optional_field_names(route.dependant.query_params) == set(
            spec.optional_params
        )


def test_warm_body_params_match_schema() -> None:
    app = _source_repo_app()
    pytest.importorskip("edgar_api.schemas")
    from edgar_api.schemas import WarmRequest

    warm_spec = next(spec for spec in SDK_METHODS if spec.sdk_method == "warm_metric_cache")
    warm_route = _route_for_spec(app, warm_spec)

    assert _field_names(warm_route.dependant.body_params) == {"payload"}
    assert set(warm_spec.body_params) == set(WarmRequest.model_fields)


def test_sdk_wrapper_signatures_match_manifest_params() -> None:
    for spec in SDK_METHODS:
        params = _signature_params(getattr(EdgarClient, spec.sdk_method))
        expected_required = set(spec.required_params) | set(spec.path_params)
        expected_optional = set(spec.optional_params) | set(spec.body_params)

        if spec.sdk_method == "warm_metric_cache":
            expected_required = set()
            expected_optional = {
                "items",
                "ticker",
                "year",
                "quarter",
                "full_year_mode",
            }

        assert _required_signature_params(params) == expected_required
        assert _optional_signature_params(params) == expected_optional


def test_examples_are_syntax_valid() -> None:
    for path in (PACKAGE_ROOT / "examples").glob("*.py"):
        py_compile.compile(str(path), doraise=True)
