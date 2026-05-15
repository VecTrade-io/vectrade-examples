"""Portfolio Analysis with finkit — No VecTrade account required."""

import pandas as pd
import numpy as np

# finkit works standalone — no API key needed
import finkit
from finkit import Rule, screen


def main():
    # Simulate portfolio returns (in production, use vectrade SDK to fetch real data)
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=252, freq="B")
    portfolio_returns = pd.Series(np.random.normal(0.0005, 0.015, 252), index=dates)
    equity_curve = (1 + portfolio_returns).cumprod()

    print("=== Portfolio Risk Metrics ===\n")

    sharpe = finkit.sharpe_ratio(portfolio_returns)
    sortino = finkit.sortino_ratio(portfolio_returns)
    mdd = finkit.max_drawdown(equity_curve)
    value_at_risk = finkit.var(portfolio_returns, confidence=0.95)

    print(f"  Sharpe Ratio:      {sharpe:.3f}")
    print(f"  Sortino Ratio:     {sortino:.3f}")
    print(f"  Max Drawdown:      {mdd:.2%}")
    print(f"  VaR (95%):         {value_at_risk:.4f}")

    # Technical analysis on a stock
    print("\n=== Technical Indicators (simulated AAPL) ===\n")

    prices = pd.Series(
        150 + np.cumsum(np.random.normal(0.1, 2, 100)),
        index=pd.date_range("2024-06-01", periods=100, freq="B"),
    )

    rsi_values = finkit.rsi(prices, period=14)
    sma_20 = finkit.sma(prices, period=20)
    upper, middle, lower = finkit.bollinger_bands(prices)

    print(f"  Current Price:     ${prices.iloc[-1]:.2f}")
    print(f"  RSI (14):          {rsi_values.iloc[-1]:.1f}")
    print(f"  SMA (20):          ${sma_20.iloc[-1]:.2f}")
    print(f"  Bollinger Upper:   ${upper.iloc[-1]:.2f}")
    print(f"  Bollinger Lower:   ${lower.iloc[-1]:.2f}")

    # Screening
    print("\n=== Stock Screener ===\n")

    universe = pd.DataFrame({
        "symbol": ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "TSLA", "BRK.B"],
        "pe_ratio": [28, 22, 35, 45, 18, 60, 55, 15],
        "market_cap": [3e12, 2e12, 3.1e12, 1.9e12, 1.3e12, 3.5e12, 0.8e12, 0.9e12],
        "dividend_yield": [0.5, 0.0, 0.7, 0.0, 0.3, 0.0, 0.0, 0.0],
        "rsi_14": [55, 42, 68, 38, 45, 72, 30, 50],
    })

    results = screen(universe, rules=[
        Rule("pe_ratio", "<", 40),
        Rule("market_cap", ">", 1e12),
        Rule("rsi_14", "between", (30, 65)),
    ])

    print(f"  Matches: {len(results)} of {len(universe)} stocks")
    for _, row in results.iterrows():
        print(f"    {row['symbol']:6s} | PE: {row['pe_ratio']:5.1f} | RSI: {row['rsi_14']:.0f}")


if __name__ == "__main__":
    main()
