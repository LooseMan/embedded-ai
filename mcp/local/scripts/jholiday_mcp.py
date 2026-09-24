#!/usr/bin/env python3
"""MCP server for checking Company holidays with jpholiday."""

from __future__ import annotations

import argparse
import json
from datetime import date
from typing import Any

import jpholiday
from mcp.server.mcpserver import MCPServer

# 曜日数値(0=月, ..., 5=土, 6=日) と名称のハッシュ
WEEKDAY_NAMES: dict[int, str] = {
    0: "月曜日",
    1: "火曜日",
    2: "水曜日",
    3: "木曜日",
    4: "金曜日",
    5: "土曜日",
    6: "日曜日",
}

server = MCPServer("jholiday")

@server.tool()
def check_holiday(target_date: str) -> dict[str, Any] | None:
    """指定日が会社の休日か判定する。

    Args:
        target_date: ISO 8601形式の日付（YYYY-MM-DD）。

    Returns:
        is_holiday、holiday_name、date を含む判定結果（休日でない場合はNone）。
    """
    try:
        parsed_date = date.fromisoformat(target_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("target_date は YYYY-MM-DD 形式で指定してください") from exc
    formatted_date = parsed_date.isoformat()

    # 祝日判定
    holiday_name = jpholiday.is_holiday_name(parsed_date)
    if holiday_name:
        return {
            "date": formatted_date,
            "is_holiday": True,
            "holiday_name": holiday_name,
        }

    # 曜日判定
    weekday = parsed_date.weekday()
    weekday_name = WEEKDAY_NAMES[weekday]
    if weekday_name == "土曜日" or weekday_name == "日曜日":
        return {
            "date": formatted_date,
            "is_holiday": True,
            "holiday_name": weekday_name,
        }

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="会社の休日を判定するMCPサーバー"
    )
    parser.add_argument(
        "target_date",
        nargs="?",
        help="デバッグ用の日付（YYYY-MM-DD）",
    )
    parser.add_argument(
        "--target-date",
        dest="target_date_option",
        help="デバッグ用の日付（YYYY-MM-DD）",
    )
    args = parser.parse_args()

    debug_target_date = args.target_date_option or args.target_date
    if debug_target_date:
        result = check_holiday(debug_target_date)
        print(json.dumps(result, ensure_ascii=False))
    else:
        server.run(transport="stdio")
