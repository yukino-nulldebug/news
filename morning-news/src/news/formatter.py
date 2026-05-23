"""Morning News のニュース概要文を整形する。"""

from __future__ import annotations

import re

from src.utils.exceptions import SummaryFormatError

NO_SUMMARY_TEXT = "概要はありません。"
PROCESS_NAME = "news.formatter"


def format_summary(summary: str, max_length: int) -> str:
    """概要文の空白を整え、指定文字数以内に丸める。"""
    if max_length <= 0:
        raise SummaryFormatError(
            "max_length は1以上である必要があります。",
            feature_id="F-03",
            process_name=PROCESS_NAME,
        )

    normalized = re.sub(r"\s+", " ", str(summary or "")).strip()
    if not normalized:
        return NO_SUMMARY_TEXT

    if len(normalized) <= max_length:
        return normalized

    if max_length < 3:
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
