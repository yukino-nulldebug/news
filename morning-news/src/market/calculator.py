"""Morning News フェーズ1 のマーケット変化率を計算する。"""

from __future__ import annotations

from typing import Optional


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def calculate_change(
    current_value: float,
    previous_close: float,
) -> tuple[Optional[float], Optional[float]]:
    """前日比と変化率を計算する。"""
    if not _is_number(current_value) or not _is_number(previous_close):
        raise ValueError("current_value と previous_close は数値である必要があります。")

    if previous_close == 0:
        return None, None

    raw_change = current_value - previous_close
    change = round(raw_change, 2)
    change_rate = round(raw_change / previous_close * 100, 2)
    return change, change_rate


def calculate_market_changes(items: list[dict]) -> list[dict]:
    """各マーケット項目に前日比と変化率の項目を追加する。"""
    calculated_items = []
    for item in items:
        calculated = dict(item)
        change, change_rate = calculate_change(
            calculated["current_value"],
            calculated["previous_close"],
        )
        calculated["change"] = change
        calculated["change_rate"] = change_rate
        calculated_items.append(calculated)
    return calculated_items
