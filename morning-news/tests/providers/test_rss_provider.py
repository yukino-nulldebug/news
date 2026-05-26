from __future__ import annotations

import builtins

from src.news.providers import rss as rss_module
from src.utils.exceptions import ExternalFetchError


def test_fetch_rss_news_returns_warning_when_urls_are_empty(api_settings):
    items, warnings = rss_module.fetch_rss_news((), "domestic", 5, api_settings)

    assert items == []
    assert "NEWS_JP_RSS_URLS" in warnings[0]


def test_fetch_rss_news_returns_warning_when_feedparser_is_missing(monkeypatch, api_settings):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "feedparser":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    items, warnings = rss_module.fetch_rss_news(("https://example.com/rss.xml",), "domestic", 5, api_settings)

    assert items == []
    assert "feedparser" in warnings[0]


def test_fetch_rss_news_normalizes_items_and_cleans_html(monkeypatch, api_settings, fixed_rss_xml):
    monkeypatch.setattr(rss_module, "get_text", lambda *args, **kwargs: fixed_rss_xml)

    items, warnings = rss_module.fetch_rss_news(("https://example.com/rss.xml",), "domestic", 5, api_settings)

    assert len(items) == 2
    assert items[0]["region"] == "domestic"
    assert items[0]["source"] == "Sample Feed"
    assert "<" not in items[0]["summary"]
    assert any("公開日時が欠損" in warning for warning in warnings)


def test_fetch_rss_news_skips_entry_when_title_or_url_is_missing(monkeypatch, api_settings):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Sample</title><item><link>https://example.com/no-title</link></item></channel></rss>
"""
    monkeypatch.setattr(rss_module, "get_text", lambda *args, **kwargs: xml)

    items, warnings = rss_module.fetch_rss_news(("https://example.com/rss.xml",), "domestic", 5, api_settings)

    assert items == []
    assert any("title または url" in warning for warning in warnings)


def test_fetch_rss_news_deduplicates_tracking_query_urls(monkeypatch, api_settings):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Sample</title>
<item><title>A</title><link>https://example.com/a?utm_source=x</link><description>A</description></item>
<item><title>A duplicate</title><link>https://example.com/a?utm_source=y</link><description>A</description></item>
</channel></rss>
"""
    monkeypatch.setattr(rss_module, "get_text", lambda *args, **kwargs: xml)

    items, _warnings = rss_module.fetch_rss_news(("https://example.com/rss.xml",), "domestic", 5, api_settings)

    assert len(items) == 1


def test_fetch_rss_news_returns_warning_when_http_fails(monkeypatch, api_settings):
    def raise_fetch_error(*args, **kwargs):
        raise ExternalFetchError(
            "failed apikey=test-secret-key",
            feature_id="F-01",
            process_name="news.rss",
        )

    monkeypatch.setattr(rss_module, "get_text", raise_fetch_error)

    items, warnings = rss_module.fetch_rss_news(
        ("https://example.com/rss.xml?apikey=test-secret-key",),
        "domestic",
        5,
        api_settings,
    )

    assert items == []
    assert "apikey=***" in warnings[0]


def test_fetch_rss_news_applies_limit(monkeypatch, api_settings, fixed_rss_xml):
    monkeypatch.setattr(rss_module, "get_text", lambda *args, **kwargs: fixed_rss_xml)

    items, _warnings = rss_module.fetch_rss_news(("https://example.com/rss.xml",), "domestic", 1, api_settings)

    assert len(items) == 1
