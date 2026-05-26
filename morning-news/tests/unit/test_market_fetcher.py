from __future__ import annotations

import pytest

from src.market.fetcher import fetch_api_markets, load_market_items
from src.utils.exceptions import DataLoadError, DataValidationError


def test_load_market_items_returns_valid_items(tmp_path, write_json, sample_market_items):
    path = write_json(tmp_path / "market.json", {"items": sample_market_items})

    items = load_market_items(path)

    assert len(items) == 2
    assert items[0]["symbol"] == "NIKKEI225"


def test_load_market_items_raises_when_file_missing(tmp_path):
    with pytest.raises(DataLoadError):
        load_market_items(tmp_path / "missing.json")


def test_load_market_items_raises_when_json_is_invalid(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(DataLoadError):
        load_market_items(path)


def test_load_market_items_raises_when_items_is_not_list(tmp_path, write_json):
    path = write_json(tmp_path / "market.json", {"items": {}})

    with pytest.raises(DataValidationError):
        load_market_items(path)


def test_load_market_items_raises_when_required_field_is_missing(
    tmp_path,
    write_json,
    sample_market_items,
):
    del sample_market_items[0]["symbol"]
    path = write_json(tmp_path / "market.json", {"items": sample_market_items})

    with pytest.raises(DataValidationError, match="symbol"):
        load_market_items(path)


def test_fetch_api_markets_uses_sample_provider(sample_settings):
    settings = sample_settings.__class__(
        **{**sample_settings.__dict__, "app_mode": "api", "market_provider": "sample"}
    )

    items, warnings = fetch_api_markets(settings)

    assert len(items) == 2
    assert "MARKET_PROVIDER=sample" in warnings[0]["message"]


def test_fetch_api_markets_returns_warning_for_unknown_provider(sample_settings):
    settings = sample_settings.__class__(
        **{**sample_settings.__dict__, "app_mode": "api", "market_provider": "unknown"}
    )

    items, warnings = fetch_api_markets(settings)

    assert items == []
    assert "未対応" in warnings[0]["message"]
