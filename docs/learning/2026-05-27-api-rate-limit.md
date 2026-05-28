# Alpha Vantage API の Rate Limit 対応

## 目的

Alpha Vantage でマーケット情報を複数件取得するとき、短時間の連続リクエストで失敗しやすい問題を、設定で調整できる形にする。

ポートフォリオとしては、単にAPIを呼ぶだけでなく、外部サービスの制限を前提にした実装判断を見せる。

## 発生した問題

`api` モードでマーケット情報を取得するとき、複数の対象を連続で取りに行くため、無料枠や一時的な制限に当たる可能性があった。

失敗時にただ例外で止めるだけだと、どの対象で失敗したか、設定で回避できる問題か、実装の不具合かを判断しにくい。

## 原因

外部APIは、レスポンス速度、利用枠、レート制限、取得可能なシンボルに左右される。

そのため、次のような前提をコード側で扱う必要があった。

- 1回の通信に上限時間を設ける。
- 一時的な失敗はretryする。
- 複数対象を連続取得するときは、対象間に待機時間を入れられるようにする。
- 取得できた対象だけでレポート生成を継続し、失敗は警告として残す。

## 調査

- 既存の `api` モードと Alpha Vantage Provider の処理を確認した。
- HTTP共通処理に timeout / retry があることを確認した。
- `Settings` で外部取得の設定値を環境変数から読める構成にした。
- 連続取得間隔はコード固定ではなく、`.env` で調整できる方針にした。
- APIキーや認証値をログ・レポートへ出さない方針を確認した。

## 実装

主な変更点は以下。

| 対象 | 内容 |
| --- | --- |
| `morning-news/.env.example` | 外部取得設定例として `REQUEST_TIMEOUT_SECONDS`、`REQUEST_RETRY_COUNT`、`MARKET_REQUEST_INTERVAL_SECONDS` を追加した。 |
| `morning-news/src/config/settings.py` | `MARKET_REQUEST_INTERVAL_SECONDS` を読み込み、`Settings.market_request_interval_seconds` として保持するようにした。 |
| `morning-news/src/market/providers/alpha_vantage.py` | 複数ターゲットの取得ループで、最後以外の取得後に `time.sleep()` できるようにした。 |
| `morning-news/src/utils/http_client.py` | retry可能なHTTPステータスを判定し、URL内のAPIキーをマスクする方針を維持した。 |
| `morning-news/tests/` | 設定読み込み、Providerの待機処理、APIキーのマスクをテストで固定した。 |

設定例。

```env
REQUEST_TIMEOUT_SECONDS=10
REQUEST_RETRY_COUNT=4
MARKET_REQUEST_INTERVAL_SECONDS=2
```

## 学んだこと

API連携では、取得処理そのものよりも、失敗したときに調整・観測・継続できる設計が重要だった。

特に無料枠のAPIでは、次の観点を最初から持っておく必要がある。

- タイムアウトを設定する。
- 一時的な失敗はretryできるようにする。
- レート制限に備えて待機秒数を設定化する。
- 取得失敗を握りつぶさず、警告として残す。
- 秘密情報をログに出さない。

## 次の改善

- APIごとの制限に合わせた backoff を追加する。
- 取得結果をキャッシュし、同じ情報を何度も取りに行かないようにする。
- queue化して、マーケット取得対象が増えても制限を超えにくい構成にする。
- 実APIを使わずに制限レスポンスを再現できるProviderテストを増やす。
