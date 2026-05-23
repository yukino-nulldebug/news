"""Morning News のサンプルマーケット情報を読み込む。"""

from __future__ import annotations

import json
from pathlib import Path

from src.utils.exceptions import DataLoadError, DataValidationError

REQUIRED_MARKET_FIELDS = ("symbol", "name", "fetched_at")
FEATURE_ID = "F-04"
PROCESS_NAME = "market.fetcher"


def _load_json(file_path: Path, feature_id: str) -> dict:
    try:
        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise DataLoadError(
            f"{file_path} が見つかりません。",
            feature_id=feature_id,
            process_name=PROCESS_NAME,
        ) from error
    except json.JSONDecodeError as error:
        raise DataLoadError(
            f"{file_path} のJSON形式が不正です: {error}",
            feature_id=feature_id,
            process_name=PROCESS_NAME,
        ) from error

    if not isinstance(data, dict):
        raise DataValidationError(
            f"{file_path} のトップレベルはオブジェクトである必要があります。",
            feature_id=feature_id,
            process_name=PROCESS_NAME,
        )
    return data


def _validate_market_item(
    item: dict,
    index: int,
    file_path: Path,
    feature_id: str,
) -> dict:
    if not isinstance(item, dict):
        raise DataValidationError(
            f"{file_path} の items[{index}] はオブジェクトである必要があります。",
            feature_id=feature_id,
            process_name=PROCESS_NAME,
        )

    missing_fields = [
        field for field in REQUIRED_MARKET_FIELDS if field not in item or item[field] in (None, "")
    ]
    if missing_fields:
        raise DataValidationError(
            f"{file_path} の items[{index}] で必須項目が欠損しています: {', '.join(missing_fields)}",
            feature_id=feature_id,
            process_name=PROCESS_NAME,
        )

    normalized = dict(item)
    normalized["unit"] = normalized.get("unit", "")
    return normalized


def load_market_items(file_path: Path, feature_id: str = FEATURE_ID) -> list[dict]:
    """サンプルJSONからマーケット一覧を読み込み、検証する。"""
    data = _load_json(file_path, feature_id)
    items = data.get("items")
    if not isinstance(items, list):
        raise DataValidationError(
            f"{file_path} の items は配列である必要があります。",
            feature_id=feature_id,
            process_name=PROCESS_NAME,
        )

    return [
        _validate_market_item(item, index, file_path, feature_id)
        for index, item in enumerate(items)
    ]


def fetch_sample_markets(settings: dict) -> list[dict]:
    """フェーズ1用のサンプルマーケット情報を読み込む。"""
    return load_market_items(settings["market_path"])
