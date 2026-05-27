from __future__ import annotations

import pytest

from src.config import settings as settings_module
from src.utils.exceptions import ConfigError


@pytest.fixture
def patched_settings_dirs(monkeypatch, tmp_path):
    monkeypatch.setattr(settings_module, "BASE_DIR", tmp_path)
    monkeypatch.setattr(settings_module, "SAMPLE_DATA_DIR", tmp_path / "sample_data")
    monkeypatch.setattr(settings_module, "REPORT_DIR", tmp_path / "reports")
    monkeypatch.setattr(settings_module, "LOG_DIR", tmp_path / "logs")
    return tmp_path


def test_load_settings_uses_sample_defaults(patched_settings_dirs):
    loaded = settings_module.load_settings()

    assert loaded.app_mode == "sample"
    assert loaded.news_provider == "rss"
    assert loaded.news_limit == 5
    assert loaded.summary_max_length == 120
    assert loaded.request_timeout_seconds == 10
    assert loaded.request_retry_count == 1
    assert loaded.market_request_interval_seconds == 0
    assert loaded.report_dir == patched_settings_dirs / "reports"


def test_load_settings_falls_back_when_app_mode_is_invalid(monkeypatch, patched_settings_dirs):
    monkeypatch.setenv("APP_MODE", "bad")

    loaded = settings_module.load_settings()

    assert loaded.app_mode == "sample"
    assert any("APP_MODE=bad" in warning for warning in loaded.settings_warnings)


def test_load_settings_falls_back_when_news_limit_is_invalid(monkeypatch, patched_settings_dirs):
    monkeypatch.setenv("NEWS_LIMIT", "abc")

    loaded = settings_module.load_settings()

    assert loaded.news_limit == 5
    assert any("NEWS_LIMIT=abc" in warning for warning in loaded.settings_warnings)


def test_load_settings_raises_when_summary_max_length_is_invalid(
    monkeypatch,
    patched_settings_dirs,
):
    monkeypatch.setenv("SUMMARY_MAX_LENGTH", "0")

    with pytest.raises(ConfigError):
        settings_module.load_settings()


def test_load_settings_excludes_invalid_rss_urls(monkeypatch, patched_settings_dirs):
    monkeypatch.setenv("NEWS_RSS_URLS", "https://example.com/rss,not-url")

    loaded = settings_module.load_settings()

    assert loaded.news_jp_rss_urls == ("https://example.com/rss",)
    assert any("不正なURL" in warning for warning in loaded.settings_warnings)


def test_load_settings_resolves_market_provider_alias(monkeypatch, patched_settings_dirs):
    monkeypatch.setenv("MARKET_PROVIDER", "alphavantage")

    loaded = settings_module.load_settings()

    assert loaded.market_provider == "alpha_vantage"


def test_load_settings_reads_market_request_interval_seconds(monkeypatch, patched_settings_dirs):
    monkeypatch.setenv("MARKET_REQUEST_INTERVAL_SECONDS", "2")

    loaded = settings_module.load_settings()

    assert loaded.market_request_interval_seconds == 2


def test_load_settings_uses_reference_market_target_names(patched_settings_dirs):
    loaded = settings_module.load_settings()

    assert loaded.market_targets[0].name == "日本市場参考指標"
    assert loaded.market_targets[1].name == "米国市場参考指標"
