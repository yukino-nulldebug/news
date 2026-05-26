from __future__ import annotations

from src.market.providers import alpha_vantage as alpha_module
from src.report.generator import DISCLAIMER, generate_report
from src.utils.exceptions import ExternalDataError
from src.utils.http_client import sanitize_text, sanitize_url


def test_sanitize_url_masks_api_key_and_token():
    url = "https://example.com/api?apikey=test-secret-key&token=test-secret-key&symbol=SPY"

    sanitized = sanitize_url(url)

    assert "test-secret-key" not in sanitized
    assert "apikey=***" in sanitized
    assert "token=***" in sanitized
    assert "symbol=SPY" in sanitized


def test_sanitize_text_masks_authorization_header():
    sanitized = sanitize_text("Authorization: Bearer test-secret-key")

    assert sanitized == "Authorization: ***"


def test_alpha_vantage_warning_masks_api_key(monkeypatch, api_settings):
    def fake_get_json(*args, **kwargs):
        raise ExternalDataError(
            "upstream failed apikey=test-secret-key",
            feature_id="F-04",
            process_name="market.alpha_vantage",
            recoverable=True,
        )

    monkeypatch.setattr(alpha_module, "get_json", fake_get_json)

    _items, warnings = alpha_module.fetch_alpha_vantage_markets(api_settings)

    assert warnings
    assert "test-secret-key" not in "\n".join(warnings)
    assert "apikey=***" in "\n".join(warnings)


def test_generate_report_masks_secret_values_in_warnings():
    markdown = generate_report(
        {
            "generated_at": "2026-05-26 07:00 JST",
            "mode": "api",
            "news_domestic": [],
            "news_global": [],
            "markets": [],
            "comments": [],
            "warnings": ["failed token=test-secret-key"],
            "errors": [],
            "disclaimer": DISCLAIMER,
            "execution_summary": {"status": "warning"},
        }
    )

    assert "test-secret-key" not in markdown
    assert "token=***" in markdown
