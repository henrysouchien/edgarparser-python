from __future__ import annotations

from edgarparser import EdgarClient


def main() -> None:
    client = EdgarClient()
    payload = client.get_metric_series(
        "AAPL",
        "Revenue",
        end_year=2025,
        end_quarter=1,
        periods=4,
        date_type="Q",
    )
    for point in payload.get("series", []):
        print(point.get("period"), point.get("value"))


if __name__ == "__main__":
    main()
