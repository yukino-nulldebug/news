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
- 変更メモ: `docs/changes/2026-05-27-market-request-interval.md`

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
