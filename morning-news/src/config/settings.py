"""Morning News フェーズ1 の設定を管理する。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
REPORT_DIR = BASE_DIR / "reports"
LOG_DIR = BASE_DIR / "logs"
NEWS_LIMIT = 5
SUMMARY_MAX_LENGTH = 120
JST = ZoneInfo("Asia/Tokyo")


def load_settings() -> dict:
    """フェーズ1で使用する固定設定を返す。

    フェーズ1では .env 読み込みや外部API設定を扱わない。
    """
    now = datetime.now(JST)
    return {
        "app_mode": "sample",
        "base_dir": BASE_DIR,
        "sample_data_dir": SAMPLE_DATA_DIR,
        "report_dir": REPORT_DIR,
        "log_dir": LOG_DIR,
        "news_jp_path": SAMPLE_DATA_DIR / "news_jp.json",
        "news_global_path": SAMPLE_DATA_DIR / "news_global.json",
        "market_path": SAMPLE_DATA_DIR / "market.json",
        "news_limit": NEWS_LIMIT,
        "summary_max_length": SUMMARY_MAX_LENGTH,
        "timezone": JST,
        "target_date": now.date(),
    }
