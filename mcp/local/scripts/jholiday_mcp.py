#!/usr/bin/env python3
"""MCP server for checking Company holidays with jpholiday."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import jpholiday
from mcp.server.mcpserver import MCPServer

# 休日とみなす曜日番号の集合（0=月曜日〜6=日曜日）
WEEKEND_DAYS = {5, 6}

SCRIPT_DIR = Path(__file__).resolve().parent

server = MCPServer("jholiday")

def holiday_result(
    target_date: str, is_holiday: bool, holiday_name: str
) -> dict[str, Any]:
    """休日判定結果の辞書を作成して返す。"""
    return {
        "date": target_date,
        "is_holiday": is_holiday,
        "holiday_name": holiday_name,
    }

def load_special_dates(year: int) -> dict[str, dict[str, str]]:
    """スクリプトと同じ階層にある年別JSONを読み込む。"""
    path = SCRIPT_DIR / f"{year}.json"
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"special_holidays": {}, "special_workdays": {}}

@server.tool()
def check_holiday(target_date: str) -> dict[str, Any]:
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

    special_dates = load_special_dates(parsed_date.year)

    # 年別設定ファイルのキーは月日（MM-DD）で管理しているため、年を除いて比較する。
    month_day = formatted_date[5:]

    # 特別休暇
    if month_day in special_dates["special_holidays"]:
        return holiday_result(
            formatted_date, True, special_dates["special_holidays"][month_day]
        )

    # 特別出社
    if month_day in special_dates["special_workdays"]:
        return holiday_result(
            formatted_date, False, special_dates["special_workdays"][month_day]
        )

    # 祝日判定
    holiday_name = jpholiday.is_holiday_name(parsed_date)
    if holiday_name:
        return holiday_result(formatted_date, True, holiday_name)

    # 曜日判定
    weekday = parsed_date.weekday()
    if weekday in WEEKEND_DAYS:
        return holiday_result(formatted_date, True, "休日")

    return holiday_result(formatted_date, False, "平日")

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
