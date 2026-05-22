"""Morning News の実行結果を集計する。"""

from __future__ import annotations


def create_execution_result(mode: str, started_at: str) -> dict:
    """実行結果集計用の初期値を返す。"""
    return {
        "status": "running",
        "mode": mode,
        "started_at": started_at,
        "ended_at": None,
        "counts": {
            "news_domestic": 0,
            "news_global": 0,
            "markets": 0,
            "market_comments": 0,
            "warnings": 0,
            "errors": 0,
        },
        "warnings": [],
        "errors": [],
    }


def set_count(result: dict, key: str, count: int) -> None:
    """件数を設定する。"""
    result["counts"][key] = count


def increment_count(result: dict, key: str, amount: int = 1) -> None:
    """件数を加算する。"""
    result["counts"][key] = result["counts"].get(key, 0) + amount


def record_warning(
    result: dict,
    feature_id: str,
    process_name: str,
    message: str,
) -> None:
    """警告情報を追加し、警告件数を更新する。"""
    result["warnings"].append(
        {
            "feature_id": feature_id,
            "process_name": process_name,
            "message": message,
        }
    )
    result["counts"]["warnings"] = len(result["warnings"])


def record_error(
    result: dict,
    feature_id: str,
    process_name: str,
    message: str,
) -> None:
    """エラー情報を追加し、エラー件数を更新する。"""
    result["errors"].append(
        {
            "feature_id": feature_id,
            "process_name": process_name,
            "message": message,
        }
    )
    result["counts"]["errors"] = len(result["errors"])


def finish_execution(result: dict, status: str, ended_at: str) -> dict:
    """終了ステータスと終了時刻を設定する。"""
    result["status"] = status
    result["ended_at"] = ended_at
    return result


def build_summary_message(result: dict) -> str:
    """サマリーログ用の文字列を作る。"""
    counts = result["counts"]
    return (
        f"実行結果: status={result['status']} "
        f"warnings={counts.get('warnings', 0)} "
        f"errors={counts.get('errors', 0)} "
        f"news_domestic={counts.get('news_domestic', 0)} "
        f"news_global={counts.get('news_global', 0)} "
        f"markets={counts.get('markets', 0)}"
    )
