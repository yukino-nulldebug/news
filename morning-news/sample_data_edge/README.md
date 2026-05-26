# Phase 5 Boundary Sample Data

`sample_data_edge` は、通常デモ用の `sample_data` とは分けた境界値確認用データである。
通常の `python3 main.py` では使用せず、pytest実行時のみ参照する。

## 含めるケース

- `summary` が空または空白のみのニュース
- 改行、タブ、重複空白を含むニュース概要
- `SUMMARY_MAX_LENGTH` による省略対象になる長文概要
- `previous_close == 0` による変化率計算不可
- `market_missing_previous_close.json`: `previous_close` 欠損による `MarketCalculationError`
- `market_invalid_number.json`: 数値項目の型不正による `MarketCalculationError`

通常の `python3 main.py` は `sample_data` を使用する。
このディレクトリは Phase 5 の異常系・境界値pytest用フィクスチャとして使う。
