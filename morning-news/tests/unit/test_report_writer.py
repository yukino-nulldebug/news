from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.report.writer import build_report_path, write_report
from src.utils.exceptions import ReportWriteError


def test_build_report_path_uses_target_date():
    path = build_report_path(Path("/tmp/reports"), date(2026, 5, 26))

    assert str(path).endswith("/tmp/reports/2026-05-26.md")


def test_build_report_path_accepts_string_date(tmp_path):
    assert build_report_path(tmp_path, "2026-05-26").name == "2026-05-26.md"


def test_build_report_path_raises_for_invalid_target_date(tmp_path):
    with pytest.raises(ReportWriteError):
        build_report_path(tmp_path, object())


def test_write_report_creates_parent_and_writes_text(tmp_path):
    report_path = tmp_path / "reports" / "2026-05-26.md"

    saved = write_report("# report\n", report_path)

    assert saved == report_path
    assert report_path.read_text(encoding="utf-8") == "# report\n"


def test_write_report_raises_when_parent_path_is_file(tmp_path):
    parent_as_file = tmp_path / "reports"
    parent_as_file.write_text("not a directory", encoding="utf-8")

    with pytest.raises(ReportWriteError):
        write_report("# report\n", parent_as_file / "2026-05-26.md")
