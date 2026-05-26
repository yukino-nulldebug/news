from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import JST, MarketTarget, Settings


APP_ENV_NAMES = (
    "APP_MODE",
    "NEWS_PROVIDER",
    "NEWS_RSS_URLS",
    "NEWS_JP_RSS_URLS",
    "NEWS_GLOBAL_RSS_URLS",
    "NEWS_API_KEY",
    "NEWS_API_ENDPOINT",
    "NEWS_LIMIT",
    "SUMMARY_MAX_LENGTH",
    "MARKET_PROVIDER",
    "MARKET_API_KEY",
    "ALPHA_VANTAGE_API_KEY",
    "MARKET_API_ENDPOINT",
    "ALPHA_VANTAGE_API_ENDPOINT",
    "MARKET_SYMBOL_NIKKEI225",
    "MARKET_SYMBOL_SP500",
    "MARKET_FX_BASE",
    "MARKET_FX_QUOTE",
    "REPORT_DIR",
    "LOG_DIR",
    "REQUEST_TIMEOUT_SECONDS",
    "REQUEST_RETRY_COUNT",
)


@pytest.fixture(autouse=True)
def clean_app_env(monkeypatch):
    for name in APP_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def write_json():
    def _write_json(path: Path, data: dict) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    return _write_json


@pytest.fixture
def sample_news_items():
    return [
        {
            "region": "domestic",
            "category": "economy",
            "title": "国内ニュース",
            "url": "https://example.com/domestic",
            "source": "Sample JP",
            "published_at": "2026-05-26T07:00:00+09:00",
            "summary": "国内市場のサンプル概要です。",
        },
        {
            "region": "domestic",
            "category": "market",
            "title": "国内ニュース2",
            "url": "https://example.com/domestic-2",
            "source": "Sample JP",
            "published_at": "2026-05-26T07:10:00+09:00",
            "summary": "",
        },
    ]


@pytest.fixture
def sample_global_news_items():
    return [
        {
            "region": "global",
            "category": "market",
            "title": "Global news",
            "url": "https://example.com/global",
            "source": "Sample Global",
            "published_at": "2026-05-26T07:00:00+09:00",
            "summary": "Global market sample summary.",
        }
    ]


@pytest.fixture
def sample_market_items():
    return [
        {
            "symbol": "NIKKEI225",
            "name": "日経平均",
            "current_value": 105.0,
            "previous_close": 100.0,
            "unit": "points",
            "fetched_at": "2026-05-26T07:00:00+09:00",
        },
        {
            "symbol": "USDJPY",
            "name": "USD/JPY",
            "current_value": 155.0,
            "previous_close": 154.0,
            "unit": "yen",
            "fetched_at": "2026-05-26T07:00:00+09:00",
        },
    ]


def make_settings(
    tmp_path: Path,
    *,
    app_mode: str = "sample",
    news_provider: str = "rss",
    market_provider: str = "alpha_vantage",
    market_api_key: str = "",
    news_jp_rss_urls: tuple[str, ...] = (),
    news_global_rss_urls: tuple[str, ...] = (),
    market_targets: tuple[MarketTarget, ...] | None = None,
) -> Settings:
    sample_data_dir = tmp_path / "sample_data"
    return Settings(
        app_mode=app_mode,
        base_dir=tmp_path,
        sample_data_dir=sample_data_dir,
        report_dir=tmp_path / "reports",
        log_dir=tmp_path / "logs",
        news_jp_path=sample_data_dir / "news_jp.json",
        news_global_path=sample_data_dir / "news_global.json",
        market_path=sample_data_dir / "market.json",
        news_provider=news_provider,
        news_jp_rss_urls=news_jp_rss_urls,
        news_global_rss_urls=news_global_rss_urls,
        news_api_key="",
        news_api_endpoint="",
        market_provider=market_provider,
        market_api_key=market_api_key,
        market_api_endpoint="https://example.com/query",
        market_targets=market_targets
        if market_targets is not None
        else (
            MarketTarget(
                symbol="SP500",
                name="S&P500",
                kind="index",
                provider_symbol="SPY",
                unit="points",
            ),
            MarketTarget(
                symbol="USDJPY",
                name="USD/JPY",
                kind="fx",
                base="USD",
                quote="JPY",
                unit="yen",
            ),
        ),
        news_limit=5,
        summary_max_length=120,
        request_timeout_seconds=10,
        request_retry_count=1,
        timezone=JST,
        target_date=date(2026, 5, 26),
        settings_warnings=(),
    )


@pytest.fixture
def sample_settings(tmp_path, write_json, sample_news_items, sample_global_news_items, sample_market_items):
    settings = make_settings(tmp_path)
    write_json(settings.news_jp_path, {"items": sample_news_items})
    write_json(settings.news_global_path, {"items": sample_global_news_items})
    write_json(settings.market_path, {"items": sample_market_items})
    return settings


@pytest.fixture
def api_settings(tmp_path):
    return make_settings(
        tmp_path,
        app_mode="api",
        news_jp_rss_urls=("https://example.com/jp.xml",),
        news_global_rss_urls=("https://example.com/global.xml",),
        market_api_key="test-secret-key",
    )


@pytest.fixture
def fixed_rss_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample Feed</title>
    <item>
      <title>RSS title 1</title>
      <link>https://example.com/rss-1?utm_source=test</link>
      <description><![CDATA[<p>RSS <strong>summary</strong> 1</p>]]></description>
      <pubDate>Tue, 26 May 2026 00:00:00 GMT</pubDate>
    </item>
    <item>
      <title>RSS title 2</title>
      <link>https://example.com/rss-2</link>
      <description>RSS summary 2</description>
    </item>
  </channel>
</rss>
"""


class FakeResponse:
    def __init__(self, *, status_code=200, text="", json_data=None, url="https://example.com/api"):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        self.url = url

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data


@pytest.fixture(name="FakeResponse")
def fake_response_fixture():
    return FakeResponse
