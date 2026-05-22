"""Morning News のMarkdownレポートを保存する。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from src.utils.exceptions import ReportWriteError

FEATURE_ID = "F-08"
PROCESS_NAME = "report.writer"


def build_report_path(report_dir: Path, target_date: date) -> Path:
    """reports/YYYY-MM-DD.md の保存先パスを組み立てる。"""
    try:
        if isinstance(target_date, str):
            file_name = f"{target_date}.md"
        else:
            file_name = f"{target_date:%Y-%m-%d}.md"
        return report_dir / file_name
    except (TypeError, ValueError) as error:
        raise ReportWriteError(
            f"レポート保存先の生成に失敗しました: {error}",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
        ) from error


def write_report(markdown: str, report_path: Path) -> Path:
    """Markdown本文をUTF-8で保存する。"""
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(markdown, encoding="utf-8")
        return report_path
    except OSError as error:
        raise ReportWriteError(
            f"レポート保存に失敗しました: {report_path}",
            feature_id=FEATURE_ID,
            process_name=PROCESS_NAME,
        ) from error
