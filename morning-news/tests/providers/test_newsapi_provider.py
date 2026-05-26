from __future__ import annotations

from src.news.providers.newsapi import fetch_newsapi_news


def test_fetch_newsapi_news_returns_unimplemented_warning(api_settings):
    items, warnings = fetch_newsapi_news(api_settings, "domestic")

    assert items == []
    assert "未対応" in warnings[0]


def test_fetch_newsapi_news_does_not_depend_on_region(api_settings):
    items, warnings = fetch_newsapi_news(api_settings, "any-region")

    assert items == []
    assert "未対応" in warnings[0]
