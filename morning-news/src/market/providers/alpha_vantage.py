"""Alpha Vantageからマーケット情報を取得するProvider。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.utils.exceptions import ExternalDataError, ExternalFetchError
from src.utils.http_client import get_json

FEATURE_ID = "F-04"
PROCESS_NAME = "market.alpha_vantage"


def _format_fetched_at(fetched_at: datetime) -> str:
    return fetched_at.strftime("%Y-%m-%d %H:%M JST")


def _to_number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def _shorten(value: Any, limit: int = 180) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _api_error_message(data: Any) -> str | None:
    if not isinstance(data, dict):
        return "レスポンスのトップレベルがオブジェクトではありません"

    for key in ("Error Message", "Note", "Information"):
        if key in data:
            return _shorten(data[key])
    return None


def _safe_error_message(error: Exception, api_key: str) -> str:
    message = getattr(error, "message", str(error))
    if api_key:
        message = message.replace(api_key, "***")
    return message


def _normalize_quote_response(data: Any, target, fetched_at: datetime) -> dict:
    api_error = _api_error_message(data)
    if api_error:
        raise ExternalDataError(
            f"{target.name} のAPIレスポンスがエラーです: {api_error}",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
            recoverable=True,
        )

    quote = data.get("Global Quote")
    if not isinstance(quote, dict) or not quote:
        raise ExternalDataError(
            f"{target.name} のレスポンスに Global Quote がありません",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
            recoverable=True,
        )

    current_value = _to_number(quote.get("05. price"))
    previous_close = _to_number(quote.get("08. previous close"))
    change = _to_number(quote.get("09. change"))
    if previous_close is None and current_value is not None and change is not None:
        previous_close = current_value - change

    if current_value is None or previous_close is None:
        raise ExternalDataError(
            f"{target.name} の current_value または previous_close を取得できませんでした",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
            recoverable=True,
        )

    return {
        "symbol": target.symbol,
        "name": target.name,
        "current_value": current_value,
        "previous_close": previous_close,
        "unit": target.unit,
        "fetched_at": _format_fetched_at(fetched_at),
    }


def _normalize_fx_daily_response(data: Any, target, fetched_at: datetime) -> dict:
    api_error = _api_error_message(data)
    if api_error:
        raise ExternalDataError(
            f"{target.name} のAPIレスポンスがエラーです: {api_error}",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
            recoverable=True,
        )

    series = data.get("Time Series FX (Daily)") if isinstance(data, dict) else None
    if not isinstance(series, dict) or len(series) < 2:
        raise ExternalDataError(
            f"{target.name} の前日終値を算出できる為替時系列がありません",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
            recoverable=True,
        )

    dates = sorted(series.keys(), reverse=True)
    current_row = series.get(dates[0], {})
    previous_row = series.get(dates[1], {})
    current_value = _to_number(current_row.get("4. close"))
    previous_close = _to_number(previous_row.get("4. close"))
    if current_value is None or previous_close is None:
        raise ExternalDataError(
            f"{target.name} の current_value または previous_close を取得できませんでした",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
            recoverable=True,
        )

    return {
        "symbol": target.symbol,
        "name": target.name,
        "current_value": current_value,
        "previous_close": previous_close,
        "unit": target.unit,
        "fetched_at": _format_fetched_at(fetched_at),
    }


def _fetch_index_quote(target, settings, fetched_at: datetime) -> dict:
    data = get_json(
        settings.market_api_endpoint,
        params={
            "function": "GLOBAL_QUOTE",
            "symbol": target.provider_symbol,
            "apikey": settings.market_api_key,
        },
        timeout_seconds=settings.request_timeout_seconds,
        retry_count=settings.request_retry_count,
        feature_id=FEATURE_ID,
        process_name=PROCESS_NAME,
    )
    return _normalize_quote_response(data, target, fetched_at)


def _fetch_fx_quote(target, settings, fetched_at: datetime) -> dict:
    data = get_json(
        settings.market_api_endpoint,
        params={
            "function": "FX_DAILY",
            "from_symbol": target.base,
            "to_symbol": target.quote,
            "outputsize": "compact",
            "apikey": settings.market_api_key,
        },
        timeout_seconds=settings.request_timeout_seconds,
        retry_count=settings.request_retry_count,
        feature_id=FEATURE_ID,
        process_name=PROCESS_NAME,
    )
    return _normalize_fx_daily_response(data, target, fetched_at)


def _fetch_target(target, settings, fetched_at: datetime) -> dict:
    if target.kind == "index":
        if not target.provider_symbol:
            raise ExternalDataError(
                f"{target.name} のProviderシンボルが未設定のためスキップしました",
                feature_id=FEATURE_ID,
                process_name=PROCESS_NAME,
                recoverable=True,
            )
        return _fetch_index_quote(target, settings, fetched_at)

    if target.kind == "fx":
        if not target.base or not target.quote:
            raise ExternalDataError(
                f"{target.name} の通貨ペア設定が不足しているためスキップしました",
                feature_id=FEATURE_ID,
                process_name=PROCESS_NAME,
                recoverable=True,
            )
        return _fetch_fx_quote(target, settings, fetched_at)

    raise ExternalDataError(
        f"{target.name} のkind={target.kind} は未対応です",
        feature_id=FEATURE_ID,
        process_name=PROCESS_NAME,
        recoverable=True,
    )


def fetch_alpha_vantage_markets(settings) -> tuple[list[dict], list[str]]:
    """対象指標を順に取得し、MarketItem形式へ正規化する。"""
    if not settings.market_api_key:
        return [], ["MARKET_API_KEY が未設定のためマーケットAPI取得をスキップしました"]

    fetched_at = datetime.now(settings.timezone)
    items: list[dict] = []
    warnings: list[str] = []

    for target in settings.market_targets:
        try:
            items.append(_fetch_target(target, settings, fetched_at))
        except (ExternalFetchError, ExternalDataError) as error:
            warnings.append(
                f"{target.name} の外部取得に失敗しました: "
                f"{_safe_error_message(error, settings.market_api_key)}"
            )

    return items, warnings
