# 学習ログHTML一覧への統合

作成日: 2026-05-31

## 使用スキルまたは担当エージェント

- AI-Assets の agent-router ルールに従い、Codexで既存のHTML導線、学習ログ、マーケットAPIの詳細ページを確認した。
- 秘密情報を含む可能性がある `.env` は読まず、公開済みドキュメントとHTMLだけを対象にした。

## 何を確認したか

- `public/index.html`
- `public/pages/market-request-interval.html`
- `docs/learning/README.md`
- `docs/learning/*.md`
- `docs/changes/2026-05-27-market-request-interval.md`

## 変更まとめ

- `public/pages/learning.html` を追加し、日付ごとの学習ログをHTMLで一覧できるようにした。
- `public/index.html` の学習ログリンクを、MarkdownではなくHTML一覧へ変更した。
- `market-request-interval.html` を学習ログの詳細ページとして扱う導線にした。
- `market-request-interval.html` 側にも学習ログ一覧へ戻るリンクを追加した。
- `docs/learning/README.md` にHTML版一覧とマーケットAPI対応ログを追記した。

## 判断理由

採用担当者が最初に見る `public/index.html` からMarkdownへ直接飛ぶと、学習ログが分散して見えやすい。
そのため、HTML上で日付、テーマ、変更点、学び、関連ページを1ページにまとめ、必要に応じて詳細ページへ進める導線にした。

## 学び

- ポートフォリオの入口では、個別Markdownへ分散させるより、HTMLで時系列にまとめるほうが確認しやすい。
- 個別の変更ページを独立カテゴリとして見せるより、学習ログの中に改善履歴として統合するほうが流れが伝わりやすい。
- 学習ログは「何を変更したか」だけでなく、「なぜその変更をしたか」「次にどう活かすか」まで見えると実務プロセスとして伝わる。

## 注意点

- HTML一覧は要約ページのため、詳細な正本は `docs/learning/` に残す。
- APIキー、トークン、認証情報、個人情報は表示しない。
- 市況コメントは投資助言ではないという前提を維持する。

## 次回変更または次回確認

- 新しい学習ログを追加したら、`public/pages/learning.html` と `docs/learning/README.md` の両方を更新する。
- 学習ログが増えた場合は、月別またはテーマ別にセクション分けする。
