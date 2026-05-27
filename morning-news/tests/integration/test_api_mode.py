from __future__ import annotations

import main as main_module


def _api_news():
    return [
        {
            "region": "domestic",
            "category": "general",
            "title": "API domestic",
            "url": "https://example.com/api-domestic",
            "source": "API",
            "published_at": "2026-05-26 07:00 JST",
            "summary": "API domestic summary",
        }
    ]


def _api_market():
    return [
        {
            "symbol": "SP500",
            "name": "S&P500",
            "current_value": 105.0,
            "previous_close": 100.0,
            "unit": "points",
            "fetched_at": "2026-05-26 07:00 JST",
        }
    ]


def test_main_api_mode_generates_report_with_mock_external_data(monkeypatch, api_settings):
    monkeypatch.setattr(main_module, "load_settings", lambda: api_settings)
    monkeypatch.setattr(
        main_module,
        "fetch_news_for_mode",
        lambda settings: (_api_news(), [], []),
    )
    monkeypatch.setattr(
        main_module,
        "fetch_markets_for_mode",
        lambda settings: (_api_market(), []),
    )

    exit_code = main_module.main()

    assert exit_code == 0
    assert (api_settings.report_dir / "2026-05-26.md").exists()


def test_main_api_mode_succeeds_when_only_news_exists(monkeypatch, api_settings):
    monkeypatch.setattr(main_module, "load_settings", lambda: api_settings)
    monkeypatch.setattr(
        main_module,
        "fetch_news_for_mode",
        lambda settings: (_api_news(), [], []),
    )
    monkeypatch.setattr(
        main_module,
        "fetch_markets_for_mode",
        lambda settings: ([], [{"feature_id": "F-04", "process_name": "market", "message": "MARKET_API_KEY 未設定"}]),
    )

    assert main_module.main() == 0


def test_main_api_mode_continues_when_market_calculation_is_incomplete(monkeypatch, api_settings):
    incomplete_market = [
        {
            "symbol": "SP500",
            "name": "S&P500",
            "current_value": 105.0,
            "unit": "points",
            "fetched_at": "2026-05-26 07:00 JST",
        }
    ]
    monkeypatch.setattr(main_module, "load_settings", lambda: api_settings)
    monkeypatch.setattr(main_module, "fetch_news_for_mode", lambda settings: ([], [], []))
    monkeypatch.setattr(main_module, "fetch_markets_for_mode", lambda settings: (incomplete_market, []))

    assert main_module.main() == 0

    report_text = (api_settings.report_dir / "2026-05-26.md").read_text(encoding="utf-8")
    log_text = (api_settings.log_dir / "app.log").read_text(encoding="utf-8")
    assert "N/A" in report_text
    assert "previous_close が欠損" in report_text
    assert "WARNING F-05" in log_text


def test_main_api_mode_returns_2_when_market_has_no_usable_value(monkeypatch, api_settings):
    unusable_market = [
        {
            "symbol": "SP500",
            "name": "S&P500",
            "unit": "points",
            "fetched_at": "2026-05-26 07:00 JST",
        }
    ]
    monkeypatch.setattr(main_module, "load_settings", lambda: api_settings)
    monkeypatch.setattr(main_module, "fetch_news_for_mode", lambda settings: ([], [], []))
    monkeypatch.setattr(main_module, "fetch_markets_for_mode", lambda settings: (unusable_market, []))

    assert main_module.main() == 2
    assert not (api_settings.report_dir / "2026-05-26.md").exists()


def test_main_api_mode_returns_2_when_all_external_data_is_empty(monkeypatch, api_settings):
    monkeypatch.setattr(main_module, "load_settings", lambda: api_settings)
    monkeypatch.setattr(main_module, "fetch_news_for_mode", lambda settings: ([], [], []))
    monkeypatch.setattr(main_module, "fetch_markets_for_mode", lambda settings: ([], []))

    exit_code = main_module.main()

    assert exit_code == 2
    assert not (api_settings.report_dir / "2026-05-26.md").exists()


def test_main_api_mode_masks_secret_values_in_logs(monkeypatch, api_settings):
    monkeypatch.setattr(main_module, "load_settings", lambda: api_settings)
    monkeypatch.setattr(
        main_module,
        "fetch_news_for_mode",
        lambda settings: (_api_news(), [], [{"feature_id": "F-01", "process_name": "news.rss", "message": "failed apikey=test-secret-key"}]),
    )
    monkeypatch.setattr(main_module, "fetch_markets_for_mode", lambda settings: (_api_market(), []))

    assert main_module.main() == 0

    log_text = (api_settings.log_dir / "app.log").read_text(encoding="utf-8")
    report_text = (api_settings.report_dir / "2026-05-26.md").read_text(encoding="utf-8")
    assert "test-secret-key" not in log_text
    assert "test-secret-key" not in report_text
    assert "apikey=***" in log_text
    assert "apikey=***" in report_text
