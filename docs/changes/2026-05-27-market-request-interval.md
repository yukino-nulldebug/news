# マーケットAPI連続取得間隔の追加

## 背景

Alpha Vantage の無料枠では短時間の連続リクエストで制限に当たることがある。
`.env` に待機秒数を設定し、複数のマーケット対象を取得するときに各取得の間で待機できるようにする。

## 設定

```env
# external request
REQUEST_TIMEOUT_SECONDS=10
REQUEST_RETRY_COUNT=4
MARKET_REQUEST_INTERVAL_SECONDS=2
```

| 設定 | 意味 |
| --- | --- |
| `REQUEST_TIMEOUT_SECONDS=10` | 1回のAPI通信を最大10秒待つ |
| `REQUEST_RETRY_COUNT=4` | 失敗時に最大4回リトライする |
| `MARKET_REQUEST_INTERVAL_SECONDS=2` | マーケットAPIを連続取得するとき、各リクエストの間に2秒待つ |

## 実装内容

| ファイル | 変更内容 |
| --- | --- |
| `morning-news/.env` | `MARKET_REQUEST_INTERVAL_SECONDS=2` を追加し、誤った単数形の変数名を置き換えた |
| `morning-news/.env.example` | Alpha Vantage向けの推奨外部取得設定を追加した |
| `morning-news/src/config/settings.py` | `MARKET_REQUEST_INTERVAL_SECONDS` を読み込み、`Settings.market_request_interval_seconds` として保持する |
| `morning-news/src/market/providers/alpha_vantage.py` | 複数ターゲット取得ループで最後以外の取得後に `time.sleep()` する |
| `morning-news/tests/` | 設定読み込みと待機処理のテストを追加した |

## 運用メモ

`MARKET_REQUEST_INTERVAL_SECONDS=2` で制限に当たる場合は、まず `5` へ増やして再実行する。
未設定時のコード既定値は `0` で、待機しない。
