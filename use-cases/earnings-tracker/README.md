# Earnings Tracker

Monitors your portfolio companies' earnings calendar and sends alerts before and after earnings releases.

## Features

- Scans upcoming earnings calendar for your watchlist
- Shows EPS and revenue estimates
- Registers webhooks for real-time earnings notifications
- Can forward to Slack/Discord/Telegram

## Usage

```bash
pip install vectrade
export VECTRADE_API_KEY=your_key

python main.py
```

## Sample Output

```
Symbol   Date         Time            EPS Est    Rev Est
------------------------------------------------------------
AAPL     2026-07-24   after_market    $1.58      $95.4B
NVDA     2026-08-20   after_market    $0.82      $28.1B
```
