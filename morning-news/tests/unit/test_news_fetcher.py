from __future__ import annotations

import pytest

from src.news.fetcher import fetch_sample_news, load_news_items
from src.utils.exceptions import DataLoadError, DataValidationError


def test_load_news_items_returns_valid_items(tmp_path, write_json, sample_news_items):
    path = write_json(tmp_path / "news.json", {"items": sample_news_items})

    items = load_news_items(path, "F-01")

    assert len(items) == 2
    assert items[0]["title"] == "国内ニュース"
    assert items[1]["summary"] == ""


def test_load_news_items_raises_when_file_missing(tmp_path):
    with pytest.raises(DataLoadError):
        load_news_items(tmp_path / "missing.json", "F-01")


def test_load_news_items_raises_when_json_is_invalid(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(DataLoadError):
        load_news_items(path, "F-01")


def test_load_news_items_raises_when_items_is_not_list(tmp_path, write_json):
    path = write_json(tmp_path / "news.json", {"items": {}})

    with pytest.raises(DataValidationError):
        load_news_items(path, "F-01")


def test_load_news_items_raises_when_required_field_is_missing(
    tmp_path,
    write_json,
    sample_news_items,
):
    del sample_news_items[0]["title"]
    path = write_json(tmp_path / "news.json", {"items": sample_news_items})

    with pytest.raises(DataValidationError, match="title"):
        load_news_items(path, "F-01")


def test_load_news_items_raises_when_region_is_invalid(tmp_path, write_json, sample_news_items):
    sample_news_items[0]["region"] = "local"
    path = write_json(tmp_path / "news.json", {"items": sample_news_items})

    with pytest.raises(DataValidationError):
        load_news_items(path, "F-01")


def test_fetch_sample_news_applies_news_limit(sample_settings):
    limited_settings = sample_settings.__class__(
        **{**sample_settings.__dict__, "news_limit": 1}
    )

    domestic, global_news = fetch_sample_news(limited_settings)

    assert len(domestic) == 1
    assert len(global_news) == 1
