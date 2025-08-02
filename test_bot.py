#!/usr/bin/env python3
"""
Quick Test of Bullish Order Block Trading Bot
This script runs a quick backtest to verify the bot is working correctly
"""

from trading_bot import BullishOrderBlockBot
from datetime import datetime, timedelta

def test_bot():
    """Run a quick test of the trading bot"""
    print("🐂 Testing Bullish Order Block Trading Bot")
    print("=" * 50)
    
    # Initialize bot with small capital for testing
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        initial_capital=1000.0,  # Small amount for testing
        position_size=0.1
    )
    
    # Test with last 7 days of data
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"Running quick test from {start_date} to {end_date}")
    print(f"Symbol: QQQ")
    print(f"Initial Capital: $1,000")
    print(f"Position Size: 10%")
    print("-" * 50)
    
    try:
        # Run the backtest
        bot.run_backtest(start_date, end_date)
        
        print("\n✅ Test completed successfully!")
        print("The trading bot is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_bot()