from __future__ import annotations

from datetime import datetime

import pytest

from src.config.settings import MarketTarget
from src.market.providers import alpha_vantage as alpha_module
from src.utils.exceptions import ExternalDataError


def test_fetch_alpha_vantage_markets_returns_warning_when_api_key_is_missing(sample_settings):
    items, warnings = alpha_module.fetch_alpha_vantage_markets(sample_settings)

    assert items == []
    assert "MARKET_API_KEY" in warnings[0]


def test_normalize_quote_response_returns_market_item(api_settings):
    target = api_settings.market_targets[0]
    data = {
        "Global Quote": {
            "05. price": "105.5",
            "08. previous close": "100.0",
        }
    }

    item = alpha_module._normalize_quote_response(data, target, datetime(2026, 5, 26, 7, 0))

    assert item["symbol"] == "SP500"
    assert item["current_value"] == 105.5
    assert item["previous_close"] == 100.0


def test_normalize_quote_response_fills_previous_close_from_change(api_settings):
    target = api_settings.market_targets[0]
    data = {
        "Global Quote": {
            "05. price": "105.5",
            "09. change": "5.5",
        }
    }

    item = alpha_module._normalize_quote_response(data, target, datetime(2026, 5, 26, 7, 0))

    assert item["previous_close"] == 100.0


def test_normalize_quote_response_raises_on_api_note(api_settings):
    target = api_settings.market_targets[0]

    with pytest.raises(ExternalDataError):
        alpha_module._normalize_quote_response({"Note": "API limit"}, target, datetime(2026, 5, 26, 7, 0))


def test_normalize_fx_daily_response_uses_two_latest_days(api_settings):
    target = api_settings.market_targets[1]
    data = {
        "Time Series FX (Daily)": {
            "2026-05-26": {"4. close": "155.5"},
            "2026-05-25": {"4. close": "154.5"},
        }
    }

    item = alpha_module._normalize_fx_daily_response(data, target, datetime(2026, 5, 26, 7, 0))

    assert item["symbol"] == "USDJPY"
    assert item["current_value"] == 155.5
    assert item["previous_close"] == 154.5


def test_normalize_fx_daily_response_raises_when_only_one_day(api_settings):
    target = api_settings.market_targets[1]

    with pytest.raises(ExternalDataError):
        alpha_module._normalize_fx_daily_response(
            {"Time Series FX (Daily)": {"2026-05-26": {"4. close": "155.5"}}},
            target,
            datetime(2026, 5, 26, 7, 0),
        )


def test_fetch_target_raises_recoverable_when_provider_symbol_is_missing(api_settings):
    target = MarketTarget(symbol="NIKKEI225", name="日経平均", kind="index")

    with pytest.raises(ExternalDataError) as exc_info:
        alpha_module._fetch_target(target, api_settings, datetime(2026, 5, 26, 7, 0))

    assert exc_info.value.recoverable is True


def test_fetch_alpha_vantage_markets_keeps_successes_and_masks_key(monkeypatch, api_settings):
    def fake_get_json(url, *, params, **kwargs):
        if params["function"] == "GLOBAL_QUOTE":
            return {"Global Quote": {"05. price": "105.0", "08. previous close": "100.0"}}
        raise ExternalDataError(
            "failed apikey=test-secret-key",
            feature_id="F-04",
            process_name="market.alpha_vantage",
            recoverable=True,
        )

    monkeypatch.setattr(alpha_module, "get_json", fake_get_json)

    items, warnings = alpha_module.fetch_alpha_vantage_markets(api_settings)

    assert len(items) == 1
    assert warnings
    assert "test-secret-key" not in warnings[0]
    assert "apikey=***" in warnings[0]
