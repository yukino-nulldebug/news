"""Morning News フェーズ1 のニュース概要文を整形する。"""

from __future__ import annotations

import re

NO_SUMMARY_TEXT = "概要はありません。"


def format_summary(summary: str, max_length: int) -> str:
    """概要文の空白を整え、指定文字数以内に丸める。"""
    if max_length <= 0:
        raise ValueError("max_length は1以上である必要があります。")

    normalized = re.sub(r"\s+", " ", str(summary or "")).strip()
    if not normalized:
        return NO_SUMMARY_TEXT

    if len(normalized) <= max_length:
        return normalized

    if max_length <= 3:
        return "." * max_length
    return normalized[: max_length - 3].rstrip() + "..."


def format_news_items(items: list[dict], max_length: int) -> list[dict]:
    """各ニュースに整形済み概要文の項目を追加する。"""
    formatted_items = []
    for item in items:
        formatted = dict(item)
        formatted["short_summary"] = format_summary(formatted.get("summary", ""), max_length)
        formatted_items.append(formatted)
    return formatted_items
