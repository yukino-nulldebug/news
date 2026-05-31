# Morning News

朝のニュースとマーケット情報を日次MarkdownレポートとしてまとめるCLIバッチアプリです。

アプリ本体は `morning-news/` 配下にあります。APIキーなしで確認する場合は `sample` モードを使ってください。

## このプロジェクトで示すこと

外部APIに依存する小さなCLIバッチを、再現性、失敗時の継続、ログ、秘密情報保護、テストまで含めて、公開できる形に設計・実装した点を見せるプロジェクトです。

- 再現性: `sample` / `api` を分け、APIキーなしでも確認できる。
- 外部依存の扱い: timeout、retry、Provider分岐、マーケットAPIの連続取得間隔を設定化する。
- 失敗設計: 欠損値は `N/A` と警告、外部データ全滅は終了コード `2` で切り分ける。
- 公開安全性: APIキーや認証情報をログ・レポートに出さない。
- 品質保証: unit、integration、provider、securityのpytestとGitHub Actionsで回帰確認する。
- AI協働: AIで設計整理、実装案、コードレビューを加速し、仕様判断・差分確認・テスト追加は自分で行う。

## 学習プロセスと設計思考

このプロジェクトでは、Pythonでニュース・マーケットレポート生成アプリを作るだけでなく、未知の技術課題を段階的に分解し、調査・設計・実装・検証を反復する過程が追えるようにしています。
学習した内容は、設計資料、コード、テスト、改善ログに残し、抽象的な自己PRではなく成果物から確認できる構成にしました。

| 工程 | 取り組み | 確認できる成果物 |
| --- | --- | --- |
| 要件定義 | 朝の情報収集という課題を、MVPスコープ、成功条件、やること/やらないこと、安全上の注意へ分解する。 | [docs/requirements/要件定義.md](docs/requirements/要件定義.md) |
| 基本設計 | `sample` / `api` モード、モジュール責務、異常系、データ正規化、公開安全性を設計する。 | [docs/basic-design/基本設計.md](docs/basic-design/基本設計.md) |
| 詳細設計 | 設定、Provider、例外、ログ、テスト、公開前チェックをフェーズごとに実装単位へ落とし込む。 | [docs/detail-design/詳細設計Phase 1.md](<docs/detail-design/詳細設計Phase 1.md>) |
| 実装 | Provider、レポート生成、ログ、秘密情報マスク、pytestを小さな単位で実装する。 | [morning-news/](morning-news/) |
| 改善 | API制限、ログ設計、AI協働、外部データ全滅時の扱いを学習ログに反映する。 | [docs/learning/README.md](docs/learning/README.md) |

設計では、未経験の領域を弱みとして扱うのではなく、未知のAPIや外部データ連携を調査し、要件定義・基本設計へ戻し、実装とテストで検証する流れを意識しました。
特に、実務で必要となる安全性・再現性・保守性を確認できるよう、次の点を明示しています。

- 市況コメントは情報提供に限定し、「投資助言ではない」注意事項をレポートに含める。
- APIキーは `.env` と環境変数で扱い、リポジトリ、ログ、レポートへ公開しない。
- `sample` モードを標準確認経路にし、APIキーがない第三者でも出力と処理フローを確認できる。
- 取得失敗、欠損値、外部データ全滅を同じ成功扱いにせず、警告、`N/A`、終了コードで切り分ける。
- 変更はpytestとドキュメントで確認し、再現性のある学習プロセスとして残す。

## 実行手順

詳しいセットアップ、sample実行、api実行、pytest、出力例は次を参照してください。

- アプリREADME: `morning-news/README.md`
- 1枚サマリーHTML: `public/index.html`
- ポートフォリオサマリー: `docs/portfolio-summary.md`
- サンプルレポート: `morning-news/reports/sample-report.md`

## ドキュメント

- 要件定義: `docs/requirements/要件定義.md`
- ポートフォリオサマリー: `docs/portfolio-summary.md`
- 基本設計: `docs/basic-design/基本設計.md`
- 詳細設計 Phase 1: `docs/detail-design/詳細設計Phase 1.md`
- 詳細設計 Phase 2: `docs/detail-design/詳細設計Phase 2.md`
- 詳細設計 Phase 3: `docs/detail-design/詳細設計Phase 3.md`
- 詳細設計 Phase 4: `docs/detail-design/詳細設計Phase 4.md`
- 詳細設計 Phase 5: `docs/detail-design/詳細設計Phase 5.md`
- 詳細設計 Phase 6: `docs/detail-design/詳細設計Phase 6.md`
- 学習ログ: `docs/learning/README.md`
- 学習ログ例: `docs/learning/2026-05-27-api-rate-limit.md`

## レビュー用HTML

`public/index.html` から要件定義、基本設計、詳細設計のHTML版を確認できます。

- 1枚サマリーHTML: `public/index.html`
- 要件定義HTML: `public/pages/requirements.html`
- 基本設計HTML: `public/pages/basic-design.html`
- 詳細設計 Phase 1 HTML: `public/pages/detail-design-phase1.html`
- 詳細設計 Phase 2 HTML: `public/pages/detail-design-phase2.html`
- 詳細設計 Phase 3 HTML: `public/pages/detail-design-phase3.html`
- 詳細設計 Phase 4 HTML: `public/pages/detail-design-phase4.html`
- 詳細設計 Phase 5 HTML: `public/pages/detail-design-phase5.html`
- 詳細設計 Phase 6 HTML: `public/pages/detail-design-phase6.html`
- 学習ログ HTML: `public/pages/learning.html`
