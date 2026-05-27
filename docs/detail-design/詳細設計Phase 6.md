# Morning News 詳細設計 Phase 6

| Phase | 対象 | 完了条件 |
| --- | --- | --- |
| Phase 6 | README・サンプルレポート整備 | 第三者がREADMEの手順通りにセットアップ、sample実行、テスト、出力確認を行える。 |

## 1. 詳細設計の目的

本書は、要件定義および基本設計で定義した公開リポジトリ方針をもとに、Phase 6 で整備する README、`.env.example`、サンプルレポート、`.gitignore`、公開前チェック、実行手順を具体化するための詳細設計書である。

Phase 1 では、`sample_data` からMarkdownレポートを生成した。
Phase 2 では、ログとエラー処理を追加した。
Phase 3 では、概要文整形、変化率計算、市況コメント生成を追加した。
Phase 4 では、`.env`、`APP_MODE=api`、RSS/API取得を追加した。
Phase 5 では、pytestによる自動テストを追加する。

Phase 6 では、実装済みの機能を第三者が迷わず確認できる状態に仕上げる。
公開リポジトリとして、APIキーなしで動くこと、機密情報を含まないこと、実行手順と出力例が一致していることを重視する。

## 2. Phase 6 の対象範囲

### 2.1 Phase 6 で実装する機能

| 対象 | 内容 |
| --- | --- |
| README整備 | 概要、機能、セットアップ、sample実行、api実行（任意）、テスト、出力例、注意事項を記載する |
| `.env.example` 整備 | 必要な環境変数、既定値、空値、Provider設定、APIキー設定例を安全に記載する |
| サンプルレポート整備 | `reports/sample-report.md` を追加し、APIキーなしで確認できる出力例を公開する |
| `.gitignore` 整備 | `.env`、`.venv/`、`__pycache__/`、`.DS_Store`、ログ、日次生成物などを管理対象外にする |
| 公開前チェック | Git管理対象、機密情報、依存関係、実行結果、テスト結果を確認する手順を定義する |
| READMEのコマンド検証 | READMEに載せたコマンドがローカルで実行できることを確認する |
| サンプルデータ説明 | `sample_data/` と `sample_data_edge/` の用途を説明する |
| 注意事項明記 | 投資助言ではないこと、ニュース本文全文を取得しないこと、APIキーを公開しないことを明記する |
| ポートフォリオ観点 | 要件定義、基本設計、詳細設計、テスト、サンプル出力への導線を用意する |

### 2.2 Phase 6 では実装しない機能

| 対象外 | 理由 |
| --- | --- |
| 新しいニュースProviderの追加 | Phase 4 で拡張口を用意済み。Phase 6 は公開準備に集中する |
| 実APIキー付きのデモ公開 | 機密情報を公開しない方針に反するため対象外 |
| 定時実行の本体実装 | MVPでは手動実行で確認可能にする。定時実行はREADMEで参考扱いにする |
| GitHub Actions必須化 | Phase 5 のテスト整備後、後続任意タスクで追加する |
| Web UI | MVP対象外 |
| 通知連携 | MVP対象外 |
| AI要約 | MVP対象外 |
| 投資助言・売買判断 | コンプライアンス要件により対象外 |

### 2.3 基本設計との対応

| 基本設計の項目 | Phase 6 での具体化 |
| --- | --- |
| 1.2 重要な設計方針 | README、サンプルデータ、サンプルレポート、テストでポートフォリオ性を示す |
| 3. 実行モード設計 | `sample` と `api` の実行手順をREADMEへ落とし込む |
| 8. レポート生成設計 | `reports/sample-report.md` を出力例として整備する |
| 12. 設定・環境変数設計 | `.env.example` を公開可能な形へ整備する |
| 13. テスト方針 | Phase 5 のpytest実行手順をREADMEに記載する |
| 14. 実装フェーズ | Phase 6 の完了条件を公開前チェックで判定できるようにする |
| 16. ポートフォリオで見せるポイント | 設計書、実装、テスト、出力例への導線をREADMEに用意する |

## 3. README設計

### 3.1 READMEの基本方針

READMEは日本語を基本にする。
コマンド、環境変数、ファイル名、Pythonモジュール名は実装と同じ英語識別子を使う。

READMEの目的は、第三者が以下を短時間で確認できるようにすることである。

- 何を作るアプリか
- APIキーなしでどう動かすか
- 実データ取得を試すには何を設定するか
- どのファイルにレポートが出るか
- どのテストを実行すればよいか
- 投資助言ではないこと
- APIキーを公開しない構成であること

### 3.2 README構成

READMEは以下の順番で構成する。

```text
# Morning News

## 概要
## 主な機能
## ディレクトリ構成
## 必要環境
## セットアップ
## sampleモードで実行する
## apiモード（任意）でRSSニュースを取得する
## Alpha Vantage（任意）でマーケット情報を取得する
## テストを実行する
## 出力されるレポート
## ログ
## 環境変数
## サンプルデータ
## 注意事項
## 設計ドキュメント
```

### 3.3 `概要`

記載内容:

- Morning News は、ニュースとマーケット情報を収集し、日次Markdownレポートを生成するCLIバッチアプリである。
- `sample` モードではAPIキーなしで動作確認できる。
- `api` モードは任意機能で、RSSニュースとマーケットAPIから外部データを取得できる。
- 生成物は `reports/YYYY-MM-DD.md` に保存される。

記載しない内容:

- AI要約を行うという誤解を招く表現
- ニュース本文全文を収集するという表現
- 投資判断を支援する、売買判断を行うという表現

### 3.4 `主な機能`

READMEでは以下を箇条書きで記載する。

- 国内ニュース、海外ニュースの取得
- ニュース概要文の整形
- 日本市場参考指標、米国市場参考指標、USD/JPY相当のマーケット情報取得
- 前日比、変化率の計算
- 中立的な市況コメント生成
- Markdownレポート保存
- ログ出力
- APIキーなしの `sample` モード
- pytestによる主要処理のテスト

### 3.5 `ディレクトリ構成`

READMEでは、実際のリポジトリ構成に合わせて以下を記載する。

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
| `src/config/` | 設定、環境変数、実行モードを管理する |
| `src/news/` | ニュース取得、Provider、概要文整形を行う |
| `src/market/` | マーケット取得、Provider、変化率計算を行う |
| `src/report/` | Markdown生成と保存を行う |
| `src/utils/` | ログ、例外、HTTP、実行結果集計を行う |
| `sample_data/` | APIキーなしで動かす正常系サンプル |
| `sample_data_edge/` | pytestで使う境界値・異常系サンプル |
| `reports/` | 生成されたレポートとサンプルレポート |
| `logs/` | 実行ログ |
| `tests/` | pytestテスト |

### 3.6 `必要環境`

記載内容:

| 項目 | 内容 |
| --- | --- |
| Python | Python 3.10以上を推奨 |
| OS | macOS / Linux / Windows のローカル環境 |
| 外部APIキー | sampleモードでは不要 |
| ネットワーク | sampleモードと単体テストでは不要。apiモード（任意）では必要 |

Pythonバージョンは、`zoneinfo` を利用しているため Python 3.9 以上を最低条件とし、READMEでは Python 3.10 以上を推奨として案内する。

### 3.7 `セットアップ`

READMEに記載する標準手順:

```bash
cd morning-news
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Phase 5 で `requirements-dev.txt` を追加した場合は、テスト実行用として以下も記載する。

```bash
python3 -m pip install -r requirements-dev.txt
```

Windows向け補足は、必要最小限にとどめる。

```bash
.venv\Scripts\activate
```

### 3.8 `sampleモードで実行する`

APIキーなしで最初に確認する手順として、READMEの中心に置く。

```bash
APP_MODE=sample python3 main.py
```

環境変数を指定しない場合も `sample` で起動できるため、簡易手順として以下も記載する。

```bash
python3 main.py
```

期待結果:

- `reports/YYYY-MM-DD.md` が作成される。
- `logs/app.log` に実行結果が出力される。
- レポートに国内ニュース、海外ニュース、マーケット情報、市況コメント、注意事項が含まれる。

### 3.9 `apiモード（任意）でRSSニュースを取得する`

RSSニュース取得を確認する最小手順を記載する。
マーケットAPIキーがない利用者でも確認しやすいように、`MARKET_PROVIDER=sample` の例を先に示す。
apiモードは任意機能として扱い、ポートフォリオ確認では `sample` モードを推奨する。

READMEには以下を明記する。

- apiモードは任意機能である。
- APIキーや外部サービスの状態により、取得結果が変わる場合がある。
- ポートフォリオ確認では `sample` モードを推奨する。

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

説明:

- `NEWS_RSS_URLS` は国内RSSのフォールバックとして扱う。
- 国内・海外を分けたい場合は `NEWS_JP_RSS_URLS` と `NEWS_GLOBAL_RSS_URLS` を使う。
- `MARKET_PROVIDER=sample` は、apiモードでニュースだけ実データにし、マーケットはsampleデータを使う確認用設定である。

### 3.10 `Alpha Vantage（任意）でマーケット情報を取得する`

マーケットAPIを試す利用者向けに、APIキーを `.env` に置く例を記載する。
Alpha Vantage連携は任意機能として扱い、sampleモードの動作確認には不要である。

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

# external request
REQUEST_TIMEOUT_SECONDS=10
REQUEST_RETRY_COUNT=4
MARKET_REQUEST_INTERVAL_SECONDS=2
```

注意点:

- `MARKET_API_KEY` は `.env` に設定し、Gitにコミットしない。
- `ALPHA_VANTAGE_API_KEY` も互換名として利用できるが、READMEでは `MARKET_API_KEY` を推奨する。
- `MARKET_REQUEST_INTERVAL_SECONDS` は、複数のマーケット対象を連続取得するときに各取得の間で待つ秒数である。
- 無料枠や取得可能シンボルは外部サービス側の仕様に依存する。
- APIキーや認証URLはログ・レポートへ出力しない設計である。

### 3.11 `テストを実行する`

Phase 5 の完了後、READMEに以下を記載する。

```bash
python3 -m pytest
```

カテゴリ別確認:

```bash
python3 -m pytest tests/unit
python3 -m pytest tests/providers
python3 -m pytest tests/integration
python3 -m pytest tests/security
```

期待結果:

- 全テストが成功する。
- テストは実APIキーと外部通信に依存しない。

### 3.12 `出力されるレポート`

READMEでは、実際の出力先とサンプルレポートへの導線を記載する。

| 種類 | パス |
| --- | --- |
| 日次レポート | `reports/YYYY-MM-DD.md` |
| 公開用サンプル | `reports/sample-report.md` |

サンプルとして、レポートの構成だけを短く掲載する。
README本文に長いレポート全文は貼らず、`reports/sample-report.md` へ誘導する。

### 3.13 `ログ`

記載内容:

- ログは `logs/app.log` に出力される。
- ログには日時、ログレベル、機能ID、処理名、メッセージが含まれる。
- APIキー、トークン、認証ヘッダー、未マスク認証URLは出力しない。

ログ例:

```text
2026-05-25 07:00:00 INFO F-10 main.main Morning News を開始しました
2026-05-25 07:00:01 INFO F-09 main.summary 実行結果: status=success warnings=0 errors=0
```

### 3.14 `環境変数`

READMEでは、主要な環境変数を表で説明し、詳細は `.env.example` を参照する形にする。

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
| `MARKET_REQUEST_INTERVAL_SECONDS` | `0` | マーケットAPIの連続取得間隔 |

### 3.15 `サンプルデータ`

READMEで以下を説明する。

| パス | 用途 |
| --- | --- |
| `sample_data/news_jp.json` | 国内ニュースの正常系サンプル |
| `sample_data/news_global.json` | 海外ニュースの正常系サンプル |
| `sample_data/market.json` | マーケット情報の正常系サンプル |
| `sample_data_edge/` | pytestで使う境界値・異常系データ |

`sample_data_edge/` は Phase 5 の異常系・境界値テスト用に追加するテストデータディレクトリである。
通常実行では使用せず、pytest実行時のみ参照する。

サンプルニュースは実在記事の本文や有料記事本文をコピーしない。
ポートフォリオ確認用の架空データとして扱う。

### 3.16 `注意事項`

READMEには、以下を明記する。

- 本アプリは情報提供を目的とする。
- 市況コメントは投資助言ではない。
- 売買推奨、自動売買、利益保証は行わない。
- ニュース本文全文、有料記事、ログイン後ページ本文は取得しない。
- `.env` とAPIキーはGitにコミットしない。
- 外部APIの無料枠、利用規約、取得可能データは利用者が確認する。

### 3.17 `設計ドキュメント`

READMEから以下へ導線を置く。

| ドキュメント | パス |
| --- | --- |
| 要件定義 | `docs/requirements/要件定義.md` |
| 基本設計 | `docs/basic-design/基本設計.md` |
| 詳細設計 Phase 1 | `docs/detail-design/詳細設計Phase 1.md` |
| 詳細設計 Phase 2 | `docs/detail-design/詳細設計Phase 2.md` |
| 詳細設計 Phase 3 | `docs/detail-design/詳細設計Phase 3.md` |
| 詳細設計 Phase 4 | `docs/detail-design/詳細設計Phase 4.md` |
| 詳細設計 Phase 5 | `docs/detail-design/詳細設計Phase 5.md` |
| 詳細設計 Phase 6 | `docs/detail-design/詳細設計Phase 6.md` |

## 4. `.env.example` 設計

### 4.1 基本方針

`.env.example` は公開リポジトリに含める。
実APIキー、個人URL、内部URL、個人情報は含めない。
値が利用者固有のものは空にする。

### 4.2 記載順

`.env.example` は以下の順番にする。

```text
# execution mode
APP_MODE=sample

# news
NEWS_PROVIDER=rss
NEWS_RSS_URLS=
NEWS_JP_RSS_URLS=
NEWS_GLOBAL_RSS_URLS=
NEWS_API_KEY=
NEWS_API_ENDPOINT=
NEWS_LIMIT=5
SUMMARY_MAX_LENGTH=120

# market
MARKET_PROVIDER=alpha_vantage
MARKET_API_KEY=
ALPHA_VANTAGE_API_KEY=
MARKET_API_ENDPOINT=https://www.alphavantage.co/query
ALPHA_VANTAGE_API_ENDPOINT=https://www.alphavantage.co/query
MARKET_SYMBOL_NIKKEI225=
MARKET_SYMBOL_SP500=
MARKET_FX_BASE=USD
MARKET_FX_QUOTE=JPY

# output
REPORT_DIR=reports
LOG_DIR=logs

# external request
REQUEST_TIMEOUT_SECONDS=10
REQUEST_RETRY_COUNT=4
MARKET_REQUEST_INTERVAL_SECONDS=2
```

### 4.3 `.env.example` の確認観点

| 確認内容 | 期待結果 |
| --- | --- |
| APIキー欄 | 空値または `your_api_key` ではなく空値を基本にする |
| RSS URL欄 | 実在する個人用URLを入れない |
| コメント | 用途がわかる最小限のコメントにする |
| 重複変数 | 互換名は必要なものだけ残す |
| 推奨値 | コード既定値と異なる運用推奨値はREADMEで用途を説明する |

### 4.4 `.env` 作成手順

READMEには、以下のように `.env.example` をコピーして使う手順を記載する。

```bash
cp .env.example .env
```

`.env` は `.gitignore` で管理対象外にする。

## 5. サンプルレポート設計

### 5.1 出力ファイル

Phase 6 では、公開用の固定サンプルレポートとして以下を追加する。

```text
reports/sample-report.md
```

日次実行で生成される `reports/YYYY-MM-DD.md` とは別に管理する。

### 5.2 サンプルレポートの生成元

サンプルレポートは、`APP_MODE=sample` の出力をもとに作る。
APIキーや外部RSSの内容に依存しない。

生成手順:

1. `APP_MODE=sample python3 main.py` を実行する。
2. 生成された `reports/YYYY-MM-DD.md` を確認する。
3. 公開用として `reports/sample-report.md` を作成または更新する。
4. APIキー、個人情報、外部サービスの認証URLが含まれないことを確認する。
5. 市況コメントに禁止表現が含まれないことを確認する。

### 5.3 サンプルレポートに含める内容

| セクション | 必須 |
| --- | --- |
| `# Morning News Report` | 必須 |
| 作成日時 | 必須 |
| 実行モード | 必須。`sample` |
| `## 1. 今日の注目ポイント` | 必須 |
| `## 2. 国内ニュース` | 必須 |
| `## 3. 海外ニュース` | 必須 |
| `## 4. マーケット情報` | 必須 |
| `## 5. 市況コメント` | 必須 |
| `## 6. 注意事項` | 必須 |
| 投資助言ではない旨 | 必須 |

### 5.4 サンプルレポートに含めない内容

| 含めないもの | 理由 |
| --- | --- |
| APIキー | 機密情報のため |
| `.env` の内容 | 機密情報を含む可能性があるため |
| 実在有料記事本文 | 著作権・利用規約リスクがあるため |
| ログ全文 | 実行環境情報を含む可能性があるため |
| 売買推奨表現 | 投資助言と誤認されるため |

### 5.5 日次レポートのGit管理方針

MVP公開版では、公開用の安定した出力例として `reports/sample-report.md` を基本にする。
日次生成される `reports/YYYY-MM-DD.md` はローカル実行結果として扱い、原則として新規追加分はGit管理対象外にする。

既にGit管理されている日次レポートがある場合は、Phase 6 実装時に以下のどちらかを選ぶ。

| 方針 | 内容 |
| --- | --- |
| 標準方針 | `sample-report.md` に集約し、既存の日次レポート整理は別コミットで扱う |
| 保持方針 | 既存の日次レポートをサンプル履歴として残し、新規生成分だけ無視する |

標準方針では、日次レポートの増加による不要な差分を防ぐ。
ただし、既存追跡済みファイルの削除は影響があるため、Phase 6 実装時に明示的に判断する。

## 6. `.gitignore` 設計

### 6.1 基本方針

`.gitignore` は公開リポジトリの安全性を守るために必須とする。
特に `.env`、仮想環境、Pythonキャッシュ、OSメタデータ、ログ、生成レポートを管理対象外にする。

### 6.2 推奨内容

```gitignore
# environment
.env
.env.*
!.env.example

# virtualenv
.venv/
venv/

# python
__pycache__/
*.py[cod]
.pytest_cache/

# os
.DS_Store

# logs
logs/*.log
!logs/.gitkeep

# generated reports
reports/*.md
!reports/sample-report.md
!reports/.gitkeep
```

### 6.3 注意点

| 項目 | 注意 |
| --- | --- |
| `.env.*` | `.env.local` 等を無視するが、`.env.example` は例外で管理する |
| `reports/*.md` | 新規日次レポートを無視するが、`sample-report.md` は管理する |
| `logs/*.log` | 実行ログを無視するが、`logs/.gitkeep` は管理する |
| 既存追跡済みファイル | `.gitignore` 追加だけでは追跡解除されないため、整理は別途判断する |

## 7. 公開前チェック設計

### 7.1 Git管理対象チェック

公開前に以下を確認する。

```bash
git status --short
git ls-files
```

確認観点:

| 確認内容 | 期待結果 |
| --- | --- |
| `.env` | Git管理対象に含まれない |
| `.venv/` | Git管理対象に含まれない |
| `.DS_Store` | Git管理対象に含まれない |
| `logs/app.log` | Git管理対象に含まれない |
| APIキー入りファイル | Git管理対象に含まれない |
| `reports/sample-report.md` | Git管理対象に含まれる |
| `docs/` | 要件定義、基本設計、詳細設計が含まれる |

### 7.2 機密情報チェック

公開前に、Git管理対象ファイルへ秘密情報が入っていないことを確認する。

```bash
git grep -n "API_KEY"
git grep -n "apikey="
git grep -n "token="
```

この確認では、変数名や説明としての `API_KEY` は許容する。
実値らしい長いキー文字列、個人用URL、認証付きURLがないことを確認する。

追加で確認する文字列:

| パターン | 意図 |
| --- | --- |
| `ALPHA_VANTAGE_API_KEY=` | `.env.example` 以外に実値がないか確認する |
| `MARKET_API_KEY=` | `.env.example` 以外に実値がないか確認する |
| `Authorization` | 認証ヘッダーがハードコードされていないか確認する |
| `secret` | テスト用以外の秘密値がないか確認する |

### 7.3 実行チェック

READMEの手順通りに実行できることを確認する。

```bash
python3 -m pip install -r requirements.txt
APP_MODE=sample python3 main.py
```

Phase 5 完了後は以下も実行する。

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

期待結果:

- sampleモード実行が終了コード `0` で完了する。
- `reports/YYYY-MM-DD.md` が生成される。
- `logs/app.log` が生成される。
- pytestが終了コード `0` で完了する。

### 7.4 出力チェック

生成されたレポートとサンプルレポートを確認する。

| 確認内容 | 期待結果 |
| --- | --- |
| 主要セクション | 1〜6がそろっている |
| 国内ニュース | タイトル、配信元、公開日時、概要、URLがある |
| 海外ニュース | タイトル、配信元、公開日時、概要、URLがある |
| マーケット情報 | 現在値、前日比、変化率がある |
| 市況コメント | 中立表現である |
| 注意事項 | 投資助言ではない旨がある |
| APIキー | 含まれない |
| 禁止表現 | 含まれない |

### 7.5 禁止表現チェック

市況コメントとREADMEに、投資助言と誤認される表現がないことを確認する。

禁止表現:

- 買うべき
- 売るべき
- 今が買い時
- 必ず上がる
- 投資すべき
- 利益が出る

確認コマンド例:

```bash
git grep -n "買うべき"
git grep -n "売るべき"
git grep -n "今が買い時"
git grep -n "必ず上がる"
git grep -n "投資すべき"
git grep -n "利益が出る"
```

要件定義で禁止表現として列挙している箇所は許容する。
レポート本文や市況コメント生成コードの出力文として使われていないことを確認する。

## 8. READMEコマンド検証設計

### 8.1 検証対象コマンド

READMEに記載したコマンドは、Phase 6 完了前に実行確認する。

| コマンド | 期待結果 |
| --- | --- |
| `python3 -m venv .venv` | 仮想環境が作成される |
| `source .venv/bin/activate` | 仮想環境が有効になる |
| `python3 -m pip install -r requirements.txt` | 依存関係が入る |
| `python3 -m pip install -r requirements-dev.txt` | pytestが入る |
| `APP_MODE=sample python3 main.py` | レポート生成成功 |
| `python3 -m pytest` | テスト成功 |

### 8.2 apiモードの検証範囲

RSSやマーケットAPIは外部サービスに依存するため、READMEのapiモード手順は以下の範囲で確認する。
READMEでも、sampleモードを標準確認手順、apiモードを任意機能として説明する。

| 手順 | 確認方法 |
| --- | --- |
| RSS URL設定例 | 文法として正しいことを確認する |
| `MARKET_PROVIDER=sample` | 実APIキーなしでapiモードの流れを確認できる |
| Alpha Vantage設定例 | `.env.example` と変数名が一致している |
| APIキー未設定時 | 警告が出て秘密情報が出ない |

実APIキーを使う確認は任意とし、公開前チェックの必須条件にはしない。

## 9. ドキュメント整合性チェック

### 9.1 設計書との整合

READMEと `.env.example` は、要件定義・基本設計・詳細設計と矛盾しないようにする。

| 確認内容 | 期待結果 |
| --- | --- |
| 実行モード | `sample` / `api` の説明が基本設計と一致している |
| レポート出力先 | `reports/YYYY-MM-DD.md` と一致している |
| サンプルレポート | `reports/sample-report.md` と一致している |
| 環境変数 | Phase 4 の設定名と一致している |
| テスト手順 | Phase 5 のpytest設計と一致している |
| 対象外機能 | AI要約、本文全文取得、投資助言をしないことが明記されている |

### 9.2 実装との整合

READMEに記載する関数名やディレクトリ構成は、実装と一致させる。

確認対象:

- `main.py`
- `src/config/settings.py`
- `src/news/fetcher.py`
- `src/news/providers/rss.py`
- `src/market/providers/alpha_vantage.py`
- `src/report/generator.py`
- `requirements.txt`
- `requirements-dev.txt`
- `.env.example`

## 10. 公開リポジトリ方針

### 10.1 公開リポジトリに含めるもの

| 対象 | 理由 |
| --- | --- |
| ソースコード | 実装内容を確認できる |
| `README.md` | 実行手順を確認できる |
| `.env.example` | 設定項目を確認できる |
| `.gitignore` | 機密情報を除外する方針を確認できる |
| `sample_data/` | APIキーなしで動作確認できる |
| `sample_data_edge/` | テスト観点を確認できる |
| `reports/sample-report.md` | 出力例を確認できる |
| `tests/` | 自動テストを確認できる |
| `docs/` | 要件定義から詳細設計までを確認できる |

### 10.2 公開リポジトリに含めないもの

| 対象 | 理由 |
| --- | --- |
| `.env` | APIキーを含む可能性がある |
| APIキー | 機密情報 |
| `.venv/` | 環境依存で大きい |
| `__pycache__/` | 生成物 |
| `.DS_Store` | OSメタデータ |
| `logs/app.log` | ローカル実行履歴 |
| 個人用RSS URL | 個人情報や利用条件を含む可能性がある |
| 有料記事本文 | 著作権・利用規約リスク |

## 11. 実装手順

Phase 6 は、以下の順番で実装・確認する。

1. 既存のREADMEを読み、実装済み機能と不足している説明を洗い出す。
2. READMEを日本語中心の構成に更新し、概要、機能、セットアップ、sample実行、api実行（任意）、テスト、出力、ログ、注意事項を記載する。
3. `.env.example` を確認し、Phase 4 の設定値とコードの既定値に合わせて整理する。
4. `.gitignore` を追加または更新し、`.env`、`.venv/`、`__pycache__/`、`.DS_Store`、ログ、生成レポートを除外する。
5. `APP_MODE=sample python3 main.py` を実行し、生成レポートを確認する。
6. `reports/sample-report.md` を追加または更新する。
7. `reports/sample-report.md` にAPIキー、個人情報、禁止表現が含まれないことを確認する。
8. Phase 5 完了後であれば `python3 -m pytest` を実行する。
9. READMEに記載したコマンドを上から順に実行し、破綻がないことを確認する。
10. `git status --short --untracked-files=all` で、公開対象外ファイルが含まれていないことを確認する。
11. `git ls-files` で、`.env`、`.venv/`、`.DS_Store`、`logs/app.log` が追跡対象でないことを確認する。
12. `git grep` で、APIキー実値や未マスク認証URLがないことを確認する。
13. READMEから設計ドキュメント、サンプルレポート、テストへの導線があることを確認する。
14. 必要なファイルだけをステージングし、日本語のコミットメッセージでコミットする。

## 12. 受け入れ条件

Phase 6 は、以下を満たしたら完了とする。

- READMEに、概要、主な機能、必要環境、セットアップ、sample実行、api実行（任意）、テスト、出力、ログ、環境変数、注意事項が記載されている。
- READMEで、apiモードは任意機能であり、APIキーや外部サービスの状態により取得結果が変わる場合があることが明記されている。
- READMEの手順通りに `APP_MODE=sample python3 main.py` を実行すると、レポートが生成される。
- READMEの手順通りに `python3 -m pytest` を実行できる。
- `.env.example` に必要な環境変数が記載され、実APIキーや個人URLが含まれていない。
- `.gitignore` に `.env`、`.venv/`、`__pycache__/`、`.DS_Store`、ログ、生成日次レポートの除外方針が記載されている。
- `reports/sample-report.md` が存在し、主要セクションと注意事項を含む。
- `reports/sample-report.md` にAPIキー、認証URL、個人情報、有料記事本文が含まれない。
- 市況コメントとREADMEに、投資助言と誤認される出力表現が含まれない。
- `git status` で `.env` やローカル生成物がステージング対象になっていない。
- `git ls-files` に `.env`、`.venv/`、`.DS_Store`、`logs/app.log` が含まれない。
- READMEから、要件定義、基本設計、詳細設計、テスト、サンプルレポートへ辿れる。
- 第三者がAPIキーなしで、セットアップ、sample実行、出力確認まで完了できる。

## 13. 後続任意タスク

Phase 6 完了後に検討できる任意タスクは以下とする。

| タスク | 内容 |
| --- | --- |
| GitHub Actions | `python3 -m pytest` をPR時に自動実行する |
| カバレッジ | `pytest-cov` を追加し、主要モジュールのカバレッジを可視化する |
| 定時実行手順 | cron、launchd、GitHub Actions scheduleの参考手順を追加する |
| Provider追加 | NewsAPI、GDELT、FMPなどの実Providerを追加する |
| ログローテーション | 長期利用時のログ肥大化に対応する |
| サンプルレポート自動生成 | 固定日時で `sample-report.md` を再生成する補助スクリプトを追加する |

Phase 6 完了時点では、実APIを使う自動E2E、定時実行の本体実装、通知、Web UI、AI要約、ニュース本文全文取得、自動売買・投資助言は実装しない。
