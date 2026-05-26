from __future__ import annotations

import pytest

from src.news.formatter import NO_SUMMARY_TEXT, format_news_items, format_summary
from src.utils.exceptions import SummaryFormatError


def test_format_summary_normalizes_repeated_whitespace():
    summary = "国内市場では\n為替動向や    企業決算を確認している。"

    assert format_summary(summary, 120) == "国内市場では 為替動向や 企業決算を確認している。"


def test_format_summary_uses_fallback_when_empty():
    assert format_summary("   ", 120) == NO_SUMMARY_TEXT


def test_format_summary_truncates_text_with_ellipsis():
    assert format_summary("abcdef", 5) == "ab..."


def test_format_summary_returns_dots_when_limit_is_less_than_three():
    assert format_summary("abcdef", 2) == ".."


def test_format_summary_raises_when_max_length_is_zero():
    with pytest.raises(SummaryFormatError):
        format_summary("abcdef", 0)


def test_format_news_items_adds_short_summary_without_mutating_source():
    source = [{"title": "t", "summary": "hello   world"}]

    formatted = format_news_items(source, 120)

    assert formatted[0]["short_summary"] == "hello world"
    assert "short_summary" not in source[0]
