"""Morning News のMarkdownレポートを生成する。"""

from __future__ import annotations

from src.utils.exceptions import ReportGenerationError
from src.utils.http_client import sanitize_text

DISCLAIMER = "本レポートは情報提供を目的としており、投資助言ではありません。"
MARKET_COMMENT_DISCLAIMER = "本コメントは情報提供であり投資助言ではありません。"
FEATURE_ID = "F-06"
PROCESS_NAME = "report.generator"
REQUIRED_REPORT_KEYS = (
    "generated_at",
    "mode",
    "news_domestic",
    "news_global",
    "markets",
    "comments",
    "warnings",
    "errors",
    "disclaimer",
    "execution_summary",
)


def _format_number(value) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _format_signed_number(value) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2f}"


def _format_rate(value) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def _generate_highlights(report_data: dict) -> str:
    highlights = []

    domestic_news = report_data.get("news_domestic", [])
    global_news = report_data.get("news_global", [])
    markets = report_data.get("markets", [])

    if domestic_news:
        highlights.append(f"- 国内: {domestic_news[0]['title']}")
    if global_news:
        highlights.append(f"- 海外: {global_news[0]['title']}")
    if markets:
        first_market = markets[0]
        highlights.append(
            f"- 市況: {first_market['name']}は前日比 {_format_rate(first_market.get('change_rate'))}"
        )

    if not highlights:
        highlights.append("- サンプルデータから注目ポイントを取得できませんでした。")

    return "\n".join(highlights)


def generate_news_section(title: str, items: list[dict]) -> str:
    """国内または海外ニュースのセクションを生成する。"""
    lines = [f"## {title}", ""]
    if not items:
        lines.append("取得できませんでした。")
        return "\n".join(lines)

    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"### {index}. {item['title']}",
                f"- 配信元: {item['source']}",
                f"- 公開日時: {item['published_at']}",
                f"- 概要: {item.get('short_summary', '概要はありません。')}",
                f"- URL: {item['url']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def generate_market_section(items: list[dict]) -> str:
    """マーケット情報のMarkdown表を生成する。"""
    lines = [
        "## 4. マーケット情報",
        "",
        "| 指標 | 現在値 | 前日比 | 変化率 | 取得日時 |",
        "| --- | ---: | ---: | ---: | --- |",
    ]

    if not items:
        lines.append("| N/A | N/A | N/A | N/A | N/A |")
        return "\n".join(lines)

    for item in items:
        current_value = _format_number(item.get("current_value"))
        unit = item.get("unit", "")
        if unit:
            current_value = f"{current_value} {unit}"

        lines.append(
            "| {name} | {current_value} | {change} | {change_rate} | {fetched_at} |".format(
                name=item["name"],
                current_value=current_value,
                change=_format_signed_number(item.get("change")),
                change_rate=_format_rate(item.get("change_rate")),
                fetched_at=item["fetched_at"],
            )
        )
    return "\n".join(lines)


def generate_market_comments(items: list[dict]) -> list[str]:
    """投資助言にならない中立的な市況コメントを生成する。"""
    comments = []
    for item in items:
        change_rate = item.get("change_rate")
        name = item.get("name", "対象指標")
        if change_rate is None:
            comments.append(f"{name}は変化率を計算できませんでした。")
        elif change_rate > 0:
            comments.append(f"{name}は前日比で上昇傾向です。")
        elif change_rate < 0:
            comments.append(f"{name}は前日比で下落傾向です。")
        else:
            comments.append(f"{name}は前日比で大きな変動は見られません。")
    return comments


def generate_report(report_data: dict) -> str:
    """Morning News レポート全体のMarkdown本文を生成する。"""
    try:
        if not isinstance(report_data, dict):
            raise TypeError("report_data は dict である必要があります。")

        missing_keys = [key for key in REQUIRED_REPORT_KEYS if key not in report_data]
        if missing_keys:
            raise KeyError(", ".join(missing_keys))

        market_comments = report_data["comments"]
        warnings = report_data["warnings"]

        sections = [
            "# Morning News Report",
            f"作成日時: {report_data['generated_at']}",
            f"実行モード: {report_data['mode']}",
            "",
            "## 1. 今日の注目ポイント",
            "",
            _generate_highlights(report_data),
            "",
            generate_news_section("2. 国内ニュース", report_data.get("news_domestic", [])),
            "",
            generate_news_section("3. 海外ニュース", report_data.get("news_global", [])),
            "",
            generate_market_section(report_data.get("markets", [])),
            "",
            "## 5. 市況コメント",
            "",
        ]

        if market_comments:
            sections.extend(f"- {comment}" for comment in market_comments)
        else:
            sections.append("- 市況コメントを生成できませんでした。")
        sections.append(f"- {MARKET_COMMENT_DISCLAIMER}")

        sections.extend(["", "## 6. 注意事項", "", report_data["disclaimer"]])

        if warnings:
            sections.extend(["", "### 警告", ""])
            sections.extend(f"- {sanitize_text(warning)}" for warning in warnings)

        return "\n".join(sections).rstrip() + "\n"
    except (KeyError, TypeError, ValueError) as error:
        raise ReportGenerationError(
            f"レポート生成に失敗しました: {error}",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
        ) from error
