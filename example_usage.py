#!/usr/bin/env python3
"""
Example Usage of Bullish Order Block Trading Bot
Demonstrates different ways to use the trading bot
"""

from trading_bot import BullishOrderBlockBot
from trading_config import TradingConfig
import pandas as pd
from datetime import datetime, timedelta

def example_1_basic_backtest():
    """Example 1: Basic backtest with default settings"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Backtest")
    print("=" * 60)
    
    # Initialize bot with default settings
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        initial_capital=10000.0,
        position_size=0.1
    )
    
    # Run backtest for last 30 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Running backtest from {start_date} to {end_date}")
    bot.run_backtest(start_date, end_date)

def example_2_custom_parameters():
    """Example 2: Custom parameters for different risk tolerance"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Conservative Parameters")
    print("=" * 60)
    
    # Conservative bot with smaller position size
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        initial_capital=50000.0,  # More capital
        position_size=0.05        # Smaller position size (5%)
    )
    
    # Run backtest for last 60 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    print(f"Running conservative backtest from {start_date} to {end_date}")
    bot.run_backtest(start_date, end_date)

def example_3_different_symbol():
    """Example 3: Testing with different symbol (SPY)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Different Symbol (SPY)")
    print("=" * 60)
    
    # Test with SPY instead of QQQ
    bot = BullishOrderBlockBot(
        symbol="SPY",             # S&P 500 ETF
        initial_capital=10000.0,
        position_size=0.1
    )
    
    # Run backtest for last 30 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Running SPY backtest from {start_date} to {end_date}")
    bot.run_backtest(start_date, end_date)

def example_4_aggressive_parameters():
    """Example 4: Aggressive parameters for higher risk/reward"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Aggressive Parameters")
    print("=" * 60)
    
    # Aggressive bot with larger position size
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        initial_capital=10000.0,
        position_size=0.2         # Larger position size (20%)
    )
    
    # Run backtest for last 30 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Running aggressive backtest from {start_date} to {end_date}")
    bot.run_backtest(start_date, end_date)

def example_5_live_simulation():
    """Example 5: Live trading simulation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Live Trading Simulation")
    print("=" * 60)
    print("⚠️  This will run for 5 minutes with 30-second updates")
    print("Press Ctrl+C to stop early")
    print("-" * 60)
    
    # Live simulation bot
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        initial_capital=10000.0,
        position_size=0.1
    )
    
    # Run for 5 minutes with 30-second updates
    try:
        import time
        start_time = time.time()
        while time.time() - start_time < 300:  # 5 minutes
            bot.run_live(update_interval=30)
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n🛑 Live simulation stopped by user")

def example_6_compare_strategies():
    """Example 6: Compare different position sizes"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Strategy Comparison")
    print("=" * 60)
    
    # Test different position sizes
    position_sizes = [0.05, 0.1, 0.15, 0.2]
    results = []
    
    for pos_size in position_sizes:
        print(f"\nTesting position size: {pos_size*100}%")
        
        bot = BullishOrderBlockBot(
            symbol="QQQ",
            initial_capital=10000.0,
            position_size=pos_size
        )
        
        # Run backtest for last 30 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        bot.run_backtest(start_date, end_date)
        
        # Store results
        results.append({
            'position_size': pos_size,
            'total_pnl': bot.total_pnl,
            'win_rate': bot.win_count/(bot.win_count + bot.loss_count)*100 if (bot.win_count + bot.loss_count) > 0 else 0,
            'total_trades': len(bot.trades)
        })
    
    # Print comparison
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON RESULTS")
    print("=" * 80)
    print(f"{'Position Size':<15} {'Total P&L':<15} {'Win Rate':<15} {'Total Trades':<15}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['position_size']*100:>5}%{'':<10} "
              f"${result['total_pnl']:>10,.2f}{'':<5} "
              f"{result['win_rate']:>8.1f}%{'':<7} "
              f"{result['total_trades']:>10}")

def example_7_custom_date_range():
    """Example 7: Custom date range backtest"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Custom Date Range")
    print("=" * 60)
    
    # Test specific date range (e.g., market volatility period)
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        initial_capital=10000.0,
        position_size=0.1
    )
    
    # Test during a specific period (e.g., March 2024)
    start_date = "2024-03-01"
    end_date = "2024-03-31"
    
    print(f"Running backtest for March 2024: {start_date} to {end_date}")
    bot.run_backtest(start_date, end_date)

def main():
    """Main function to run examples"""
    print("🐂 BULLISH ORDER BLOCK TRADING BOT - EXAMPLES")
    print("=" * 60)
    print("This script demonstrates different ways to use the trading bot.")
    print("Each example shows different configurations and use cases.")
    print("=" * 60)
    
    # List available examples
    examples = [
        ("Basic Backtest", example_1_basic_backtest),
        ("Conservative Parameters", example_2_custom_parameters),
        ("Different Symbol (SPY)", example_3_different_symbol),
        ("Aggressive Parameters", example_4_aggressive_parameters),
        ("Live Simulation", example_5_live_simulation),
        ("Strategy Comparison", example_6_compare_strategies),
        ("Custom Date Range", example_7_custom_date_range)
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\nEnter example number (1-7) or 'all' to run all examples:")
    choice = input("Choice: ").strip().lower()
    
    if choice == "all":
        # Run all examples
        for name, func in examples:
            try:
                func()
                input("\nPress Enter to continue to next example...")
            except Exception as e:
                print(f"❌ Error in {name}: {e}")
                input("\nPress Enter to continue...")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        # Run specific example
        idx = int(choice) - 1
        name, func = examples[idx]
        try:
            func()
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
    else:
        print("❌ Invalid choice. Please enter 1-7 or 'all'.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Examples stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")