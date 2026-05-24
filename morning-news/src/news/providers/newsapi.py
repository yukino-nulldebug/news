"""News API Providerの未対応スタブ。"""

from __future__ import annotations


def fetch_newsapi_news(settings, region: str) -> tuple[list[dict], list[str]]:
    """Phase 4では外部ニュースAPIへ通信せず、未対応警告だけ返す。"""
    return [], ["NEWS_PROVIDER=newsapi は Phase 4 では未対応のため RSS Provider を使用してください。"]
