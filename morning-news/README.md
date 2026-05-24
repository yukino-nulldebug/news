# Morning News

CLI batch application that generates `reports/YYYY-MM-DD.md`.

## Run with sample data

```bash
python3 main.py
```

## Run RSS news with sample market data

Use this mode first when checking Phase 4 external news fetching.

```env
APP_MODE=api
NEWS_PROVIDER=rss
NEWS_RSS_URLS=https://example.com/rss
MARKET_PROVIDER=sample
```

`NEWS_RSS_URLS` is treated as a fallback for domestic RSS. Use
`NEWS_JP_RSS_URLS` and `NEWS_GLOBAL_RSS_URLS` when you want to split feeds.

## Run Alpha Vantage market fetching

```env
APP_MODE=api
NEWS_PROVIDER=rss
NEWS_RSS_URLS=https://example.com/rss
MARKET_PROVIDER=alpha_vantage
ALPHA_VANTAGE_API_KEY=your_api_key
```

`MARKET_PROVIDER=alphavantage` is also accepted. `MARKET_API_KEY` is the
preferred key name, but `ALPHA_VANTAGE_API_KEY` is supported for convenience.
