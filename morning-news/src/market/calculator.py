"""Morning News のマーケット変化率を計算する。"""

from __future__ import annotations

from typing import Optional

from src.utils.exceptions import MarketCalculationError

FEATURE_ID = "F-05"
PROCESS_NAME = "market.calculator"
CALCULATION_WARNING_KEY = "calculation_warning"


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


def _item_name(item: dict, index: int) -> str:
    return str(item.get("name") or item.get("symbol") or f"items[{index}]")


def _calculation_warning(item: dict, index: int, reason: str) -> str:
    return f"{_item_name(item, index)} は {reason} のため前日比と変化率を計算できませんでした"


def calculate_market_changes(items: list[dict]) -> list[dict]:
    """各マーケット項目に前日比と変化率の項目を追加する。"""
    calculated_items = []
    for index, item in enumerate(items):
        calculated = dict(item)
        calculated.pop(CALCULATION_WARNING_KEY, None)
        try:
            change, change_rate = calculate_change(
                calculated["current_value"],
                calculated["previous_close"],
            )
        except KeyError as error:
            missing_key = str(error).strip("'")
            change, change_rate = None, None
            calculated[CALCULATION_WARNING_KEY] = _calculation_warning(
                calculated,
                index,
                f"{missing_key} が欠損している",
            )
        except MarketCalculationError:
            change, change_rate = None, None
            calculated[CALCULATION_WARNING_KEY] = _calculation_warning(
                calculated,
                index,
                "current_value または previous_close が数値でない",
            )
        if change is None and change_rate is None and CALCULATION_WARNING_KEY not in calculated:
            calculated[CALCULATION_WARNING_KEY] = _calculation_warning(
                calculated,
                index,
                "previous_close が 0",
            )
        calculated["change"] = change
        calculated["change_rate"] = change_rate
        calculated_items.append(calculated)
    return calculated_items
