# Morning News 詳細設計 Phase 5

| Phase | 対象 | 完了条件 |
| --- | --- | --- |
| Phase 5 | pytest追加 | 主要処理の単体テスト、Providerモックテスト、異常系テスト、sample/apiの結合テストが通る。 |

## 1. 詳細設計の目的

本書は、要件定義および基本設計で定義したテスト方針をもとに、Phase 5 で追加する pytest の構成、テスト対象、テストデータ、モック方針、実行コマンド、受け入れ条件を具体化するための詳細設計書である。

Phase 1 では、`sample_data` からMarkdownレポートを生成する最小機能を実装した。
Phase 2 では、ログ、例外、実行結果集計、終了コード制御を追加した。
Phase 3 では、概要文整形、変化率計算、市況コメント生成を追加した。
Phase 4 では、`.env` 読み込み、`APP_MODE=api`、RSS/API Provider、HTTP共通処理、外部取得の警告処理を追加した。

Phase 5 では、これまで手動確認していた主要処理を pytest で自動化する。
テストは、外部ネットワークや実APIキーに依存せず、ローカル環境とGitHub公開後の第三者環境で再現できることを優先する。

Phase 5 は対象範囲が広いため、実装時は `Phase 5-A` と `Phase 5-B` に分けて進めてもよい。
ただし、本書における Phase 5 の完了条件は、5-A と 5-B の両方が完了し、全体の `python3 -m pytest` が成功することとする。

## 2. Phase 5 の対象範囲

### 2.1 Phase 5 で実装する機能

| 対象 | 内容 |
| --- | --- |
| pytest依存関係 | pytestをテスト実行用依存関係として追加する |
| テストディレクトリ整備 | `tests/` 配下に単体、Provider、結合、異常系テストを配置する |
| 共通fixture | `tmp_path`、`monkeypatch`、設定オブジェクト、サンプルデータ、疑似HTTPレスポンスを共通化する |
| 単体テスト | 概要文整形、変化率計算、Markdown生成、レポート保存先生成、実行結果集計を検証する |
| 設定テスト | `.env` / 環境変数、`APP_MODE`、Provider、数値設定、URL設定のパースを検証する |
| sample取得テスト | `sample_data/*.json` の読み込み、必須項目検証、件数制限を検証する |
| Providerモックテスト | RSS、NewsAPI未対応スタブ、Alpha Vantage、HTTP共通処理を外部通信なしで検証する |
| 結合テスト | `sample` モードと、HTTPをモックした `api` モードのレポート生成フローを検証する |
| 異常系テスト | JSON欠損、必須項目欠損、数値不正、保存失敗、全外部取得失敗の終了コードを検証する |
| セキュリティ回帰テスト | APIキーや認証URLがログ、警告、レポート、例外メッセージに出ないことを検証する |

### 2.2 Phase 5 では実装しない機能

| 対象外 | 理由 |
| --- | --- |
| 実APIへのE2Eテスト | APIキー、無料枠、ネットワーク状態に依存するため、公開リポジトリの必須テストにしない |
| 定時実行テスト | Phase 6 のREADME整備または後続任意タスクで扱う |
| Web UIテスト | MVP対象外 |
| 通知テスト | MVP対象外 |
| AI要約品質テスト | AI要約はMVP対象外 |
| 厳密なカバレッジ閾値運用 | MVPでは主要処理の回帰検知を優先し、数値閾値は後続で設定する |
| 外部サービスの利用規約検証 | README・公開前チェックで確認観点として扱い、自動テストにはしない |

### 2.3 基本設計との対応

| 基本設計の項目 | Phase 5 での具体化 |
| --- | --- |
| 13. テスト方針 | pytestのテストファイル、fixture、実行コマンド、期待結果を定義する |
| 13.1 テスト対象 | F-01〜F-10の主要処理をテストケースへ分解する |
| 13.2 テスト種別 | 単体、結合、異常系、セキュリティ確認をpytestで実行できるようにする |
| 14. 実装フェーズ | Phase 5 の完了条件を `pytest` の成功で判定できるようにする |

### 2.4 実装時の分割方針

Phase 5 はテスト対象が広いため、実装負荷を下げるために以下の2段階で進める。

| 区分 | 主な対象 | 目的 |
| --- | --- | --- |
| Phase 5-A | formatter、calculator、generator、writer、execution result、sampleモード結合テスト | APIキーなしで確認できる主要処理の回帰テストを先に整備する |
| Phase 5-B | settings、sample fetcher、HTTP Client、Provider、apiモード結合テスト、セキュリティ回帰テスト | 外部取得分岐と公開前の安全性を外部通信なしで検証する |

Phase 5-A 完了時点では、Provider系、apiモード、セキュリティ回帰テストが未完了でもよい。
Phase 5 全体の完了判定は、Phase 5-B まで完了した時点で行う。

## 3. テスト基本方針

### 3.1 外部通信に依存しない

Phase 5 のテストは、通常実行時に外部ネットワークへ接続しない。
RSSとマーケットAPIは、Providerに渡すHTTP取得関数を `monkeypatch` で差し替える。

| 対象 | テスト方針 |
| --- | --- |
| RSS取得 | `src.news.providers.rss.get_text` を差し替え、固定RSS XMLを返す |
| Alpha Vantage | `src.market.providers.alpha_vantage.get_json` を差し替え、固定JSONを返す |
| HTTP共通処理 | `requests.get` を差し替え、成功、HTTP失敗、タイムアウト、JSON不正を再現する |
| NewsAPI | Phase 4 の未対応スタブとして、通信せず警告を返すことのみを確認する |

### 3.2 ファイル出力は一時ディレクトリへ閉じ込める

テストで作成するレポート、ログ、一時JSONは `tmp_path` 配下に保存する。
既存の `morning-news/reports/`、`morning-news/logs/`、`sample_data/` は破壊的に変更しない。

| 出力 | 方針 |
| --- | --- |
| レポート | `tmp_path / "reports"` に出力する |
| ログ | `tmp_path / "logs"` に出力する |
| 一時JSON | `tmp_path / "sample_data"` に作成する |
| `.env` | 実ファイルを作らず `monkeypatch.setenv()` を基本にする |

### 3.3 検証は仕様ベースで行う

テストは内部実装の細かい書き方ではなく、要件と詳細設計で定義した入出力を検証する。
ただし、機密情報マスクや終了コードのように不具合時の影響が大きい箇所は、関数単位でも検証する。

### 3.4 テスト名は期待動作を表す

テスト関数名は `test_<対象>_<条件>_<期待結果>` 形式を基本とする。

例:

```python
def test_format_summary_truncates_text_with_ellipsis():
    ...

def test_main_returns_2_when_api_mode_fetches_no_external_data():
    ...
```

## 4. ファイル構成

Phase 5 では、既存の `morning-news/tests/` 配下を以下の構成にする。

```text
morning-news/
├── requirements.txt
├── requirements-dev.txt
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_settings.py
    │   ├── test_news_fetcher.py
    │   ├── test_news_formatter.py
    │   ├── test_market_fetcher.py
    │   ├── test_market_calculator.py
    │   ├── test_report_generator.py
    │   ├── test_report_writer.py
    │   ├── test_execution_result.py
    │   └── test_http_client.py
    ├── providers/
    │   ├── test_rss_provider.py
    │   ├── test_newsapi_provider.py
    │   └── test_alpha_vantage_provider.py
    ├── integration/
    │   ├── test_sample_mode.py
    │   └── test_api_mode.py
    └── security/
        └── test_secret_masking.py
```

### 4.1 追加・変更対象ファイル

| ファイル | 区分 | 役割 |
| --- | --- | --- |
| `requirements-dev.txt` | 追加 | pytestなどテスト実行用依存関係を記載する |
| `tests/conftest.py` | 追加 | 共通fixture、テスト用Settings、固定RSS/JSONを提供する |
| `tests/unit/test_settings.py` | 追加 | 設定読み込み、環境変数パース、Provider名解決を検証する |
| `tests/unit/test_news_fetcher.py` | 追加 | sampleニュースJSONの読み込み・検証を検証する |
| `tests/unit/test_news_formatter.py` | 追加 | 概要文整形の境界値を検証する |
| `tests/unit/test_market_fetcher.py` | 追加 | sampleマーケットJSONの読み込み・検証を検証する |
| `tests/unit/test_market_calculator.py` | 追加 | 前日比・変化率計算の境界値を検証する |
| `tests/unit/test_report_generator.py` | 追加 | Markdown生成、市況コメント、禁止表現不使用を検証する |
| `tests/unit/test_report_writer.py` | 追加 | レポート保存先生成と保存失敗時例外を検証する |
| `tests/unit/test_execution_result.py` | 追加 | 実行結果の件数、警告、エラー、サマリー文を検証する |
| `tests/unit/test_http_client.py` | 追加 | HTTP GET、リトライ、URLマスク、JSON解析失敗を検証する |
| `tests/providers/test_rss_provider.py` | 追加 | RSS正規化、重複排除、日時代替、警告を検証する |
| `tests/providers/test_newsapi_provider.py` | 追加 | NewsAPI未対応スタブの警告を検証する |
| `tests/providers/test_alpha_vantage_provider.py` | 追加 | Alpha Vantageレスポンス正規化とAPIキー未設定警告を検証する |
| `tests/integration/test_sample_mode.py` | 追加 | sampleモードの起動から保存までを検証する |
| `tests/integration/test_api_mode.py` | 追加 | モック外部データによるapiモードの保存、全取得失敗時終了コードを検証する |
| `tests/security/test_secret_masking.py` | 追加 | APIキーがログ・レポート・例外に出ないことを検証する |

### 4.2 依存関係

テスト実行用の依存関係は `requirements-dev.txt` に追加する。
実行環境を単純にしたい場合は、Phase 6 のREADMEで `requirements.txt` と `requirements-dev.txt` の両方をインストールする手順を示す。

```text
-r requirements.txt
pytest>=8.0.0
```

## 5. テスト実行コマンド

### 5.1 全テスト

```bash
python3 -m pytest
```

### 5.2 詳細出力

```bash
python3 -m pytest -v
```

### 5.3 失敗時に早期停止

```bash
python3 -m pytest -x
```

### 5.4 特定カテゴリのみ

```bash
python3 -m pytest tests/unit
python3 -m pytest tests/providers
python3 -m pytest tests/integration
python3 -m pytest tests/security
```

### 5.5 READMEに載せる標準確認コマンド

Phase 6 のREADMEでは、以下を標準の確認コマンドとして案内する。

```bash
python3 -m pytest
APP_MODE=sample python3 main.py
```

## 6. 共通fixture設計

### 6.1 `sample_settings`

`load_settings()` の戻り値と同等の `Settings` を生成する。
出力先は `tmp_path` 配下に差し替える。

| 項目 | 値 |
| --- | --- |
| `app_mode` | `sample` |
| `report_dir` | `tmp_path / "reports"` |
| `log_dir` | `tmp_path / "logs"` |
| `news_jp_path` | テスト用 `news_jp.json` |
| `news_global_path` | テスト用 `news_global.json` |
| `market_path` | テスト用 `market.json` |
| `news_limit` | `5` |
| `summary_max_length` | `120` |
| `timezone` | `Asia/Tokyo` |

### 6.2 `api_settings`

`APP_MODE=api` 用の `Settings` を生成する。
RSS URLとマーケットAPI設定は、実在URLではなくテスト用URLを入れる。

| 項目 | 値 |
| --- | --- |
| `app_mode` | `api` |
| `news_provider` | `rss` |
| `news_jp_rss_urls` | `("https://example.com/jp.xml",)` |
| `news_global_rss_urls` | `("https://example.com/global.xml",)` |
| `market_provider` | `alpha_vantage` または `sample` |
| `market_api_key` | `test-secret-key` |
| `market_api_endpoint` | `https://example.com/query` |

### 6.3 `report_data_factory`

`generate_report()` 用の最小 `ReportData` を返す。
各テストでは、必要な項目だけ上書きして利用する。

必須キー:

- `generated_at`
- `mode`
- `news_domestic`
- `news_global`
- `markets`
- `comments`
- `warnings`
- `errors`
- `disclaimer`
- `execution_summary`

### 6.4 `fake_rss_text`

RSS Providerのテストで使う固定RSS XMLを返す。
以下のケースを含める。

| ケース | 内容 |
| --- | --- |
| 正常entry | title, link, pubDate, description を持つ |
| HTML概要 | description にHTMLタグを含む |
| 追跡クエリ | URLに `utm_source` を含む |
| 日時欠損 | pubDate がないentry |
| 必須欠損 | title または link がないentry |

### 6.5 `fake_alpha_vantage_json`

Alpha Vantage Providerのテストで使う固定JSONを返す。

| 種別 | JSON |
| --- | --- |
| `GLOBAL_QUOTE` 正常 | `Global Quote` に `05. price` と `08. previous close` を含む |
| `GLOBAL_QUOTE` 差分補完 | `08. previous close` 欠損、`09. change` あり |
| `FX_DAILY` 正常 | `Time Series FX (Daily)` に2日分の終値を含む |
| APIエラー | `Note` または `Error Message` を含む |
| 形式不正 | 必須キーがない |

## 7. 単体テスト設計

### 7.1 `src/news/formatter.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `format_summary()` | 改行、タブ、連続空白を含む | 半角スペース1つに正規化される |
| `format_summary()` | 前後空白を含む | 前後空白が削除される |
| `format_summary()` | `None` | `概要はありません。` |
| `format_summary()` | 空文字 | `概要はありません。` |
| `format_summary()` | 上限以内 | 元の内容が返る |
| `format_summary()` | `max_length=120` で上限超過 | 117文字 + `...` になる |
| `format_summary()` | `max_length=4` | 1文字 + `...` になる |
| `format_summary()` | `max_length=3` | `...` になる |
| `format_summary()` | `max_length=2` | `..` になる |
| `format_summary()` | `max_length=0` | `SummaryFormatError` |
| `format_news_items()` | 複数ニュース | 各項目に `short_summary` が追加される |
| `format_news_items()` | 入力list | 元のdictが破壊的変更されない |

### 7.2 `src/market/calculator.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `calculate_change()` | `current_value=110`, `previous_close=100` | `change=10`, `change_rate=10.0` |
| `calculate_change()` | `current_value=90`, `previous_close=100` | `change=-10`, `change_rate=-10.0` |
| `calculate_change()` | `current_value=100`, `previous_close=100` | `change=0`, `change_rate=0.0` |
| `calculate_change()` | 小数値 | 小数第2位へ丸められる |
| `calculate_change()` | `previous_close=0` | `(None, None)` |
| `calculate_change()` | `current_value` が文字列 | `MarketCalculationError` |
| `calculate_change()` | `previous_close` が `bool` | `MarketCalculationError` |
| `calculate_market_changes()` | 正常items | `change` と `change_rate` が追加される |
| `calculate_market_changes()` | `previous_close` 欠損 | `MarketCalculationError` |

### 7.3 `src/report/generator.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `generate_news_section()` | itemsあり | タイトル、配信元、公開日時、概要、URLが出る |
| `generate_news_section()` | itemsなし | `取得できませんでした。` が出る |
| `generate_market_section()` | marketsあり | Markdown表が生成される |
| `generate_market_section()` | market値が `None` | `N/A` が出る |
| `generate_market_comments()` | 正の変化率 | `上昇傾向です。` |
| `generate_market_comments()` | 負の変化率 | `下落傾向です。` |
| `generate_market_comments()` | 0 | `大きな変動は見られません。` |
| `generate_market_comments()` | `None` | `変化率を計算できませんでした。` |
| `generate_report()` | 必須キーあり | 6つの主要セクションが出る |
| `generate_report()` | warningsあり | `### 警告` が出る |
| `generate_report()` | 必須キー欠損 | `ReportGenerationError` |
| `generate_report()` | 市況コメント | 禁止表現が含まれない |

### 7.4 `src/report/writer.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `build_report_path()` | `date(2026, 5, 25)` | `reports/2026-05-25.md` |
| `build_report_path()` | 文字列日付 | `reports/<文字列>.md` |
| `write_report()` | 保存先ディレクトリなし | ディレクトリ作成後に保存される |
| `write_report()` | 書き込み失敗 | `ReportWriteError` |

### 7.5 `src/utils/execution_result.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `create_execution_result()` | 初期化 | `status=running`、件数0 |
| `set_count()` | 件数設定 | 指定キーの件数が更新される |
| `record_warning()` | 警告追加 | `warnings` 配列と件数が更新される |
| `record_error()` | エラー追加 | `errors` 配列と件数が更新される |
| `finish_execution()` | 終了 | `status` と `ended_at` が更新される |
| `build_summary_message()` | 件数あり | `status`、`warnings`、`errors`、取得件数を含む |

### 7.6 `src/config/settings.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `load_settings()` | 環境変数なし | `app_mode=sample` |
| `load_settings()` | `APP_MODE=api` | `app_mode=api` |
| `load_settings()` | 不正な `APP_MODE` | `sample` にフォールバックし警告が入る |
| `load_settings()` | `NEWS_PROVIDER=newsapi` | `news_provider=newsapi` |
| `load_settings()` | 不正な `NEWS_PROVIDER` | `rss` にフォールバックし警告が入る |
| `load_settings()` | `NEWS_RSS_URLS` | 国内RSSのフォールバックとして使われる |
| `load_settings()` | 不正URL混在 | 不正URLを除外し警告が入る |
| `load_settings()` | `MARKET_PROVIDER=alphavantage` | `alpha_vantage` に正規化される |
| `load_settings()` | `MARKET_API_KEY` と `ALPHA_VANTAGE_API_KEY` | `MARKET_API_KEY` を優先する |
| `load_settings()` | `SUMMARY_MAX_LENGTH=0` | `ConfigError` |
| `load_settings()` | `REQUEST_RETRY_COUNT=-1` | 既定値へフォールバックし警告が入る |

### 7.7 `src/news/fetcher.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `load_news_items()` | 正常JSON | NewsItem配列を返す |
| `load_news_items()` | ファイルなし | `DataLoadError` |
| `load_news_items()` | JSON不正 | `DataLoadError` |
| `load_news_items()` | top-levelがobject以外 | `DataValidationError` |
| `load_news_items()` | `items` が配列以外 | `DataValidationError` |
| `load_news_items()` | 必須項目欠損 | `DataValidationError` |
| `load_news_items()` | `region` 不正 | `DataValidationError` |
| `fetch_sample_news()` | `news_limit=2` | 国内・海外それぞれ2件まで返す |
| `fetch_news_for_mode()` | `sample` | sample JSONから取得する |
| `fetch_news_for_mode()` | `api` | Provider取得関数へ委譲する |

### 7.8 `src/market/fetcher.py`

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `load_market_items()` | 正常JSON | MarketItem配列を返す |
| `load_market_items()` | ファイルなし | `DataLoadError` |
| `load_market_items()` | JSON不正 | `DataLoadError` |
| `load_market_items()` | `items` が配列以外 | `DataValidationError` |
| `load_market_items()` | `symbol` 欠損 | `DataValidationError` |
| `fetch_api_markets()` | `MARKET_PROVIDER=sample` | sampleマーケットと警告を返す |
| `fetch_api_markets()` | `MARKET_PROVIDER=alpha_vantage` | Alpha Vantage Providerへ委譲する |
| `fetch_api_markets()` | 未対応Provider | 空配列と警告を返す |

## 8. Provider・HTTPテスト設計

### 8.1 RSS Provider

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `fetch_rss_news()` | URL未設定 | 空配列と未設定警告 |
| `fetch_rss_news()` | feedparser未インストール相当 | 空配列と警告 |
| `fetch_rss_news()` | 正常RSS | `NewsItem` に正規化される |
| `fetch_rss_news()` | HTML概要 | タグ除去済みsummaryになる |
| `fetch_rss_news()` | 日時欠損 | 取得日時が入り警告が返る |
| `fetch_rss_news()` | title欠損entry | entryをスキップし警告が返る |
| `fetch_rss_news()` | 重複URL | 1件に重複排除される |
| `fetch_rss_news()` | `utm_` クエリ違い | 同一URLとして重複排除される |
| `fetch_rss_news()` | HTTP取得失敗 | 該当feedをスキップし警告が返る |
| `fetch_rss_news()` | limit指定 | 指定件数以内になる |

### 8.2 NewsAPI Provider

Phase 5 では、NewsAPI の本格的な取得処理は実装対象外とする。
テスト対象は、未対応スタブが外部通信を行わず、空配列と警告を返すことに限定する。
NewsAPI の実Provider化と取得テストは後続任意タスクで扱う。

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `fetch_newsapi_news()` | domestic | 空配列と未対応警告 |
| `fetch_newsapi_news()` | global | 空配列と未対応警告 |
| `fetch_newsapi_news()` | 任意region | 外部通信を行わない |

### 8.3 Alpha Vantage Provider

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `fetch_alpha_vantage_markets()` | APIキー未設定 | 空配列と警告 |
| `_normalize_quote_response()` | 正常 `Global Quote` | `current_value` と `previous_close` が入る |
| `_normalize_quote_response()` | `previous close` 欠損、`change` あり | `previous_close` を補完する |
| `_normalize_quote_response()` | API制限Note | `ExternalDataError` |
| `_normalize_fx_daily_response()` | 2日分の為替時系列 | 現在値と前日終値が入る |
| `_normalize_fx_daily_response()` | 1日分のみ | `ExternalDataError` |
| `_fetch_target()` | indexでProviderシンボル未設定 | recoverableな `ExternalDataError` |
| `_fetch_target()` | fxで通貨ペア不足 | recoverableな `ExternalDataError` |
| `fetch_alpha_vantage_markets()` | 一部指標失敗 | 成功分と警告を返す |
| `fetch_alpha_vantage_markets()` | 例外メッセージにAPIキー | 警告内では `***` にマスクされる |
| `fetch_alpha_vantage_markets()` | `MARKET_REQUEST_INTERVAL_SECONDS=2` | 複数指標の取得間で `sleep(2)` が呼ばれる |

### 8.4 HTTP Client

| テスト対象 | 条件 | 期待結果 |
| --- | --- | --- |
| `sanitize_url()` | `apikey=secret` | `apikey=***` |
| `sanitize_url()` | `token=secret` | `token=***` |
| `sanitize_url()` | 通常クエリ | 値を維持する |
| `get_text()` | HTTP 200 | response.textを返す |
| `get_json()` | HTTP 200 JSON | response.json()を返す |
| `get_json()` | JSON解析失敗 | `ExternalDataError` |
| `_request()` | 500後200 | リトライ後成功 |
| `_request()` | 404 | `ExternalFetchError` |
| `_request()` | Timeout | `ExternalFetchError` |
| `_request()` | requests未インストール相当 | `ExternalFetchError` |

## 9. 結合テスト設計

### 9.1 sampleモード

`tests/integration/test_sample_mode.py` では、`APP_MODE=sample` 相当の設定で、起動からレポート保存までを検証する。

| テスト内容 | 期待結果 |
| --- | --- |
| `main.main()` をsample設定で実行する | 終了コード `0` |
| レポート出力先を `tmp_path` にする | `YYYY-MM-DD.md` が作成される |
| ログ出力先を `tmp_path` にする | `app.log` が作成される |
| レポート本文を読む | 国内ニュース、海外ニュース、マーケット情報、市況コメント、注意事項が含まれる |
| ログ本文を読む | `F-01`〜`F-10` の主要ログが含まれる |
| 再実行する | 同一ファイルが上書きされ、終了コード `0` |

### 9.2 apiモード

`tests/integration/test_api_mode.py` では、外部通信関数をモックして `APP_MODE=api` の分岐を検証する。

| テスト内容 | 期待結果 |
| --- | --- |
| RSSとマーケットAPIが成功 | レポート保存まで完了し終了コード `0` |
| RSSのみ成功、マーケットAPIキー未設定 | 警告付きで終了コード `0` |
| RSS未設定、MARKET_PROVIDER=sample | 警告付きで終了コード `0` |
| NewsAPI provider指定 | 未対応警告が出て外部NewsAPIへ通信しない |
| 外部データが全件0件 | レポート保存せず終了コード `2` |
| APIキーを含む例外 | ログとレポートにキー値が含まれない |

### 9.3 `build_report_data()` の結合確認

`main.py` の `build_report_data()` は、取得、整形、計算、コメント生成、警告集計を接続するため、個別に検証する。

| 条件 | 期待結果 |
| --- | --- |
| summary空のニュースあり | `warnings` に概要欠損警告が入る |
| `previous_close=0` のマーケットあり | `warnings` に計算不可警告が入る |
| apiモードで全データ空 | `DataLoadError` |
| 市況データあり | `comments` 件数がmarkets件数と一致する |

## 10. 異常系テスト設計

### 10.1 sample JSON異常

| 条件 | 期待結果 |
| --- | --- |
| `news_jp.json` が存在しない | `DataLoadError`、結合時は終了コード `2` |
| `news_global.json` が壊れたJSON | `DataLoadError`、結合時は終了コード `2` |
| `market.json` の `items` が配列でない | `DataValidationError`、結合時は終了コード `2` |
| ニュース必須項目欠損 | 欠損項目名を含む `DataValidationError` |
| マーケット数値項目が文字列 | 計算時に `MarketCalculationError`、結合時は終了コード `1` |

### 10.2 設定異常

| 条件 | 期待結果 |
| --- | --- |
| `SUMMARY_MAX_LENGTH=0` | `ConfigError`、終了コード `1` |
| `NEWS_LIMIT=abc` | 既定値にフォールバックし警告 |
| `REQUEST_TIMEOUT_SECONDS=0` | 既定値にフォールバックし警告 |
| `REQUEST_RETRY_COUNT=-1` | 既定値にフォールバックし警告 |
| `MARKET_REQUEST_INTERVAL_SECONDS=-1` | 既定値にフォールバックし警告 |
| 不正RSS URL | 該当URLを除外し警告 |

### 10.3 保存異常

| 条件 | 期待結果 |
| --- | --- |
| レポート保存先が書き込めない | `ReportWriteError`、終了コード `1` |
| report path生成に不正値 | `ReportWriteError` |
| ログファイル初期化失敗 | 標準出力のみで継続できる |

## 11. セキュリティ回帰テスト設計

### 11.1 禁止する出力

以下の値は、ログ、レポート、警告、例外メッセージに出力しない。

| 値 | 例 |
| --- | --- |
| APIキー | `test-secret-key` |
| 認証クエリ | `apikey=test-secret-key` |
| 認証トークン | `token=test-secret-key` |
| `.env` 全文 | `.env` の内容全体 |
| HTTPヘッダー | `Authorization` |

### 11.2 テスト観点

| テスト内容 | 期待結果 |
| --- | --- |
| `sanitize_url()` に認証URLを渡す | 秘密値が `***` に置換される |
| Alpha Vantage例外にAPIキーが含まれる | warningsでは `***` に置換される |
| `generate_report()` のwarningsに秘密値がない | レポート本文に秘密値がない |
| `logs/app.log` を読む | 秘密値がない |
| News/RSS URLに通常クエリあり | 認証キー以外は必要に応じて保持される |

## 12. テストデータ設計

### 12.1 既存データの利用

既存の `sample_data/` と、Phase 5 の異常系・境界値テスト用に追加する `sample_data_edge/` をテストで利用する。
ただし、テスト中に内容を変更しない。

| ディレクトリ | 用途 |
| --- | --- |
| `sample_data/` | 正常系sampleモードの確認 |
| `sample_data_edge/` | 欠損、空概要、数値不正など境界値確認 |

`sample_data_edge/` は通常実行では使用しない。
pytest実行時のみ参照し、公開後の利用者が sample モードを確認するときは `sample_data/` を使う。

### 12.2 一時データの生成

ファイル欠損、JSON不正、保存失敗など、リポジトリ内の実ファイルを壊す必要があるケースは `tmp_path` に一時ファイルを生成して検証する。

## 13. 実装手順

Phase 5 は、以下の順番で実装・確認する。

### 13.1 Phase 5-A: sampleモード中心のpytest

1. `requirements-dev.txt` を追加し、`pytest` を記載する。
2. `tests/conftest.py` を追加し、Settings、ReportData、一時出力先のfixtureを定義する。
3. `tests/unit/test_news_formatter.py` を追加し、概要文整形の境界値を検証する。
4. `tests/unit/test_market_calculator.py` を追加し、前日比・変化率計算を検証する。
5. `tests/unit/test_report_generator.py` を追加し、Markdown生成、市況コメント、禁止表現不使用を検証する。
6. `tests/unit/test_report_writer.py` を追加し、レポート保存先生成と保存失敗時例外を検証する。
7. `tests/unit/test_execution_result.py` を追加し、実行結果の件数、警告、エラー、サマリー文を検証する。
8. `tests/integration/test_sample_mode.py` を追加し、sampleモードのレポート生成を検証する。
9. `python3 -m pytest tests/unit/test_news_formatter.py tests/unit/test_market_calculator.py tests/unit/test_report_generator.py tests/unit/test_report_writer.py tests/unit/test_execution_result.py tests/integration/test_sample_mode.py` を実行し、Phase 5-A のテストが成功することを確認する。
10. `APP_MODE=sample python3 main.py` を実行し、既存の手動実行が壊れていないことを確認する。

### 13.2 Phase 5-B: Provider・apiモード・セキュリティ回帰テスト

1. `tests/unit/test_news_fetcher.py` と `tests/unit/test_market_fetcher.py` を追加し、sample JSON検証を自動化する。
2. `tests/unit/test_settings.py` を追加し、環境変数と設定値のパースを検証する。
3. `tests/unit/test_http_client.py` を追加し、HTTP共通処理とURLマスクを検証する。
4. `tests/providers/test_rss_provider.py` を追加し、RSS正規化と警告を検証する。
5. `tests/providers/test_alpha_vantage_provider.py` を追加し、マーケットAPIレスポンス正規化とAPIキー未設定警告を検証する。
6. `tests/providers/test_newsapi_provider.py` を追加し、未対応スタブの動作のみを検証する。
7. `tests/integration/test_api_mode.py` を追加し、モック外部データによるapiモードを検証する。
8. `tests/security/test_secret_masking.py` を追加し、機密情報が出力されないことを検証する。
9. `python3 -m pytest` を実行し、全テストが成功することを確認する。

## 14. 受け入れ条件

Phase 5 は、以下を満たしたら完了とする。

- `python3 -m pytest` が終了コード `0` で完了する。
- 外部ネットワーク、実APIキー、実 `.env` に依存せずテストが実行できる。
- 概要文整形、変化率計算、Markdown生成、市況コメント生成の単体テストがある。
- sampleニュース、sampleマーケットの正常系・異常系テストがある。
- RSS Providerは、正常RSS、日時欠損、必須項目欠損、重複URL、HTTP失敗をテストしている。
- Alpha Vantage Providerは、APIキー未設定、正常レスポンス、APIエラー、部分失敗、キー値マスクをテストしている。
- `APP_MODE=sample` の結合テストで、レポート保存とログ出力を確認できる。
- `APP_MODE=api` の結合テストで、モック外部データによる成功と全取得失敗時の終了コード `2` を確認できる。
- `SUMMARY_MAX_LENGTH=0`、JSON欠損、マーケット数値不正、保存失敗の異常系がテストされている。
- APIキー、トークン、未マスク認証URLがログ・レポート・警告に出ないことをテストしている。
- テスト実行中に既存の `reports/`、`logs/`、`sample_data/` を破壊的に変更しない。
- READMEで案内できるテスト実行手順が確定している。

## 15. 次フェーズで追加するもの

Phase 5 では、主要処理の自動テストを整備する。
以下は次フェーズで追加する。

| フェーズ | 追加内容 |
| --- | --- |
| Phase 6 | README、`.env.example`、サンプルレポート、公開前チェック、実行手順整備 |
| 後続任意 | GitHub Actions、カバレッジ閾値、実APIを使う任意E2Eテスト、定時実行手順の詳細化 |

Phase 5 完了時点では、実APIを使う自動E2E、定時実行、通知、Web UI、AI要約、ニュース本文全文取得、自動売買・投資助言は実装しない。
