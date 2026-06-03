# edgarparser-sdk

Python SDK for the hosted EdgarParser API.

```bash
pip install edgarparser-sdk
```

```python
from edgarparser import EdgarClient

client = EdgarClient(api_key="...")
print(client)
```

## Status

This package is being implemented in the EdgarParser source repo and is not
published yet. The current local package exports `EdgarClient`, typed SDK
errors, and the first v1 hosted-API endpoint methods.

## Package Boundary

Install `edgarparser-sdk` and import `edgarparser` when you want the hosted
EdgarParser API from Python.

Use `edgar-parser` when you want the local parsing library.

Use `edgar-mcp` when you want AI-agent tools over the hosted API.

The SDK is intentionally a thin HTTP client. It should not parse filings
locally, rank metric matches, resolve tag equivalence, or mutate server caches
as a hidden side effect.

## Configuration

`EdgarClient` accepts an explicit API key:

```python
from edgarparser import EdgarClient

client = EdgarClient(api_key="edgar_...")
```

It can also read `EDGAR_API_KEY`:

```python
from edgarparser import EdgarClient

client = EdgarClient()
```

Use `base_url` for staging or local API testing:

```python
client = EdgarClient(api_key="edgar_...", base_url="http://127.0.0.1:8000")
```

## V1 Methods

The current local SDK surface includes:

- `get_financials`
- `get_metric`
- `get_metric_series`
- `list_metrics`
- `search_metrics`
- `get_statement`
- `get_filings`
- `get_filing_document`
- `search_filing_text`
- `warm_metric_cache`
- `warm_metric_cache_status`

## Examples

From `packages/edgarparser/` or the synced package repo, run examples with
`EDGAR_API_KEY` set:

```bash
EDGAR_API_KEY=... python examples/financials.py
EDGAR_API_KEY=... python examples/metric_series.py
EDGAR_API_KEY=... python examples/filing_search.py
```

## Development

From the repo root:

```bash
python -m pip install -e packages/edgarparser
python -m pytest packages/edgarparser/tests -q
```
