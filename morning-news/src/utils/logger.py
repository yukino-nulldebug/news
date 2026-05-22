"""Morning News のログ出力を設定する。"""

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


class ContextFormatter(JSTFormatter):
    """機能IDと処理名がないログにも既定値を補完する。"""

    def format(self, record):
        if not hasattr(record, "feature_id"):
            record.feature_id = "-"
        if not hasattr(record, "process_name"):
            record.process_name = "-"
        return super().format(record)


def _build_handler(handler: logging.Handler) -> logging.Handler:
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        ContextFormatter(
            "%(asctime)s %(levelname)s %(feature_id)s %(process_name)s %(message)s"
        )
    )
    return handler


def setup_logger(log_dir: Path) -> logging.Logger:
    """標準出力と logs/app.log に出力するロガーを作成する。

    ファイル出力に失敗した場合も例外を外へ投げず、標準出力ロガーを返す。
    """
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
        log_warning(
            logger,
            "F-09",
            "logger.setup_logger",
            "logs/app.log に書き込めないため標準出力のみで継続します: %s",
            error,
        )

    return logger


def get_logger() -> logging.Logger:
    """設定済みの Morning News ロガーを返す。"""
    return logging.getLogger(LOGGER_NAME)


def _extra(feature_id: str, process_name: str) -> dict:
    return {"feature_id": feature_id, "process_name": process_name}


def log_info(
    logger: logging.Logger,
    feature_id: str,
    process_name: str,
    message: str,
    *args,
) -> None:
    """INFO ログを機能ID付きで出す。"""
    logger.info(message, *args, extra=_extra(feature_id, process_name))


def log_warning(
    logger: logging.Logger,
    feature_id: str,
    process_name: str,
    message: str,
    *args,
) -> None:
    """WARNING ログを機能ID付きで出す。"""
    logger.warning(message, *args, extra=_extra(feature_id, process_name))


def log_error(
    logger: logging.Logger,
    feature_id: str,
    process_name: str,
    message: str,
    *args,
) -> None:
    """ERROR ログを機能ID付きで出す。"""
    logger.error(message, *args, extra=_extra(feature_id, process_name))
