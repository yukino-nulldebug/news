from __future__ import annotations

import sys

import pytest
import requests

from src.utils.exceptions import ExternalDataError, ExternalFetchError
from src.utils.http_client import get_json, get_text, sanitize_text, sanitize_url


def test_sanitize_url_masks_secret_query_values():
    url = "https://example.com/api?symbol=SPY&apikey=test-secret-key&token=abc"

    assert sanitize_url(url) == "https://example.com/api?symbol=SPY&apikey=***&token=***"


def test_sanitize_text_masks_secret_assignments_and_authorization():
    text = "failed apikey=test-secret-key Authorization: Bearer abc123"

    sanitized = sanitize_text(text)

    assert "apikey=***" in sanitized
    assert "test-secret-key" not in sanitized
    assert "Authorization: ***" in sanitized


def test_get_text_returns_response_text(monkeypatch, FakeResponse):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse(text="ok"))

    assert get_text("https://example.com") == "ok"


def test_get_json_returns_response_json(monkeypatch, FakeResponse):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse(json_data={"ok": True}))

    assert get_json("https://example.com") == {"ok": True}


def test_get_json_raises_when_json_parse_fails(monkeypatch, FakeResponse):
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: FakeResponse(json_data=ValueError("broken")),
    )

    with pytest.raises(ExternalDataError):
        get_json("https://example.com")


def test_request_retries_retryable_status(monkeypatch, FakeResponse):
    responses = [FakeResponse(status_code=500), FakeResponse(text="ok")]

    def fake_get(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(requests, "get", fake_get)

    assert get_text("https://example.com", retry_count=1) == "ok"


def test_request_raises_on_404(monkeypatch, FakeResponse):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse(status_code=404))

    with pytest.raises(ExternalFetchError):
        get_text("https://example.com")


def test_request_raises_on_timeout(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(ExternalFetchError):
        get_text("https://example.com", retry_count=0)


def test_request_raises_when_requests_is_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "requests", None)

    with pytest.raises(ExternalFetchError):
        get_text("https://example.com")
