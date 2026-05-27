from __future__ import annotations

import pytest

from src.market.calculator import calculate_market_changes
from src.news.formatter import format_news_items
from src.report.generator import (
    DISCLAIMER,
    MARKET_COMMENT_DISCLAIMER,
    generate_market_comments,
    generate_report,
)
from src.utils.exceptions import ReportGenerationError


def _report_data(sample_news_items, sample_global_news_items, sample_market_items):
    markets = calculate_market_changes(sample_market_items)
    return {
        "generated_at": "2026-05-26 07:00 JST",
        "mode": "sample",
        "news_domestic": format_news_items(sample_news_items, 120),
        "news_global": format_news_items(sample_global_news_items, 120),
        "markets": markets,
        "comments": generate_market_comments(markets),
        "warnings": [],
        "errors": [],
        "disclaimer": DISCLAIMER,
        "execution_summary": {"status": "success"},
    }


def test_generate_report_contains_required_sections(
    sample_news_items,
    sample_global_news_items,
    sample_market_items,
):
    markdown = generate_report(_report_data(sample_news_items, sample_global_news_items, sample_market_items))

    assert "# Morning News Report" in markdown
    assert "## 1. 今日の注目ポイント" in markdown
    assert "## 2. 国内ニュース" in markdown
    assert "## 3. 海外ニュース" in markdown
    assert "## 4. マーケット情報" in markdown
    assert "## 5. 市況コメント" in markdown
    assert MARKET_COMMENT_DISCLAIMER in markdown
    assert DISCLAIMER in markdown


def test_generate_market_comments_uses_neutral_phrasing(sample_market_items):
    comments = generate_market_comments(calculate_market_changes(sample_market_items))

    joined = "\n".join(comments)
    assert "買うべき" not in joined
    assert "売るべき" not in joined
    assert "上昇傾向" in joined


def test_generate_report_masks_secret_query_values(
    sample_news_items,
    sample_global_news_items,
    sample_market_items,
):
    data = _report_data(sample_news_items, sample_global_news_items, sample_market_items)
    data["warnings"] = ["failed url=https://example.com/api?apikey=test-secret-key&symbol=SPY"]

    markdown = generate_report(data)

    assert "apikey=***" in markdown
    assert "test-secret-key" not in markdown


def test_generate_report_raises_when_required_key_is_missing(
    sample_news_items,
    sample_global_news_items,
    sample_market_items,
):
    data = _report_data(sample_news_items, sample_global_news_items, sample_market_items)
    del data["generated_at"]

    with pytest.raises(ReportGenerationError):
        generate_report(data)
