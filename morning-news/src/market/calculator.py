"""Morning News のマーケット変化率を計算する。"""

from __future__ import annotations

from typing import Optional

from src.utils.exceptions import MarketCalculationError

FEATURE_ID = "F-05"
PROCESS_NAME = "market.calculator"


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def calculate_change(
    current_value: float,
    previous_close: float,
) -> tuple[Optional[float], Optional[float]]:
    """前日比と変化率を計算する。"""
    if not _is_number(current_value) or not _is_number(previous_close):
        raise MarketCalculationError(
            "current_value と previous_close は数値である必要があります。",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
        )

    if previous_close == 0:
        return None, None

    raw_change = current_value - previous_close
    change = round(raw_change, 2)
    change_rate = round(raw_change / previous_close * 100, 2)
    return change, change_rate


def calculate_market_changes(items: list[dict]) -> list[dict]:
    """各マーケット項目に前日比と変化率の項目を追加する。"""
    calculated_items = []
    for index, item in enumerate(items):
        calculated = dict(item)
        try:
            change, change_rate = calculate_change(
                calculated["current_value"],
                calculated["previous_close"],
            )
        except KeyError as error:
            raise MarketCalculationError(
                f"items[{index}] の計算に必要な項目がありません: {error}",
                feature_id=FEATURE_ID,
                process_name=PROCESS_NAME,
            ) from error
        calculated["change"] = change
        calculated["change_rate"] = change_rate
        calculated_items.append(calculated)
    return calculated_items
