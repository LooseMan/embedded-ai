#!/usr/bin/env python3
"""MCP server for checking Japanese public holidays with jpholiday."""

from __future__ import annotations

from datetime import date
from typing import Any

import jpholiday
from mcp.server.mcpserver import MCPServer


server = MCPServer("jholiday")


@server.tool()
def check_holiday(target_date: str) -> dict[str, Any]:
    """指定日が日本の祝日か判定する。

    Args:
        target_date: ISO 8601形式の日付（YYYY-MM-DD）。

    Returns:
        is_holiday、holiday_name、date を含む判定結果。
    """
    try:
        parsed_date = date.fromisoformat(target_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("target_date は YYYY-MM-DD 形式で指定してください") from exc

    holiday_name = jpholiday.is_holiday_name(parsed_date)
    return {
        "date": parsed_date.isoformat(),
        "is_holiday": bool(holiday_name),
        "holiday_name": holiday_name or None,
    }


if __name__ == "__main__":
    server.run(transport="stdio")
