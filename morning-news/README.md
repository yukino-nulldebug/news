# Morning News

ニュースとマーケット情報を収集し、日次Markdownレポートを生成するCLIバッチアプリです。

`sample` モードではAPIキーなしで動作確認できます。ポートフォリオ確認では、まず `sample` モードを使ってください。
`api` モードは任意機能です。APIキーや外部サービスの状態により、取得結果が変わる場合があります。

## 主な機能

- 国内ニュース、海外ニュースの取得
- ニュース概要文の整形
- 日経平均、S&P500、USD/JPY相当のマーケット情報取得
- 前日比、変化率の計算
- 中立的な市況コメント生成
- Markdownレポート保存
- ログ出力
- APIキーなしの `sample` モード
- pytestによる主要処理のテスト

## ディレクトリ構成

```text
morning-news/
├── main.py
├── src/
│   ├── config/
│   ├── news/
│   ├── market/
│   ├── report/
│   └── utils/
├── sample_data/
├── sample_data_edge/
├── reports/
├── logs/
└── tests/
```

| ディレクトリ | 説明 |
| --- | --- |
| `src/config/` | 設定、環境変数、実行モードを管理します。 |
| `src/news/` | ニュース取得、Provider、概要文整形を行います。 |
| `src/market/` | マーケット取得、Provider、変化率計算を行います。 |
| `src/report/` | Markdown生成と保存を行います。 |
| `src/utils/` | ログ、例外、HTTP、実行結果集計を行います。 |
| `sample_data/` | APIキーなしで動かす正常系サンプルです。 |
| `sample_data_edge/` | pytestで使う境界値・異常系サンプルです。 |
| `reports/` | 生成されたレポートとサンプルレポートを置きます。 |
| `logs/` | 実行ログを出力します。 |
| `tests/` | pytestテストを置きます。 |

## 必要環境

| 項目 | 内容 |
| --- | --- |
| Python | Python 3.10以上を推奨 |
| OS | macOS / Linux / Windows のローカル環境 |
| 外部APIキー | `sample` モードでは不要 |
| ネットワーク | `sample` モードと単体テストでは不要。`api` モードでは必要 |

## セットアップ

```bash
cd morning-news
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
```

Windowsでは仮想環境の有効化コマンドだけ次のように読み替えてください。

```bash
.venv\Scripts\activate
```

## sampleモードで実行する

APIキーなしで最初に確認する手順です。

```bash
APP_MODE=sample python3 main.py
```

環境変数を指定しない場合も `sample` で起動できます。

```bash
python3 main.py
```

期待結果:

- `reports/YYYY-MM-DD.md` が作成されます。
- `logs/app.log` に実行結果が出力されます。
- レポートに国内ニュース、海外ニュース、マーケット情報、市況コメント、注意事項が含まれます。

## apiモード（任意）でRSSニュースを取得する

`api` モードは任意機能です。APIキーや外部サービスの状態により、取得結果が変わる場合があります。
ポートフォリオ確認では `sample` モードを推奨します。

マーケットAPIキーがない場合は、`MARKET_PROVIDER=sample` を使うとRSSニュースだけ実データにできます。

```env
APP_MODE=api
NEWS_PROVIDER=rss
NEWS_RSS_URLS=https://example.com/rss
MARKET_PROVIDER=sample
```

実行:

```bash
python3 main.py
```

補足:

- `NEWS_RSS_URLS` は国内RSSのフォールバックとして扱います。
- 国内・海外を分けたい場合は `NEWS_JP_RSS_URLS` と `NEWS_GLOBAL_RSS_URLS` を使います。
- `MARKET_PROVIDER=sample` は、apiモードでニュースだけ実データにし、マーケットはsampleデータを使う確認用設定です。

## Alpha Vantage（任意）でマーケット情報を取得する

Alpha Vantage連携は任意機能です。sampleモードの動作確認には不要です。

```env
APP_MODE=api
NEWS_PROVIDER=rss
NEWS_RSS_URLS=https://example.com/rss
MARKET_PROVIDER=alpha_vantage
MARKET_API_KEY=your_api_key
MARKET_SYMBOL_NIKKEI225=
MARKET_SYMBOL_SP500=
MARKET_FX_BASE=USD
MARKET_FX_QUOTE=JPY
```

注意点:

- `MARKET_API_KEY` は `.env` に設定し、Gitにコミットしないでください。
- `ALPHA_VANTAGE_API_KEY` も互換名として利用できますが、READMEでは `MARKET_API_KEY` を推奨します。
- 無料枠や取得可能シンボルは外部サービス側の仕様に依存します。
- APIキーや認証URLはログ・レポートへ出力しない設計です。

## テストを実行する

```bash
python3 -m pytest
```

カテゴリ別に確認する場合:

```bash
python3 -m pytest tests/unit
python3 -m pytest tests/providers
python3 -m pytest tests/integration
python3 -m pytest tests/security
```

期待結果:

- 全テストが成功します。
- テストは実APIキーと外部通信に依存しません。

## 出力されるレポート

日次実行では次のファイルが生成されます。

```text
reports/YYYY-MM-DD.md
```

公開用の固定サンプルレポートは次のファイルです。

```text
reports/sample-report.md
```

README本文に長いレポート全文は貼らず、`reports/sample-report.md` を出力例として参照してください。

## ログ

実行ログは次のファイルに出力されます。

```text
logs/app.log
```

ログには、機能ID、処理名、件数、警告、エラー概要を出力します。
APIキー、認証URL、`.env` 全文、認証ヘッダーは出力しない方針です。

## 環境変数

主要な環境変数は次の通りです。詳細な設定例は `.env.example` を参照してください。

| 変数 | 既定値 | 説明 |
| --- | --- | --- |
| `APP_MODE` | `sample` | `sample` または `api` |
| `NEWS_PROVIDER` | `rss` | ニュースProvider |
| `NEWS_RSS_URLS` | 空 | 国内RSSのフォールバックURL |
| `NEWS_JP_RSS_URLS` | 空 | 国内RSS URL |
| `NEWS_GLOBAL_RSS_URLS` | 空 | 海外RSS URL |
| `MARKET_PROVIDER` | `alpha_vantage` | マーケットProvider |
| `MARKET_API_KEY` | 空 | マーケットAPIキー |
| `REPORT_DIR` | `reports` | レポート出力先 |
| `LOG_DIR` | `logs` | ログ出力先 |
| `NEWS_LIMIT` | `5` | 国内/海外ニュースの最大件数 |
| `SUMMARY_MAX_LENGTH` | `120` | 概要文の最大文字数 |
| `REQUEST_TIMEOUT_SECONDS` | `10` | 外部取得タイムアウト |
| `REQUEST_RETRY_COUNT` | `1` | 外部取得リトライ回数 |

`.env.example` をコピーして `.env` を作成できます。

```bash
cp .env.example .env
```

`.env` は `.gitignore` で管理対象外にしています。

## サンプルデータ

| パス | 用途 |
| --- | --- |
| `sample_data/news_jp.json` | 国内ニュースの正常系サンプル |
| `sample_data/news_global.json` | 海外ニュースの正常系サンプル |
| `sample_data/market.json` | マーケット情報の正常系サンプル |
| `sample_data_edge/` | pytestで使う境界値・異常系データ |

`sample_data_edge/` は Phase 5 の異常系・境界値テスト用に追加したテストデータディレクトリです。
通常実行では使用せず、pytest実行時のみ参照します。

サンプルニュースは実在記事の本文や有料記事本文をコピーせず、ポートフォリオ確認用の架空データとして扱います。

## 注意事項

- 本アプリは情報提供を目的とします。
- 市況コメントは投資助言ではありません。
- 売買推奨、自動売買、利益保証は行いません。
- ニュース本文全文、有料記事、ログイン後ページ本文は取得しません。
- `.env` とAPIキーはGitにコミットしないでください。
- 外部APIの無料枠、利用規約、取得可能データは利用者が確認してください。

## 設計ドキュメント

| ドキュメント | パス |
| --- | --- |
| 要件定義 | `../docs/requirements/要件定義.md` |
| 基本設計 | `../docs/basic-design/基本設計.md` |
| 詳細設計 Phase 1 | `../docs/detail-design/詳細設計Phase 1.md` |
| 詳細設計 Phase 2 | `../docs/detail-design/詳細設計Phase 2.md` |
| 詳細設計 Phase 3 | `../docs/detail-design/詳細設計Phase 3.md` |
| 詳細設計 Phase 4 | `../docs/detail-design/詳細設計Phase 4.md` |
| 詳細設計 Phase 5 | `../docs/detail-design/詳細設計Phase 5.md` |
| 詳細設計 Phase 6 | `../docs/detail-design/詳細設計Phase 6.md` |
