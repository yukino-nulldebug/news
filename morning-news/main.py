"""Morning News のCLIエントリポイント。"""

from __future__ import annotations

import sys
from datetime import datetime

from src.config.settings import load_settings
from src.market.calculator import calculate_market_changes
from src.market.fetcher import load_market_items
from src.news.fetcher import load_news_items
from src.news.formatter import format_news_items
from src.report.generator import generate_market_comments, generate_report
from src.report.writer import build_report_path, write_report
from src.utils.exceptions import DataLoadError, DataValidationError, MorningNewsError
from src.utils.execution_result import (
    build_summary_message,
    create_execution_result,
    finish_execution,
    record_error,
    record_warning,
    set_count,
)
from src.utils.logger import log_error, log_info, log_warning, setup_logger


def _format_execution_time(settings: dict) -> str:
    """実行結果用のJST時刻文字列を作る。"""
    return datetime.now(settings["timezone"]).strftime("%Y-%m-%d %H:%M:%S JST")


def _format_report_time(settings: dict) -> str:
    """レポート本文用のJST時刻文字列を作る。"""
    return datetime.now(settings["timezone"]).strftime("%Y-%m-%d %H:%M JST")


def record_recoverable_warning(
    logger,
    result: dict,
    feature_id: str,
    process_name: str,
    message: str,
) -> None:
    """継続可能な警告をログと実行結果に記録する。"""
    record_warning(result, feature_id, process_name, message)
    log_warning(logger, feature_id, process_name, message)


def build_report_data(settings: dict, logger, result: dict) -> dict:
    """サンプルJSONからレポート用データを組み立てる。"""
    news_limit = settings["news_limit"]

    log_info(
        logger,
        "F-01",
        "news.fetcher",
        "国内ニュースJSONを読み込みます: %s",
        settings["news_jp_path"],
    )
    domestic_news = load_news_items(settings["news_jp_path"], "F-01")[:news_limit]
    set_count(result, "news_domestic", len(domestic_news))
    log_info(logger, "F-01", "news.fetcher", "国内ニュース読み込み件数: %s", len(domestic_news))

    log_info(
        logger,
        "F-02",
        "news.fetcher",
        "海外ニュースJSONを読み込みます: %s",
        settings["news_global_path"],
    )
    global_news = load_news_items(settings["news_global_path"], "F-02")[:news_limit]
    set_count(result, "news_global", len(global_news))
    log_info(logger, "F-02", "news.fetcher", "海外ニュース読み込み件数: %s", len(global_news))

    formatted_domestic_news = format_news_items(
        domestic_news,
        max_length=settings["summary_max_length"],
    )
    formatted_global_news = format_news_items(
        global_news,
        max_length=settings["summary_max_length"],
    )
    log_info(
        logger,
        "F-03",
        "news.formatter",
        "ニュース概要文整形件数: %s",
        len(formatted_domestic_news) + len(formatted_global_news),
    )

    for index, item in enumerate(domestic_news):
        if not str(item.get("summary", "")).strip():
            record_recoverable_warning(
                logger,
                result,
                "F-03",
                "news.formatter",
                f"domestic_news[{index}] の summary が空のため代替文を設定しました",
            )
    for index, item in enumerate(global_news):
        if not str(item.get("summary", "")).strip():
            record_recoverable_warning(
                logger,
                result,
                "F-03",
                "news.formatter",
                f"global_news[{index}] の summary が空のため代替文を設定しました",
            )

    log_info(
        logger,
        "F-04",
        "market.fetcher",
        "マーケットJSONを読み込みます: %s",
        settings["market_path"],
    )
    market_items = load_market_items(settings["market_path"], "F-04")
    set_count(result, "markets", len(market_items))
    log_info(logger, "F-04", "market.fetcher", "マーケット読み込み件数: %s", len(market_items))

    log_info(logger, "F-05", "market.calculator", "変化率計算を開始します")
    calculated_markets = calculate_market_changes(market_items)
    log_info(
        logger,
        "F-05",
        "market.calculator",
        "変化率計算件数: %s",
        len(calculated_markets),
    )

    for item in calculated_markets:
        if item.get("change_rate") is None:
            record_recoverable_warning(
                logger,
                result,
                "F-05",
                "market.calculator",
                f"{item['name']} は previous_close が 0 のため変化率を計算できませんでした",
            )

    market_comments = generate_market_comments(calculated_markets)
    set_count(result, "market_comments", len(market_comments))
    log_info(
        logger,
        "F-07",
        "report.generator",
        "市況コメント生成件数: %s",
        len(market_comments),
    )

    return {
        "generated_at": _format_report_time(settings),
        "mode": settings["app_mode"],
        "news_domestic": formatted_domestic_news,
        "news_global": formatted_global_news,
        "markets": calculated_markets,
        "warnings": [warning["message"] for warning in result["warnings"]],
        "execution_summary": result,
    }


def log_exception(logger, result: dict, error: MorningNewsError) -> None:
    """例外情報をログと実行結果に記録する。"""
    record_error(result, error.feature_id, error.process_name, error.message)
    log_error(logger, error.feature_id, error.process_name, error.message)


def log_execution_summary(logger, result: dict) -> None:
    """実行結果サマリーをログ出力する。"""
    message = build_summary_message(result)
    if result["status"] == "warning":
        log_warning(logger, "F-09", "main.summary", message)
    elif result["status"] in {"failed", "data_failed"}:
        log_error(logger, "F-09", "main.summary", message)
    else:
        log_info(logger, "F-09", "main.summary", message)


def _status_for_error(error: MorningNewsError) -> str:
    if isinstance(error, (DataLoadError, DataValidationError)):
        return "data_failed"
    return "failed"


def _exit_code_for_error(error: MorningNewsError) -> int:
    if isinstance(error, (DataLoadError, DataValidationError)):
        return 2
    return 1


def main() -> int:
    """レポート生成処理を実行し、終了コードを返す。"""
    logger = None
    result = None
    settings = None
    try:
        settings = load_settings()
        logger = setup_logger(settings["log_dir"])
        result = create_execution_result(
            settings["app_mode"],
            _format_execution_time(settings),
        )

        log_info(logger, "F-10", "main.main", "Morning News を開始しました")
        log_info(
            logger,
            "F-10",
            "settings.load_settings",
            "設定読み込み完了: APP_MODE=%s",
            settings["app_mode"],
        )

        report_data = build_report_data(settings, logger, result)
        log_info(logger, "F-06", "report.generator", "Markdown生成を開始します")
        markdown_text = generate_report(report_data)
        log_info(logger, "F-06", "report.generator", "Markdown生成完了")

        report_path = build_report_path(settings["report_dir"], settings["target_date"])
        log_info(logger, "F-08", "report.writer", "レポート保存を開始します: %s", report_path)
        saved_path = write_report(markdown_text, report_path)

        log_info(logger, "F-08", "report.writer", "レポート保存先: %s", saved_path)

        status = "warning" if result["warnings"] else "success"
        finish_execution(result, status, _format_execution_time(settings))
        log_execution_summary(logger, result)
        log_info(logger, "F-10", "main.main", "Morning News は正常終了しました")
        return 0
    except MorningNewsError as error:
        if logger and result is not None and settings is not None:
            log_exception(logger, result, error)
            finish_execution(result, _status_for_error(error), _format_execution_time(settings))
            log_execution_summary(logger, result)
            log_error(logger, "F-10", "main.main", "Morning News は失敗しました: %s", error.message)
        print(f"ERROR: {error.message}", file=sys.stderr)
        return _exit_code_for_error(error)
    except Exception as error:
        if logger and result is not None and settings is not None:
            message = f"想定外のエラーが発生しました: {error}"
            record_error(result, "F-09", "main.main", message)
            finish_execution(result, "failed", _format_execution_time(settings))
            log_error(logger, "F-09", "main.main", message)
            log_execution_summary(logger, result)
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
