"""Morning News のCLIエントリポイント。"""

from __future__ import annotations

import sys
from datetime import datetime

from src.config.settings import LOG_DIR, Settings, load_settings
from src.market.calculator import calculate_market_changes
from src.market.fetcher import fetch_markets_for_mode
from src.news.fetcher import fetch_news_for_mode
from src.news.formatter import format_news_items
from src.report.generator import DISCLAIMER, generate_market_comments, generate_report
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
from src.utils.http_client import sanitize_text
from src.utils.logger import log_error, log_info, log_warning, setup_logger


def _format_execution_time(settings: Settings) -> str:
    """実行結果用のJST時刻文字列を作る。"""
    return datetime.now(settings.timezone).strftime("%Y-%m-%d %H:%M:%S JST")


def _format_report_time(settings: Settings) -> str:
    """レポート本文用のJST時刻文字列を作る。"""
    return datetime.now(settings.timezone).strftime("%Y-%m-%d %H:%M JST")


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _has_usable_market_data(items: list[dict]) -> bool:
    return any(_is_number(item.get("current_value")) for item in items)


def record_recoverable_warning(
    logger,
    result: dict,
    feature_id: str,
    process_name: str,
    message: str,
) -> None:
    """継続可能な警告をログと実行結果に記録する。"""
    safe_message = sanitize_text(message)
    record_warning(result, feature_id, process_name, safe_message)
    log_warning(logger, feature_id, process_name, safe_message)


def _warning_parts(entry, default_feature_id: str, default_process_name: str) -> tuple[str, str, str]:
    if isinstance(entry, dict):
        return (
            entry.get("feature_id", default_feature_id),
            entry.get("process_name", default_process_name),
            entry.get("message", ""),
        )
    return default_feature_id, default_process_name, str(entry)


def record_warning_entries(
    logger,
    result: dict,
    warnings,
    default_feature_id: str,
    default_process_name: str,
) -> None:
    """文字列または警告dictの一覧を実行結果とログへ記録する。"""
    for warning in warnings:
        feature_id, process_name, message = _warning_parts(
            warning,
            default_feature_id,
            default_process_name,
        )
        if message:
            record_recoverable_warning(logger, result, feature_id, process_name, message)


def build_report_data(settings: Settings, logger, result: dict) -> dict:
    """取得済みニュース・マーケット情報からレポート用データを組み立てる。"""
    if settings.app_mode == "sample":
        log_info(
            logger,
            "F-01",
            "news.fetcher",
            "国内ニュースJSONを読み込みます: %s",
            settings.news_jp_path,
        )
        log_info(
            logger,
            "F-02",
            "news.fetcher",
            "海外ニュースJSONを読み込みます: %s",
            settings.news_global_path,
        )
    else:
        log_info(
            logger,
            "F-01",
            "news.fetcher",
            "国内ニュース取得を開始します: provider=%s feeds=%s",
            settings.news_provider,
            len(settings.news_jp_rss_urls),
        )
        log_info(
            logger,
            "F-02",
            "news.fetcher",
            "海外ニュース取得を開始します: provider=%s feeds=%s",
            settings.news_provider,
            len(settings.news_global_rss_urls),
        )

    domestic_news, global_news, news_warnings = fetch_news_for_mode(settings)
    record_warning_entries(logger, result, news_warnings, "F-01", "news.fetcher")
    set_count(result, "news_domestic", len(domestic_news))
    set_count(result, "news_global", len(global_news))
    log_info(logger, "F-01", "news.fetcher", "国内ニュース取得件数: %s", len(domestic_news))
    log_info(logger, "F-02", "news.fetcher", "海外ニュース取得件数: %s", len(global_news))

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

    formatted_domestic_news = format_news_items(
        domestic_news,
        max_length=settings.summary_max_length,
    )
    formatted_global_news = format_news_items(
        global_news,
        max_length=settings.summary_max_length,
    )
    log_info(
        logger,
        "F-03",
        "news.formatter",
        "ニュース概要文整形件数: %s",
        len(formatted_domestic_news) + len(formatted_global_news),
    )

    if settings.app_mode == "sample":
        log_info(
            logger,
            "F-04",
            "market.fetcher",
            "マーケットJSONを読み込みます: %s",
            settings.market_path,
        )
    else:
        log_info(
            logger,
            "F-04",
            "market.fetcher",
            "マーケットAPI取得を開始します: provider=%s targets=%s",
            settings.market_provider,
            len(settings.market_targets),
        )

    market_items, market_warnings = fetch_markets_for_mode(settings)
    record_warning_entries(logger, result, market_warnings, "F-04", "market.fetcher")
    set_count(result, "markets", len(market_items))
    log_info(logger, "F-04", "market.fetcher", "マーケット取得件数: %s", len(market_items))

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
        calculation_warning = item.get("calculation_warning")
        if calculation_warning:
            record_recoverable_warning(
                logger,
                result,
                "F-05",
                "market.calculator",
                calculation_warning,
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

    if (
        settings.app_mode == "api"
        and not formatted_domestic_news
        and not formatted_global_news
        and not _has_usable_market_data(calculated_markets)
    ):
        raise DataLoadError(
            "apiモードで外部データを1件も取得できませんでした。",
            feature_id="F-09",
            process_name="main.build_report_data",
        )

    return {
        "generated_at": _format_report_time(settings),
        "mode": settings.app_mode,
        "news_domestic": formatted_domestic_news,
        "news_global": formatted_global_news,
        "markets": calculated_markets,
        "comments": market_comments,
        "warnings": [warning["message"] for warning in result["warnings"]],
        "errors": [error["message"] for error in result["errors"]],
        "disclaimer": DISCLAIMER,
        "execution_summary": result,
    }


def log_exception(logger, result: dict, error: MorningNewsError) -> None:
    """例外情報をログと実行結果に記録する。"""
    safe_message = sanitize_text(error.message)
    record_error(result, error.feature_id, error.process_name, safe_message)
    log_error(logger, error.feature_id, error.process_name, safe_message)


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
        logger = setup_logger(settings.log_dir)
        result = create_execution_result(
            settings.app_mode,
            _format_execution_time(settings),
        )

        log_info(logger, "F-10", "main.main", "Morning News を開始しました")
        log_info(
            logger,
            "F-10",
            "settings.load_settings",
            "設定読み込み完了: APP_MODE=%s",
            settings.app_mode,
        )
        record_warning_entries(
            logger,
            result,
            settings.settings_warnings,
            "F-10",
            "settings.load_settings",
        )

        report_data = build_report_data(settings, logger, result)
        log_info(logger, "F-06", "report.generator", "Markdown生成を開始します")
        markdown_text = generate_report(report_data)
        log_info(logger, "F-06", "report.generator", "Markdown生成完了")

        report_path = build_report_path(settings.report_dir, settings.target_date)
        log_info(logger, "F-08", "report.writer", "レポート保存を開始します: %s", report_path)
        saved_path = write_report(markdown_text, report_path)

        log_info(logger, "F-08", "report.writer", "レポート保存先: %s", saved_path)

        status = "warning" if result["warnings"] else "success"
        finish_execution(result, status, _format_execution_time(settings))
        log_execution_summary(logger, result)
        log_info(logger, "F-10", "main.main", "Morning News は正常終了しました")
        return 0
    except MorningNewsError as error:
        if logger is None:
            try:
                logger = setup_logger(LOG_DIR)
            except Exception:
                logger = None
        if logger and result is not None and settings is not None:
            log_exception(logger, result, error)
            finish_execution(result, _status_for_error(error), _format_execution_time(settings))
            log_execution_summary(logger, result)
            log_error(logger, "F-10", "main.main", "Morning News は失敗しました: %s", error.message)
        elif logger:
            log_error(logger, error.feature_id, error.process_name, error.message)
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
