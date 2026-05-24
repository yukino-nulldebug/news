"""外部HTTP取得の共通処理。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from src.utils.exceptions import ExternalDataError, ExternalFetchError

USER_AGENT = "MorningNews/0.1"
SECRET_QUERY_KEYS = {"apikey", "api_key", "key", "token", "access_token"}


def _encode_query_items(query_items: list[tuple[str, str]]) -> str:
    return "&".join(
        f"{quote_plus(str(key))}={quote_plus(str(value), safe='*')}"
        for key, value in query_items
    )


def sanitize_url(url: str) -> str:
    """URL内のAPIキーやトークン値をマスクする。"""
    parsed = urlsplit(str(url))
    query_items = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        masked_value = "***" if key.lower() in SECRET_QUERY_KEYS else value
        query_items.append((key, masked_value))
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            _encode_query_items(query_items),
            parsed.fragment,
        )
    )


def _url_with_params(url: str, params: Mapping[str, Any] | None) -> str:
    if not params:
        return url

    parsed = urlsplit(str(url))
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    query_items.extend((key, str(value)) for key, value in params.items())
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(query_items, doseq=True),
            parsed.fragment,
        )
    )


def _is_retryable_status(status_code: int) -> bool:
    """一時的な失敗としてリトライするHTTPステータスを判定する。"""
    return status_code == 429 or 500 <= status_code <= 599


def _request(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    timeout_seconds: int = 10,
    retry_count: int = 1,
    headers: Mapping[str, str] | None = None,
    feature_id: str = "F-09",
    process_name: str = "utils.http_client",
):
    try:
        import requests
    except ImportError as error:
        raise ExternalFetchError(
            "requests が未インストールのため外部HTTP取得を実行できません。",
            feature_id=feature_id,
            process_name=process_name,
            recoverable=True,
        ) from error

    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)

    attempts = max(0, retry_count) + 1
    masked_url = sanitize_url(_url_with_params(url, params))
    last_error: Exception | None = None

    for attempt in range(attempts):
        try:
            response = requests.get(
                url,
                params=params,
                headers=request_headers,
                timeout=timeout_seconds,
            )
        except (requests.Timeout, requests.ConnectionError) as error:
            last_error = error
            if attempt + 1 < attempts:
                continue
            raise ExternalFetchError(
                f"外部取得に失敗しました: {masked_url}",
                feature_id=feature_id,
                process_name=process_name,
                recoverable=True,
            ) from error
        except requests.RequestException as error:
            request_url = getattr(getattr(error, "request", None), "url", masked_url)
            raise ExternalFetchError(
                f"外部取得に失敗しました: {sanitize_url(request_url)}",
                feature_id=feature_id,
                process_name=process_name,
                recoverable=True,
            ) from error

        status_code = response.status_code
        response_url = sanitize_url(getattr(response, "url", masked_url))
        if 200 <= status_code <= 299:
            return response

        if _is_retryable_status(status_code) and attempt + 1 < attempts:
            continue

        raise ExternalFetchError(
            f"外部取得に失敗しました: {response_url} (HTTP {status_code})",
            feature_id=feature_id,
            process_name=process_name,
            recoverable=True,
        )

    raise ExternalFetchError(
        f"外部取得に失敗しました: {masked_url}: {last_error}",
        feature_id=feature_id,
        process_name=process_name,
        recoverable=True,
    )


def get_text(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    timeout_seconds: int = 10,
    retry_count: int = 1,
    headers: Mapping[str, str] | None = None,
    feature_id: str = "F-09",
    process_name: str = "utils.http_client",
) -> str:
    """HTTP GETし、レスポンス本文を文字列で返す。"""
    response = _request(
        url,
        params=params,
        timeout_seconds=timeout_seconds,
        retry_count=retry_count,
        headers=headers,
        feature_id=feature_id,
        process_name=process_name,
    )
    return response.text


def get_json(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    timeout_seconds: int = 10,
    retry_count: int = 1,
    headers: Mapping[str, str] | None = None,
    feature_id: str = "F-09",
    process_name: str = "utils.http_client",
) -> Any:
    """HTTP GETし、JSONレスポンスを返す。"""
    response = _request(
        url,
        params=params,
        timeout_seconds=timeout_seconds,
        retry_count=retry_count,
        headers=headers,
        feature_id=feature_id,
        process_name=process_name,
    )
    try:
        return response.json()
    except ValueError as error:
        raise ExternalDataError(
            f"外部レスポンスのJSON解析に失敗しました: {sanitize_url(response.url)}",
            feature_id=feature_id,
            process_name=process_name,
            recoverable=True,
        ) from error
