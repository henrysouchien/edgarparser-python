from __future__ import annotations

from edgarparser import EdgarClient


def main() -> None:
    client = EdgarClient()
    payload = client.search_filing_text("AAPL", "risk", year=2025, quarter=1)
    for hit in payload.get("hits", [])[:3]:
        section = hit.get("section_header") or hit.get("section_key")
        print(section, hit.get("snippet"))


if __name__ == "__main__":
    main()
