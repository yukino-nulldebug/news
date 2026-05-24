"""Morning News のアプリケーション専用例外を定義する。"""

from __future__ import annotations


class MorningNewsError(Exception):
    """Morning News の共通例外。"""

    def __init__(
        self,
        message: str,
        *,
        feature_id: str,
        process_name: str,
        recoverable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.feature_id = feature_id
        self.process_name = process_name
        self.recoverable = recoverable


class ConfigError(MorningNewsError):
    """設定読み込み・設定値不正。"""


class DataLoadError(MorningNewsError):
    """ファイル読み込み失敗、JSON解析失敗。"""


class DataValidationError(MorningNewsError):
    """JSON必須項目欠損、型不正。"""


class ExternalFetchError(MorningNewsError):
    """外部HTTP取得失敗。"""


class ExternalDataError(MorningNewsError):
    """外部レスポンスの解析・正規化失敗。"""


class SummaryFormatError(MorningNewsError):
    """概要文整形失敗。"""


class MarketCalculationError(MorningNewsError):
    """前日比・変化率計算失敗。"""


class ReportGenerationError(MorningNewsError):
    """Markdown生成失敗。"""


class ReportWriteError(MorningNewsError):
    """レポート保存失敗。"""


class LoggingSetupError(MorningNewsError):
    """ログファイル設定失敗。"""
