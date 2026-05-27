# Morning News

朝の情報収集では、ニュースサイト、為替、株価などを個別に確認する必要があり、必要な情報だけを短時間で把握しづらいことがあります。

Morning News は、RSS/APIから取得した国内外ニュースとマーケット情報をMarkdownレポートとして構造化し、朝の情報収集を効率化するためのPython製CLIバッチアプリです。

ポートフォリオとしては、外部APIに依存する小さなCLIバッチを、再現性、失敗時の継続、ログ、秘密情報保護、テストまで含めて公開できる形に設計・実装した点を見せることを目的にしています。

## 開発背景

ニュースやSNSから大量の情報が流れる一方で、毎朝確認したい情報は「国内外の主要ニュース」「為替や株価の変化」「前日からの大きな流れ」に絞られます。

このアプリでは、大量のニュースを集めるのではなく、RSS/APIで取得できるタイトル、URL、配信元、公開日時、概要文を整理し、マーケット情報と同じMarkdownにまとめます。ニュースという定性情報と、価格変動という定量情報を同じファイルに残すことで、後から見返しやすい形にしました。

UIは作り込まず、CLIバッチとMarkdown出力に絞っています。これは、GitHubやObsidianで確認しやすく、APIキーなしでも `sample` モードで再現できることを優先したためです。

## 解決したい課題

- ニュース、為替、株価を複数サイトで確認する手間がある。
- 朝の限られた時間で、必要な情報だけを短く把握しづらい。
- APIキーがない閲覧者に、アプリの動作を再現してもらいづらい。
- 外部API連携、ログ、例外処理、テストまで含めた実装プロセスを見せづらい。

## このプロジェクトで示すこと

- 再現性: `sample` / `api` を分け、APIキーがない第三者でも確認できる経路を用意した。
- 外部依存の扱い: timeout、retry、Provider分岐、マーケットAPIの連続取得間隔を設定化した。
- 失敗設計: 欠損値は `N/A` と警告で継続し、外部データ全滅は終了コード `2` で明示した。
- 公開安全性: `.env` をGit管理外にし、APIキー、トークン、認証ヘッダーをログ・レポートに出さない。
- 品質保証: 取得、整形、計算、保存、秘密情報マスクをpytestとGitHub Actionsで回帰確認する。
- レビュー改善: 見つかった仕様の穴を、コード修正だけでなく回帰テストまで追加して塞いだ。
- AI協働: AIで要件整理、実装案、コードレビューを加速し、仕様判断・安全判断・最終差分は自分で確認した。

## AI活用の進め方

このプロジェクトでは、AIを設計整理、実装案の作成、コードレビュー、テスト観点の洗い出しに使いました。

ただし、AIの出力をそのまま採用するのではなく、次の流れで確認しています。

| 工程 | AIで加速したこと | 自分で判断・確認したこと |
| --- | --- | --- |
| 要件整理 | 課題、機能、受け入れ条件の分解 | `sample` モードを標準確認経路にする判断 |
| 実装 | 設定、Provider、レポート生成、pytestの実装案 | 既存構造に合う形だけ採用し、差分を確認 |
| レビュー | 仕様漏れ、セキュリティ、テスト不足の指摘 | 外部データ全滅時の終了コードや秘密情報マスクを修正 |
| 検証 | テスト観点とREADME構成の提案 | 回帰テストを追加し、`pytest` で確認 |

## 開発プロセス

主な制作期間は **2026-05-15 から 2026-05-27** です。要件定義と設計資料を先に作り、その後に段階的に実装とテストを追加しました。

| 日付 | 内容 | 関連コミット例 |
| --- | --- | --- |
| 2026-05-15 | 要件定義とスコープ整理 | `c5bda11` |
| 2026-05-16〜2026-05-18 | 基本設計、HTMLレビュー資料、詳細設計Phase 1 | `2a61570`, `1748e1c`, `144a18e` |
| 2026-05-19〜2026-05-23 | sample実行、ログ、例外処理、概要整形、変化率計算 | `a057407`, `45f9bc4`, `fc24181`, `44d5349` |
| 2026-05-24 | RSS/APIモード、`.env`、HTTP共通処理、Alpha Vantage連携 | `1ae2c15` |
| 2026-05-25〜2026-05-26 | 詳細設計Phase 5/6、pytest、README、公開準備 | `cf85e46`, `8337379`, `05d2568` |
| 2026-05-27 | マーケットAPI取得間隔、CI、ポートフォリオ見せ方改善 | `0675ce7` |

## 主な機能

- 国内ニュース、海外ニュースの取得
- RSSフィードの正規化と重複URLの除外
- ニュース概要文の整形
- 日本市場参考指標、米国市場参考指標、USD/JPY相当のマーケット情報取得
- 前日比、変化率の計算
- 欠損したマーケット値の `N/A` 表示と警告記録
- 投資助言にならない中立的な市況コメント生成
- Markdownレポート保存
- 標準出力と `logs/app.log` へのログ出力
- APIキーなしで動く `sample` モード
- pytestとGitHub Actionsによる自動テスト

## 技術スタック

| 区分 | 技術 | 用途 |
| --- | --- | --- |
| 言語 | Python 3.10+ | CLIバッチ、ファイル出力、データ整形 |
| HTTP | requests | RSS/API取得 |
| RSS解析 | feedparser | RSS/Atomフィード解析 |
| 環境変数 | python-dotenv | `.env` 読み込み |
| レポート | Markdown | GitHub、Obsidian、ローカル確認向け出力 |
| ログ | logging | 実行結果、警告、エラーの記録 |
| テスト | pytest | 単体・結合・Provider・セキュリティ回帰 |
| CI | GitHub Actions | push / pull request時のテスト実行 |

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
| `reports/` | 生成されたレポートと公開用サンプルレポートを置きます。 |
| `tests/` | pytestテストを置きます。 |

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

`sample` モードは、APIキーなしでポートフォリオ閲覧者が動作確認するためのモードです。通常の確認では最初にこちらを使ってください。

```bash
APP_MODE=sample python3 main.py
```

環境変数を指定しない場合も `sample` で起動します。

```bash
python3 main.py
```

期待結果:

- `reports/YYYY-MM-DD.md` が作成されます。
- `logs/app.log` に実行結果が出力されます。
- レポートに国内ニュース、海外ニュース、マーケット情報、市況コメント、注意事項が含まれます。

## apiモードでRSSニュースを取得する

`api` モードは任意機能です。APIキーや外部サービスの状態により取得結果が変わります。ポートフォリオ確認では `sample` モードを推奨します。

マーケットAPIキーがない場合は、`MARKET_PROVIDER=sample` を使うとRSSニュースだけ実データにできます。

```env
APP_MODE=api
NEWS_PROVIDER=rss
NEWS_RSS_URLS=https://example.com/rss
MARKET_PROVIDER=sample
```

```bash
python3 main.py
```

補足:

- `NEWS_RSS_URLS` は国内RSSのフォールバックとして扱います。
- 国内・海外を分けたい場合は `NEWS_JP_RSS_URLS` と `NEWS_GLOBAL_RSS_URLS` を使います。
- `NEWS_PROVIDER=newsapi` は拡張口のみ用意しており、現時点では外部News APIへ通信せず未対応警告を返します。
- `APP_MODE=api` で外部取得が全滅した場合、黙って `sample` データへ切り替えず、終了コード `2` で失敗を明示します。

## Alpha Vantageでマーケット情報を取得する

Alpha Vantage連携は任意機能です。無料枠では取得可能なシンボルやリクエスト回数に制約があります。

日経平均やS&P500そのものを直接取得できない場合があるため、実運用では `MARKET_SYMBOL_NIKKEI225` や `MARKET_SYMBOL_SP500` に、APIで取得可能な参考ETFや代替シンボルを指定できます。例として、米国市場参考指標に `SPY`、日本市場参考指標にAPI対応シンボルを設定する想定です。

```env
APP_MODE=api
NEWS_PROVIDER=rss
NEWS_RSS_URLS=https://example.com/rss
MARKET_PROVIDER=alpha_vantage
MARKET_API_KEY=your_api_key
MARKET_SYMBOL_NIKKEI225=
MARKET_SYMBOL_SP500=SPY
MARKET_FX_BASE=USD
MARKET_FX_QUOTE=JPY

# external request
REQUEST_TIMEOUT_SECONDS=10
REQUEST_RETRY_COUNT=4
MARKET_REQUEST_INTERVAL_SECONDS=2
```

注意点:

- `MARKET_API_KEY` は `.env` に設定し、Gitにコミットしないでください。
- `ALPHA_VANTAGE_API_KEY` も互換名として利用できますが、READMEでは `MARKET_API_KEY` を推奨します。
- `MARKET_REQUEST_INTERVAL_SECONDS` は、複数のマーケット対象を連続取得するときに各取得の間で待つ秒数です。
- 無料枠で制限に当たる場合は、`MARKET_REQUEST_INTERVAL_SECONDS=5` などへ増やしてください。
- Alpha Vantageの制限レスポンスは警告として扱い、取得できた指標だけでレポート生成を継続します。
- APIキーや認証URLはログ・レポートへ出力しない設計です。

## `.env.example` の使い方

必要に応じて `.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

`.env` は `.gitignore` で管理対象外にしています。APIキー、個人用RSS URL、認証情報は公開リポジトリへ含めないでください。

主要な環境変数:

| 変数 | 既定値 | 説明 |
| --- | --- | --- |
| `APP_MODE` | `sample` | `sample` または `api` |
| `NEWS_PROVIDER` | `rss` | ニュースProvider |
| `NEWS_RSS_URLS` | 空 | 国内RSSのフォールバックURL |
| `NEWS_JP_RSS_URLS` | 空 | 国内RSS URL |
| `NEWS_GLOBAL_RSS_URLS` | 空 | 海外RSS URL |
| `MARKET_PROVIDER` | `alpha_vantage` | マーケットProvider |
| `MARKET_API_KEY` | 空 | マーケットAPIキー |
| `MARKET_SYMBOL_NIKKEI225` | 空 | 日本市場参考指標のProviderシンボル |
| `MARKET_SYMBOL_SP500` | 空 | 米国市場参考指標のProviderシンボル |
| `REQUEST_TIMEOUT_SECONDS` | `10` | 外部取得タイムアウト |
| `REQUEST_RETRY_COUNT` | `1` | 外部取得リトライ回数 |
| `MARKET_REQUEST_INTERVAL_SECONDS` | `0` | マーケットAPIの連続取得間隔 |

## テスト実行

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

テストは実APIキーと外部通信に依存しません。

## CI

GitHub Actions設定はリポジトリルートの `.github/workflows/tests.yml` にあります。

push / pull request時に以下を実行します。

```bash
cd morning-news
python -m pip install -r requirements-dev.txt
python -m pytest
```

## 出力されるレポート

日次実行では次のファイルが生成されます。

```text
reports/YYYY-MM-DD.md
```

公開用の固定サンプルレポートは次のファイルです。

```text
reports/sample-report.md
```

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
| ポートフォリオサマリー | `../docs/portfolio-summary.md` |
| 要件定義 | `../docs/requirements/要件定義.md` |
| 基本設計 | `../docs/basic-design/基本設計.md` |
| 詳細設計 Phase 1 | `../docs/detail-design/詳細設計Phase 1.md` |
| 詳細設計 Phase 2 | `../docs/detail-design/詳細設計Phase 2.md` |
| 詳細設計 Phase 3 | `../docs/detail-design/詳細設計Phase 3.md` |
| 詳細設計 Phase 4 | `../docs/detail-design/詳細設計Phase 4.md` |
| 詳細設計 Phase 5 | `../docs/detail-design/詳細設計Phase 5.md` |
| 詳細設計 Phase 6 | `../docs/detail-design/詳細設計Phase 6.md` |
| 変更メモ | `../docs/changes/2026-05-27-market-request-interval.md` |

## ポートフォリオとして見てほしいポイント

- 外部APIがなくても `sample` モードで再現できる構成にしていること。
- 部分失敗、欠損値、外部データ全滅を同じ成功に見せず、警告と終了コードで分けていること。
- APIキー漏えい、認証ヘッダー、個人用URLなど、公開時に問題になりやすい点をテストしていること。
- 設計、実装、テスト、READMEを分けて整備し、第三者が判断理由を追える形にしていること。

## 今後の改善予定

- News APIやGDELTなど、ニュースProviderの実接続を追加する。
- マーケット指標の表示名とProviderシンボルをより柔軟に設定できるようにする。
- GitHub PagesでHTML資料を見やすく公開する。
- カバレッジ計測やCIバッジを追加する。
- 定時実行手順を整備する。
