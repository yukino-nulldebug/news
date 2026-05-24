"""Morning News のマーケット情報を読み込む。"""

from __future__ import annotations

import json
from pathlib import Path

from src.market.providers.alpha_vantage import fetch_alpha_vantage_markets
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


def _warning_entry(feature_id: str, process_name: str, message: str) -> dict:
    return {
        "feature_id": feature_id,
        "process_name": process_name,
        "message": message,
    }


def _warning_entries(feature_id: str, process_name: str, messages: list[str]) -> list[dict]:
    return [_warning_entry(feature_id, process_name, message) for message in messages]


def fetch_sample_markets(settings) -> list[dict]:
    """サンプルマーケット情報を読み込む。"""
    return load_market_items(settings.market_path)


def fetch_api_markets(settings) -> tuple[list[dict], list[dict]]:
    """Providerに応じて外部マーケット情報を取得する。"""
    if settings.market_provider == "sample":
        return (
            fetch_sample_markets(settings),
            [
                _warning_entry(
                    "F-04",
                    "market.fetcher",
                    "APP_MODE=api ですが MARKET_PROVIDER=sample のためサンプルマーケットを使用しました",
                )
            ],
        )

    if settings.market_provider == "alpha_vantage":
        items, warnings = fetch_alpha_vantage_markets(settings)
        return items, _warning_entries("F-04", "market.alpha_vantage", warnings)

    return (
        [],
        [
            _warning_entry(
                "F-04",
                "market.fetcher",
                f"MARKET_PROVIDER={settings.market_provider} は未対応のためマーケット取得をスキップしました",
            )
        ],
    )


def fetch_markets_for_mode(settings) -> tuple[list[dict], list[dict]]:
    """実行モードに応じてマーケット情報を返す。"""
    if settings.app_mode == "sample":
        return fetch_sample_markets(settings), []
    return fetch_api_markets(settings)
