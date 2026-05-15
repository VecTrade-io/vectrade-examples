# Momentum Scanner

Screens the market for stocks exhibiting strong price momentum, then runs technical analysis on the top candidates.

## Features

- Market-wide screening with configurable filters
- Paginated results for large result sets
- Technical indicator analysis on top picks
- Combines VecTrade API with FinKit local computation

## Usage

```bash
pip install vectrade finkit
export VECTRADE_API_KEY=your_key

python main.py
```

## Customization

Edit the filter criteria in `main.py`:
- `market_cap_min`: Minimum market cap
- `avg_volume_min`: Minimum average daily volume
- `change_pct_min`: Minimum daily price change %
