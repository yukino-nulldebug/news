# Morning News 詳細設計 phase 1
| Phase 1 | `sample_data` からMarkdownレポート生成 | APIキーなしで `reports/YYYY-MM-DD.md` が作成される。 |

## 1. 詳細設計の目的

本書は、要件定義および基本設計で定義した内容をもとに、実装に必要なファイル構成、関数名、処理内容、入出力、エラー処理を具体化するための詳細設計書である。

本プロジェクトでは、開発範囲を Phase ごとに分けて進める。
そのため、本書ではまず Phase 1 の対象範囲を明確にし、次フェーズ以降の機能や全体構想が混在しないようにする。

Phase 1 では、`sample_data` のJSONファイルを読み込み、Markdownレポートを生成・保存する最小機能を対象とする。

## 2. Phase 1 の対象範囲

Phase 1 では、API通信を行わず、`sample_data` に配置した固定JSONファイルを読み込み、Markdownレポートを生成・保存する最小機能を実装対象とする。

### 2.1 Phase 1 で実装する機能

| 対象 | 内容 |
| --- | --- |
| サンプルニュース読み込み | `sample_data/news_jp.json` と `sample_data/news_global.json` を読み込む |
| サンプルマーケット読み込み | `sample_data/market.json` を読み込む |
| 概要文整形 | ニュース概要文の改行・重複空白を除去し、指定文字数以内に整形する |
| 変化率計算 | `current_value` と `previous_close` から前日比・変化率を計算する |
| Markdown生成 | ニュース、市況、注意事項を含むMarkdownレポートを生成する |
| レポート保存 | `reports/YYYY-MM-DD.md` にレポートを保存する |
| 基本ログ出力 | 起動、読み込み、生成、保存の結果をログ出力する |

### 2.2 Phase 1 では実装しない機能

| 対象外 | 理由 |
| --- | --- |
| API/RSSからのニュース取得 | Phase 4 で実装する |
| 株価APIからの実データ取得 | Phase 4 で実装する |
| AIによる高度な要約 | MVP対象外 |
| メール・LINE通知 | 後続フェーズで検討する |
| Web UI | MVP対象外 |
| 自動売買・投資助言 | 本システムの対象外 |

### 2.3 Phase 1 で使用する主なファイル

| ファイル | 役割 |
| --- | --- |
| `main.py` | CLIエントリポイント。全体の処理順序を制御する |
| `src/config/settings.py` | 設定値、出力先、最大文字数などを管理する |
| `src/news/fetcher.py` | `sample_data` からニュースデータを読み込む |
| `src/news/formatter.py` | ニュース概要文を整形する |
| `src/market/fetcher.py` | `sample_data` からマーケットデータを読み込む |
| `src/market/calculator.py` | 前日比と変化率を計算する |
| `src/report/generator.py` | Markdownレポート本文を生成する |
| `src/report/writer.py` | レポートファイルを保存する |
| `src/utils/logger.py` | 実行結果とエラーをログ出力する |

## 3. ファイル構成

## 4. データ構造

## 5. 関数設計

## 6. 処理順序

## 7. エラー処理

## 8. テスト観点

## 9. 次フェーズで追加するもの
