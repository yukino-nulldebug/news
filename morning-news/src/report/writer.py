"""Morning News フェーズ1 のMarkdownレポートを保存する。"""

from __future__ import annotations

from datetime import date
from pathlib import Path


def build_report_path(report_dir: Path, target_date: date) -> Path:
    """reports/YYYY-MM-DD.md の保存先パスを組み立てる。"""
    if isinstance(target_date, str):
        file_name = f"{target_date}.md"
    else:
        file_name = f"{target_date:%Y-%m-%d}.md"
    return report_dir / file_name


def write_report(markdown: str, report_path: Path) -> Path:
    """Markdown本文をUTF-8で保存する。"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(markdown, encoding="utf-8")
    return report_path
