"""Morning News フェーズ1 のログ出力を設定する。"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOGGER_NAME = "morning_news"
JST = ZoneInfo("Asia/Tokyo")


class JSTFormatter(logging.Formatter):
    """ログ日時をJSTで表示するフォーマッター。"""

    def formatTime(self, record, datefmt=None):
        created_at = datetime.fromtimestamp(record.created, JST)
        if datefmt:
            return created_at.strftime(datefmt)
        return created_at.strftime("%Y-%m-%d %H:%M:%S")


def _build_handler(handler: logging.Handler) -> logging.Handler:
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        JSTFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    return handler


def setup_logger(log_dir: Path) -> logging.Logger:
    """標準出力と logs/app.log に出力するロガーを作成する。"""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

    logger.addHandler(_build_handler(logging.StreamHandler(sys.stdout)))

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.addHandler(
            _build_handler(logging.FileHandler(log_dir / "app.log", encoding="utf-8"))
        )
    except OSError as error:
        logger.warning("logs/app.log に書き込めないため標準出力のみで継続します: %s", error)

    return logger


def get_logger() -> logging.Logger:
    """設定済みの Morning News ロガーを返す。"""
    return logging.getLogger(LOGGER_NAME)
