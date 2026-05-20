"""Morning News フェーズ1 のCLIエントリポイント。"""

from __future__ import annotations

import sys
from datetime import datetime

from src.config.settings import load_settings
from src.market.calculator import calculate_market_changes
from src.market.fetcher import fetch_sample_markets
from src.news.fetcher import fetch_sample_news
from src.news.formatter import format_news_items
from src.report.generator import generate_report
from src.report.writer import build_report_path, write_report
from src.utils.logger import setup_logger


def build_report_data(settings: dict, logger) -> dict:
    """フェーズ1のサンプルJSONからレポート用データを組み立てる。"""
    logger.info("サンプルデータ読み込み開始")

    domestic_news, global_news = fetch_sample_news(settings)
    market_items = fetch_sample_markets(settings)

    logger.info("国内ニュース読み込み件数: %s", len(domestic_news))
    logger.info("海外ニュース読み込み件数: %s", len(global_news))
    logger.info("マーケット読み込み件数: %s", len(market_items))

    formatted_domestic_news = format_news_items(
        domestic_news,
        max_length=settings["summary_max_length"],
    )
    formatted_global_news = format_news_items(
        global_news,
        max_length=settings["summary_max_length"],
    )
    calculated_markets = calculate_market_changes(market_items)

    warnings = [
        f"{item['name']}は変化率を計算できませんでした。"
        for item in calculated_markets
        if item.get("change_rate") is None
    ]
    for warning in warnings:
        logger.warning(warning)

    generated_at = datetime.now(settings["timezone"]).strftime("%Y-%m-%d %H:%M JST")

    return {
        "generated_at": generated_at,
        "mode": settings["app_mode"],
        "news_domestic": formatted_domestic_news,
        "news_global": formatted_global_news,
        "markets": calculated_markets,
        "warnings": warnings,
    }


def main() -> int:
    """フェーズ1のレポート生成処理を実行する。"""
    logger = None
    try:
        settings = load_settings()
        logger = setup_logger(settings["log_dir"])

        logger.info("Morning News を開始しました")
        logger.info("APP_MODE=%s", settings["app_mode"])

        report_data = build_report_data(settings, logger)
        markdown_text = generate_report(report_data)
        logger.info("Markdown生成完了")

        report_path = build_report_path(settings["report_dir"], settings["target_date"])
        saved_path = write_report(markdown_text, report_path)

        logger.info("レポート保存先: %s", saved_path)
        logger.info("Morning News は正常終了しました")
        return 0
    except (FileNotFoundError, OSError, ValueError) as error:
        if logger:
            logger.error("Morning News は失敗しました: %s", error)
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
