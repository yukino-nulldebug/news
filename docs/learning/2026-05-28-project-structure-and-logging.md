# ファイル構成とログ設計の整理

## 目的

Morning News を、採用側が見たときに「何をどう完成させたか」を追えるプロジェクト構成にする。

特に、ファイル構成、ログ、テスト、ドキュメントを分け、実装判断の流れがコードだけに埋もれない状態にする。

## 発生した問題

最初のままだと、ニュース取得アプリとして動いていても、採用側には次の点が伝わりにくい。

- どのファイルがどの責務を持つのか。
- sample実行とapi実行の違いは何か。
- 外部取得に失敗したとき、どこに何が記録されるのか。
- 警告とエラーをどう分けているのか。
- 設計、実装、テスト、公開準備をどう進めたのか。

単なる「作りました」ではなく、実務に近い開発プロセスとして見せるには、構成とログの意味を説明できる必要があった。

## 調査

既存ファイルを確認し、責務ごとに説明できる形へ整理した。

| 領域 | 確認したこと |
| --- | --- |
| `morning-news/src/config/` | `.env`、実行モード、Provider設定、API設定を集中管理できているか。 |
| `morning-news/src/news/` | ニュース取得、Provider、RSS正規化、概要文整形を分けられているか。 |
| `morning-news/src/market/` | マーケット取得、Alpha Vantage Provider、変化率計算を分けられているか。 |
| `morning-news/src/report/` | Markdown生成とファイル保存を分けられているか。 |
| `morning-news/src/utils/` | HTTP、ログ、例外、実行結果集計など共通処理を置けているか。 |
| `morning-news/tests/` | unit、integration、provider、security の観点でテストを分けられているか。 |
| `docs/` | 要件定義、基本設計、詳細設計、変更メモを追えるか。 |
| `public/` | 採用側がHTMLで概要を見られるか。 |

ログについては、次の情報が残るかを確認した。

- 実行開始、設定読み込み、取得開始、取得件数、Markdown生成、保存先、終了結果。
- `feature_id` と `process_name` による処理箇所の識別。
- recoverable な失敗は警告として継続。
- 外部データ全滅やデータ不正は終了コードで失敗を明示。
- APIキー、token、Authorization header はマスクする。

## 実装

最終的な見せ方は次の構成にした。

```text
ニュース/
├── README.md
├── docs/
│   ├── requirements/
│   ├── basic-design/
│   ├── detail-design/
│   ├── changes/
│   ├── learning/
│   └── portfolio-summary.md
├── public/
│   ├── index.html
│   ├── pages/
│   └── assets/
└── morning-news/
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

ログ設計は、`main.py` を中心に以下の形へ整理した。

| 処理 | ログ・実行結果で残すこと |
| --- | --- |
| 設定読み込み | `APP_MODE`、設定警告、実行日時 |
| ニュース取得 | 国内・海外の取得開始、Provider、取得件数、整形件数 |
| マーケット取得 | Provider、取得対象数、取得件数、失敗時の警告 |
| 変化率計算 | 計算開始、計算件数、欠損時の警告 |
| レポート生成 | Markdown生成開始・完了、保存先 |
| 終了処理 | `success`、`warning`、`data_failed`、`failed` と件数サマリー |

また、公開リポジトリ向けに次を分けた。

- `reports/sample-report.md` は成果物例として残す。
- 日次生成レポートはGit管理外にする。
- `logs/.gitkeep` は残し、`logs/*.log` はGit管理外にする。
- `.env.example` は残し、`.env` はGit管理外にする。

## 学んだこと

ファイル構成は、ただ整理されているだけではなく、「なぜ分かれているか」を説明できることが重要だった。

今回の構成では、次のように責務を切り分けることで、コードレビューや採用側の確認がしやすくなった。

- 設定は `src/config/` に寄せる。
- 外部取得は Provider に閉じ込める。
- レポート生成と保存を分ける。
- 失敗の記録はログと実行結果に集約する。
- テストは機能単位とリスク単位で分ける。
- ドキュメントは要件、設計、変更、学習ログで分ける。

## 次の改善

- `docs/learning/` のログを実装日ごとに増やす。
- HTMLトップページから学習ログへ辿れる導線を増やす。
- `logs/app.log` のサンプルを、秘密情報を含まない形でドキュメント化する。
- カバレッジ計測を追加し、どの責務がテストで守られているか見えるようにする。
