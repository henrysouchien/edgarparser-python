from __future__ import annotations

from edgarparser import EdgarClient


def main() -> None:
    client = EdgarClient()
    payload = client.get_financials("AAPL", year=2025, quarter=1)
    print(payload["status"])
    print(len(payload.get("facts", [])))


if __name__ == "__main__":
    main()
