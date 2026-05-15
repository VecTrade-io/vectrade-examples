# VecTrade Python Project Template

A minimal Python project structure for building applications with the VecTrade SDK.

## Quick Start

```bash
# Clone this template
cp -r templates/python-project my-project
cd my-project

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set your API key
export VECTRADE_API_KEY=your_key_here

# Run
python main.py
```

## Project Structure

```
my-project/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── README.md
```
