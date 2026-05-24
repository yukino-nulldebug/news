"""RSS/Atomフィードからニュースを取得するProvider。"""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from src.utils.exceptions import ExternalDataError, ExternalFetchError
from src.utils.http_client import get_text, sanitize_url

PROCESS_NAME = "news.rss"
TRACKING_QUERY_KEYS = {"fbclid", "gclid"}


def _get_value(obj: Any, key: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _clean_text(value: Any) -> str:
    return _normalize_space(html.unescape(str(value or "")))


def _clean_summary(value: Any) -> str:
    decoded = html.unescape(str(value or ""))
    without_tags = re.sub(r"<[^>]+>", " ", decoded)
    return _normalize_space(without_tags)


def _format_jst(value: datetime, settings) -> str:
    return value.astimezone(settings.timezone).strftime("%Y-%m-%d %H:%M JST")


def _parse_entry_datetime(entry: Any, fetched_at: datetime, settings) -> tuple[str, str | None]:
    parsed_time = _get_value(entry, "published_parsed") or _get_value(entry, "updated_parsed")
    title = _clean_text(_get_value(entry, "title")) or "タイトル不明"

    if parsed_time:
        try:
            parsed_tuple = tuple(parsed_time)[:6]
            published_at = datetime(*parsed_tuple, tzinfo=timezone.utc)
            return _format_jst(published_at, settings), None
        except (TypeError, ValueError) as error:
            return (
                _format_jst(fetched_at, settings),
                f"{title} の公開日時を解析できないため取得日時を使用しました: {error}",
            )

    return (
        _format_jst(fetched_at, settings),
        f"{title} の公開日時が欠損しているため取得日時を使用しました",
    )


def _source_from_feed(feed: Any, source_url: str) -> str:
    feed_title = _clean_text(_get_value(feed, "title"))
    if feed_title:
        return feed_title

    host = urlsplit(source_url).netloc
    return host or "unknown"


def _canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    query_items = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        lowered_key = key.lower()
        if lowered_key.startswith("utm_") or lowered_key in TRACKING_QUERY_KEYS:
            continue
        query_items.append((key, value))
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(query_items, doseq=True),
            "",
        )
    )


def _deduplicate_news(items: list[dict]) -> list[dict]:
    seen_urls = set()
    deduplicated = []
    for item in items:
        canonical_url = _canonical_url(item["url"])
        if canonical_url in seen_urls:
            continue
        seen_urls.add(canonical_url)
        deduplicated.append(item)
    return deduplicated


def _normalize_rss_entry(
    entry: Any,
    feed: Any,
    *,
    region: str,
    source_url: str,
    fetched_at: datetime,
    settings,
) -> tuple[dict | None, list[str]]:
    warnings = []
    title = _clean_text(_get_value(entry, "title"))
    url = _normalize_space(_get_value(entry, "link"))

    if not title or not url:
        warnings.append(f"{sanitize_url(source_url)} のentryで title または url が欠損しているためスキップしました")
        return None, warnings

    summary = _get_value(entry, "summary") or _get_value(entry, "description")
    published_at, date_warning = _parse_entry_datetime(entry, fetched_at, settings)
    if date_warning:
        warnings.append(date_warning)

    return (
        {
            "region": region,
            "category": "general",
            "title": title,
            "url": url,
            "source": _source_from_feed(feed, source_url),
            "published_at": published_at,
            "summary": _clean_summary(summary),
        },
        warnings,
    )


def _sort_news(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda item: item["published_at"], reverse=True)


def fetch_rss_news(
    feed_urls: tuple[str, ...],
    region: str,
    limit: int,
    settings,
) -> tuple[list[dict], list[str]]:
    """RSS/Atomフィードを取得し、NewsItem形式へ正規化する。"""
    feature_id = "F-01" if region == "domestic" else "F-02"
    region_label = "国内" if region == "domestic" else "海外"
    if not feed_urls:
        env_name = "NEWS_JP_RSS_URLS" if region == "domestic" else "NEWS_GLOBAL_RSS_URLS"
        return [], [f"{env_name} が未設定のため{region_label}ニュース取得をスキップしました"]

    try:
        import feedparser
    except ImportError:
        return [], ["feedparser が未インストールのためRSS取得を実行できません"]

    fetched_at = datetime.now(settings.timezone)
    items: list[dict] = []
    warnings: list[str] = []

    for feed_url in feed_urls:
        masked_url = sanitize_url(feed_url)
        try:
            feed_text = get_text(
                feed_url,
                timeout_seconds=settings.request_timeout_seconds,
                retry_count=settings.request_retry_count,
                feature_id=feature_id,
                process_name=PROCESS_NAME,
            )
        except (ExternalFetchError, ExternalDataError) as error:
            warnings.append(f"RSS取得に失敗しました: {masked_url}: {error.message}")
            continue

        parsed = feedparser.parse(feed_text)
        feed = _get_value(parsed, "feed", {})
        entries = list(_get_value(parsed, "entries", []) or [])
        if _get_value(parsed, "bozo", False):
            bozo_exception = _get_value(parsed, "bozo_exception", "解析警告")
            warnings.append(f"RSS解析警告: {masked_url}: {bozo_exception}")

        for entry in entries:
            normalized_item, entry_warnings = _normalize_rss_entry(
                entry,
                feed,
                region=region,
                source_url=feed_url,
                fetched_at=fetched_at,
                settings=settings,
            )
            warnings.extend(entry_warnings)
            if normalized_item:
                items.append(normalized_item)

    normalized_items = _sort_news(_deduplicate_news(items))
    return normalized_items[:limit], warnings
