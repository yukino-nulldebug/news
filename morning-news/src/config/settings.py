"""Morning News の設定を管理する。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
REPORT_DIR = BASE_DIR / "reports"
LOG_DIR = BASE_DIR / "logs"
NEWS_LIMIT = 5
SUMMARY_MAX_LENGTH = 120
REQUEST_TIMEOUT_SECONDS = 10
REQUEST_RETRY_COUNT = 1
MARKET_REQUEST_INTERVAL_SECONDS = 0
MARKET_API_ENDPOINT = "https://www.alphavantage.co/query"
JST = ZoneInfo("Asia/Tokyo")
SUPPORTED_APP_MODES = {"sample", "api"}
SUPPORTED_NEWS_PROVIDERS = {"rss", "newsapi"}
MARKET_PROVIDER_ALIASES = {
    "alphavantage": "alpha_vantage",
    "alpha-vantage": "alpha_vantage",
}


@dataclass(frozen=True)
class MarketTarget:
    """マーケット取得対象の論理IDとProvider設定。"""

    symbol: str
    name: str
    kind: str
    unit: str = ""
    provider_symbol: str = ""
    base: str = ""
    quote: str = ""


@dataclass(frozen=True)
class Settings:
    """アプリ起動時に確定する設定値。"""

    app_mode: str
    base_dir: Path
    sample_data_dir: Path
    report_dir: Path
    log_dir: Path
    news_jp_path: Path
    news_global_path: Path
    market_path: Path
    news_provider: str
    news_jp_rss_urls: tuple[str, ...]
    news_global_rss_urls: tuple[str, ...]
    news_api_key: str
    news_api_endpoint: str
    market_provider: str
    market_api_key: str
    market_api_endpoint: str
    market_targets: tuple[MarketTarget, ...]
    news_limit: int
    summary_max_length: int
    request_timeout_seconds: int
    request_retry_count: int
    market_request_interval_seconds: int
    timezone: ZoneInfo
    target_date: date
    settings_warnings: tuple[str, ...]


def _load_dotenv() -> tuple[str, ...]:
    """`.env` があれば読み込む。OS環境変数を優先する。"""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return ()

    try:
        from dotenv import load_dotenv
    except ImportError:
        return ("python-dotenv が未インストールのため .env を読み込めませんでした",)

    load_dotenv(env_path, override=False)
    return ()


def _get_env(name: str, default: str = "") -> str:
    """環境変数を取得し、空文字は未設定として扱う。"""
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _get_first_env(names: tuple[str, ...], default: str = "") -> str:
    """複数の環境変数名から最初に設定されている値を返す。"""
    for name in names:
        value = _get_env(name)
        if value:
            return value
    return default


def _resolve_app_mode(raw_mode: str, warnings: list[str]) -> str:
    mode = (raw_mode or "sample").strip().lower()
    if mode in SUPPORTED_APP_MODES:
        return mode

    warnings.append(f"APP_MODE={raw_mode} は不正なため sample で実行します")
    return "sample"


def _resolve_news_provider(raw_provider: str, warnings: list[str]) -> str:
    provider = (raw_provider or "rss").strip().lower()
    if provider in SUPPORTED_NEWS_PROVIDERS:
        return provider

    warnings.append(f"NEWS_PROVIDER={raw_provider} は未対応のため rss で実行します")
    return "rss"


def _resolve_market_provider(raw_provider: str) -> str:
    provider = (raw_provider or "alpha_vantage").strip().lower()
    return MARKET_PROVIDER_ALIASES.get(provider, provider)


def _parse_int(
    name: str,
    default: int,
    min_value: int,
    warnings: list[str],
    *,
    fatal: bool = False,
) -> int:
    """整数環境変数を検証し、不正時は既定値または例外にする。"""
    from src.utils.exceptions import ConfigError

    raw_value = _get_env(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as error:
        if fatal:
            raise ConfigError(
                f"{name} は整数である必要があります。",
                feature_id="F-03",
                process_name="settings.load_settings",
            ) from error
        warnings.append(f"{name}={raw_value} は不正なため {default} を使用します")
        return default

    if value < min_value:
        if fatal:
            raise ConfigError(
                f"{name} は {min_value} 以上である必要があります。",
                feature_id="F-03",
                process_name="settings.load_settings",
            )
        warnings.append(f"{name}={raw_value} は不正なため {default} を使用します")
        return default

    return value


def _resolve_path(raw_path: str, default_path: Path) -> Path:
    if not raw_path:
        return default_path

    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return BASE_DIR / path


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_csv_urls(name: str, warnings: list[str]) -> tuple[str, ...]:
    """カンマ区切りURLを検証し、HTTP(S) URLだけ返す。"""
    raw_value = _get_env(name)
    if not raw_value:
        return ()

    urls = []
    for value in raw_value.split(","):
        url = value.strip()
        if not url:
            continue
        if not _is_http_url(url):
            warnings.append(f"{name} に不正なURLがあるため除外しました: {url}")
            continue
        urls.append(url)
    return tuple(urls)


def _build_market_targets() -> tuple[MarketTarget, ...]:
    market_symbol_nikkei225 = _get_env("MARKET_SYMBOL_NIKKEI225")
    market_symbol_sp500 = _get_env("MARKET_SYMBOL_SP500")
    market_fx_base = _get_env("MARKET_FX_BASE", "USD").upper()
    market_fx_quote = _get_env("MARKET_FX_QUOTE", "JPY").upper()

    return (
        MarketTarget(
            symbol="NIKKEI225",
            name="日本市場参考指標",
            kind="index",
            provider_symbol=market_symbol_nikkei225,
            unit="points",
        ),
        MarketTarget(
            symbol="SP500",
            name="米国市場参考指標",
            kind="index",
            provider_symbol=market_symbol_sp500,
            unit="points",
        ),
        MarketTarget(
            symbol="USDJPY",
            name="USD/JPY",
            kind="fx",
            base=market_fx_base,
            quote=market_fx_quote,
            unit="yen",
        ),
    )


def load_settings() -> Settings:
    """`.env`、環境変数、既定値から設定を作る。"""
    warnings = list(_load_dotenv())
    now = datetime.now(JST)
    app_mode = _resolve_app_mode(_get_env("APP_MODE", "sample"), warnings)
    news_provider = _resolve_news_provider(_get_env("NEWS_PROVIDER", "rss"), warnings)
    news_limit = _parse_int("NEWS_LIMIT", NEWS_LIMIT, 1, warnings)
    summary_max_length = _parse_int(
        "SUMMARY_MAX_LENGTH",
        SUMMARY_MAX_LENGTH,
        1,
        warnings,
        fatal=True,
    )
    request_timeout_seconds = _parse_int(
        "REQUEST_TIMEOUT_SECONDS",
        REQUEST_TIMEOUT_SECONDS,
        1,
        warnings,
    )
    request_retry_count = _parse_int(
        "REQUEST_RETRY_COUNT",
        REQUEST_RETRY_COUNT,
        0,
        warnings,
    )
    market_request_interval_seconds = _parse_int(
        "MARKET_REQUEST_INTERVAL_SECONDS",
        MARKET_REQUEST_INTERVAL_SECONDS,
        0,
        warnings,
    )
    common_rss_urls = _parse_csv_urls("NEWS_RSS_URLS", warnings)
    news_jp_rss_urls = _parse_csv_urls("NEWS_JP_RSS_URLS", warnings) or common_rss_urls
    news_global_rss_urls = _parse_csv_urls("NEWS_GLOBAL_RSS_URLS", warnings)

    return Settings(
        app_mode=app_mode,
        base_dir=BASE_DIR,
        sample_data_dir=SAMPLE_DATA_DIR,
        report_dir=_resolve_path(_get_env("REPORT_DIR"), REPORT_DIR),
        log_dir=_resolve_path(_get_env("LOG_DIR"), LOG_DIR),
        news_jp_path=SAMPLE_DATA_DIR / "news_jp.json",
        news_global_path=SAMPLE_DATA_DIR / "news_global.json",
        market_path=SAMPLE_DATA_DIR / "market.json",
        news_provider=news_provider,
        news_jp_rss_urls=news_jp_rss_urls,
        news_global_rss_urls=news_global_rss_urls,
        news_api_key=_get_env("NEWS_API_KEY"),
        news_api_endpoint=_get_env("NEWS_API_ENDPOINT"),
        market_provider=_resolve_market_provider(_get_env("MARKET_PROVIDER", "alpha_vantage")),
        market_api_key=_get_first_env(("MARKET_API_KEY", "ALPHA_VANTAGE_API_KEY")),
        market_api_endpoint=_get_first_env(
            ("MARKET_API_ENDPOINT", "ALPHA_VANTAGE_API_ENDPOINT"),
            MARKET_API_ENDPOINT,
        ),
        market_targets=_build_market_targets(),
        news_limit=news_limit,
        summary_max_length=summary_max_length,
        request_timeout_seconds=request_timeout_seconds,
        request_retry_count=request_retry_count,
        market_request_interval_seconds=market_request_interval_seconds,
        timezone=JST,
        target_date=now.date(),
        settings_warnings=tuple(warnings),
    )
