"""Morning News フェーズ1 のサンプルニュースを読み込む。"""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_NEWS_FIELDS = ("region", "category", "title", "url", "source", "published_at")
ALLOWED_REGIONS = {"domestic", "global"}


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


def _validate_news_item(item: dict, index: int, file_path: Path) -> dict:
    if not isinstance(item, dict):
        raise ValueError(f"{file_path} の items[{index}] はオブジェクトである必要があります。")

    missing_fields = [
        field for field in REQUIRED_NEWS_FIELDS if field not in item or item[field] in (None, "")
    ]
    if missing_fields:
        raise ValueError(f"{file_path} の items[{index}] で必須項目が欠損しています: {', '.join(missing_fields)}")

    if item["region"] not in ALLOWED_REGIONS:
        raise ValueError(
            f"{file_path} の items[{index}].region は domestic または global である必要があります。"
        )

    normalized = dict(item)
    normalized["summary"] = normalized.get("summary") or ""
    return normalized


def load_news_items(file_path: Path) -> list[dict]:
    """サンプルJSONからニュース一覧を読み込み、検証する。"""
    data = _load_json(file_path)
    items = data.get("items")
    if not isinstance(items, list):
        raise ValueError(f"{file_path} の items は配列である必要があります。")

    return [_validate_news_item(item, index, file_path) for index, item in enumerate(items)]


def fetch_sample_news(settings: dict) -> tuple[list[dict], list[dict]]:
    """国内ニュースと海外ニュースのサンプルデータを読み込む。"""
    news_limit = settings["news_limit"]
    domestic_news = load_news_items(settings["news_jp_path"])[:news_limit]
    global_news = load_news_items(settings["news_global_path"])[:news_limit]
    return domestic_news, global_news
