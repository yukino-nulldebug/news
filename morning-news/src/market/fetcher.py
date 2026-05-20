"""Morning News フェーズ1 のサンプルマーケット情報を読み込む。"""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_MARKET_FIELDS = ("symbol", "name", "current_value", "previous_close", "fetched_at")


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _load_json(file_path: Path) -> dict:
    try:
        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_path} が見つかりません。")
    except json.JSONDecodeError as error:
        raise ValueError(f"{file_path} のJSON形式が不正です: {error}") from error

    if not isinstance(data, dict):
        raise ValueError(f"{file_path} のトップレベルはオブジェクトである必要があります。")
    return data


def _validate_market_item(item: dict, index: int, file_path: Path) -> dict:
    if not isinstance(item, dict):
        raise ValueError(f"{file_path} の items[{index}] はオブジェクトである必要があります。")

    missing_fields = [
        field for field in REQUIRED_MARKET_FIELDS if field not in item or item[field] in (None, "")
    ]
    if missing_fields:
        raise ValueError(f"{file_path} の items[{index}] で必須項目が欠損しています: {', '.join(missing_fields)}")

    for field in ("current_value", "previous_close"):
        if not _is_number(item[field]):
            raise ValueError(f"{file_path} の items[{index}].{field} は数値である必要があります。")

    normalized = dict(item)
    normalized["unit"] = normalized.get("unit", "")
    return normalized


def load_market_items(file_path: Path) -> list[dict]:
    """サンプルJSONからマーケット一覧を読み込み、検証する。"""
    data = _load_json(file_path)
    items = data.get("items")
    if not isinstance(items, list):
        raise ValueError(f"{file_path} の items は配列である必要があります。")

    return [_validate_market_item(item, index, file_path) for index, item in enumerate(items)]


def fetch_sample_markets(settings: dict) -> list[dict]:
    """フェーズ1用のサンプルマーケット情報を読み込む。"""
    return load_market_items(settings["market_path"])
