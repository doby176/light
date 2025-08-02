#!/bin/bash

# Bullish Order Block Trading Bot Startup Script
# This script activates the virtual environment and starts the trading bot

echo "🐂 Bullish Order Block Trading Bot"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "trading_env" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv trading_env
    source trading_env/bin/activate
    pip install pandas numpy yfinance
    echo "✅ Virtual environment created and dependencies installed."
else
    echo "✅ Virtual environment found."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source trading_env/bin/activate

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import pandas, numpy, yfinance; print('✅ All dependencies are installed')" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install pandas numpy yfinance
    echo "✅ Dependencies installed."
}

# Start the trading bot
echo "🚀 Starting trading bot..."
echo "Press Ctrl+C to stop the bot"
echo "=================================="

python3 run_bot.py