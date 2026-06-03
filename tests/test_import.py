from __future__ import annotations


def test_import_exports_client_and_version() -> None:
    import edgarparser
    from edgarparser import EdgarAPIError, EdgarClient, EdgarError

    assert edgarparser.__version__ == "0.1.1"
    assert EdgarClient.__name__ == "EdgarClient"
    assert EdgarError.__name__ == "EdgarError"
    assert issubclass(EdgarAPIError, EdgarError)
    assert hasattr(EdgarClient, "get_financials")
    assert hasattr(EdgarClient, "warm_metric_cache_status")
