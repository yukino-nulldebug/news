from __future__ import annotations

from src.utils.execution_result import (
    build_summary_message,
    create_execution_result,
    finish_execution,
    increment_count,
    record_error,
    record_warning,
    set_count,
)


def test_execution_result_records_counts_warnings_and_errors():
    result = create_execution_result("sample", "2026-05-26 07:00:00 JST")

    set_count(result, "news_domestic", 2)
    increment_count(result, "news_domestic")
    record_warning(result, "F-03", "news.formatter", "summary empty")
    record_error(result, "F-09", "main.main", "failed")
    finish_execution(result, "failed", "2026-05-26 07:01:00 JST")

    assert result["counts"]["news_domestic"] == 3
    assert result["counts"]["warnings"] == 1
    assert result["counts"]["errors"] == 1
    assert result["status"] == "failed"
    assert "warnings=1" in build_summary_message(result)
    assert "errors=1" in build_summary_message(result)
