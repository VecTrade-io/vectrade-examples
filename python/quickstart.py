"""
VecTrade Python SDK — Complete Quickstart.

Demonstrates ALL 12 resource groups available in the SDK.
Shows real-time quotes, fundamentals, technical analysis, news,
analyst ratings, earnings, insider activity, options, sentiment,
company profile, historical data, and ETF information.

Prerequisites:
    pip install vectrade
    export VECTRADE_API_KEY=vq_your_key_here

Run:
    python quickstart.py
"""

from vectrade import VecTrade

client = VecTrade()

# ─── 1. Real-Time Quote ───────────────────────────────────────────
print("=== Real-Time Quote ===")
quote = client.quotes.get("AAPL")
print(f"  {quote.symbol}: ${quote.price:.2f} ({quote.change_pct:+.2f}%)")
print(f"  Volume: {quote.volume:,}")

# ─── 2. Batch Quotes ─────────────────────────────────────────────
print("\n=== Batch Quotes ===")
symbols = ["MSFT", "GOOGL", "NVDA", "META", "AMZN"]
quotes = client.quotes.batch(symbols)
for q in quotes:
    print(f"  {q.symbol}: ${q.price:.2f} ({q.change_pct:+.2f}%)")

# ─── 3. Company Profile ──────────────────────────────────────────
print("\n=== Company Profile ===")
profile = client.profile.get("AAPL")
print(f"  {profile.company.name}")
print(f"  Sector: {profile.company.sector} | Industry: {profile.company.industry}")
print(f"  Location: {profile.location.city}, {profile.location.state}")

# ─── 4. Fundamentals ─────────────────────────────────────────────
print("\n=== Fundamentals ===")
fund = client.fundamentals.get("AAPL")
print(f"  Market Cap: ${fund.market_cap/1e12:.2f}T")
print(f"  52-Week Range: ${fund.fifty_two_week_low:.2f} - ${fund.fifty_two_week_high:.2f}")
print(f"  SMA50: ${fund.sma50:.2f} | SMA200: ${fund.sma200:.2f}")

# ─── 5. Financial Statements ─────────────────────────────────────
print("\n=== Financial Statements ===")
stmts = client.fundamentals.statements("AAPL")
print(f"  Available: {[k for k in stmts.keys() if k != 'ticker']}")

# ─── 6. Technical Analysis ───────────────────────────────────────
print("\n=== Technical Analysis ===")
tech = client.technicals.get("AAPL")
print(f"  Technical Score: {tech.technical_score}/100")
rsi = tech.indicators.get("rsi", {})
print(f"  RSI: {rsi.get('value', 'N/A')} ({rsi.get('signal', 'N/A')})")
print(f"  Trend: {tech.summary.get('trend', 'N/A')}")

# ─── 7. News ─────────────────────────────────────────────────────
print("\n=== Latest News ===")
articles = client.news.list("AAPL")
for article in articles[:3]:
    print(f"  • {article.title[:70]}")

# ─── 8. Sentiment Analysis ───────────────────────────────────────
print("\n=== Sentiment ===")
sentiment = client.sentiment.get("AAPL")
print(f"  Score: {sentiment.sentiment_score} | Signal: {sentiment.signal}")
print(f"  Trend: {sentiment.sentiment_trend}")
if sentiment.social_sentiment:
    print(f"  Social Mentions (24h): {sentiment.social_sentiment.mentions_24h}")

# ─── 9. Analyst Consensus ────────────────────────────────────────
print("\n=== Analyst Consensus ===")
analyst = client.analyst.consensus("AAPL")
print(f"  Rating: {analyst.consensus} (Signal: {analyst.signal})")
print(f"  Analysts: {analyst.total_analysts}")

# ─── 10. Price Targets ───────────────────────────────────────────
print("\n=== Price Targets ===")
targets = client.analyst.price_targets("AAPL")
pt = targets[0]
print(f"  High: ${pt.target_high:.0f} | Mean: ${pt.target_mean:.0f} | Low: ${pt.target_low:.0f}")

# ─── 11. Upgrades/Downgrades ─────────────────────────────────────
print("\n=== Recent Upgrades/Downgrades ===")
ratings = client.analyst.ratings("AAPL")
for r in ratings[:3]:
    print(f"  {r.date[:10]}: {r.firm} → {r.to_grade} ({r.action})")

# ─── 12. Earnings ────────────────────────────────────────────────
print("\n=== Earnings History ===")
earnings = client.earnings.history("AAPL")
for e in earnings[:4]:
    surprise = f" (surprise: {e.eps_surprise_pct:+.1f}%)" if e.eps_surprise_pct else ""
    print(f"  {e.date}: EPS ${e.eps_actual:.2f} vs est ${e.eps_estimate:.2f}{surprise}")

# ─── 13. Insider Transactions ────────────────────────────────────
print("\n=== Insider Activity ===")
trades = client.insider.transactions("AAPL")
for t in trades[:3]:
    print(f"  {t.transaction_date[:10]}: {t.insider_name} — {t.transaction_type} {t.shares:,} shares (${t.total_value:,.0f})")

# ─── 14. Options Chain ───────────────────────────────────────────
print("\n=== Options Chain ===")
chain = client.options.chain("AAPL")
print(f"  Expiration: {chain.expiration}")
print(f"  Calls: {len(chain.calls)} | Puts: {len(chain.puts)}")

# ─── 15. Historical Prices ───────────────────────────────────────
print("\n=== Historical Prices (5 day) ===")
hist = client.historical.get("AAPL", period="5d")
print(f"  {len(hist.history)} bars loaded")
if hist.history:
    last = hist.history[-1]
    print(f"  Latest: {last.timestamp[:16]} Close=${last.close:.2f}")

# ─── 16. ETF Data ────────────────────────────────────────────────
print("\n=== ETF Data ===")
etf = client.etf.get("SPY")
print(f"  {etf.name}")
print(f"  NAV: ${etf.nav_price:.2f} | YTD: {etf.ytd_return:.2f}%")
print(f"  Total Assets: ${etf.total_assets/1e9:.1f}B")
