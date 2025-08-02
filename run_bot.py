#!/usr/bin/env python3
"""
Bullish Order Block Trading Bot Launcher
A simple interface to run the trading bot with different configurations
"""

import sys
import os
from datetime import datetime, timedelta
from trading_bot import BullishOrderBlockBot
from trading_config import TradingConfig, BullishOrderBlockConfig

def print_banner():
    """Print the bot banner"""
    print("=" * 60)
    print("🐂 BULLISH ORDER BLOCK TRADING BOT 🐂")
    print("=" * 60)
    print("Strategy: Bullish Order Block Detection with Auto-Cycling")
    print("Symbol: QQQ (NASDAQ-100 ETF)")
    print("Timeframe: 1-minute")
    print("=" * 60)

def get_user_input():
    """Get user input for bot configuration"""
    print("\n📊 TRADING BOT CONFIGURATION")
    print("-" * 40)
    
    # Symbol
    symbol = input(f"Trading Symbol (default: {TradingConfig.SYMBOL}): ").strip()
    if not symbol:
        symbol = TradingConfig.SYMBOL
    
    # Capital
    while True:
        try:
            capital_input = input(f"Initial Capital (default: ${TradingConfig.INITIAL_CAPITAL:,.2f}): ").strip()
            if not capital_input:
                capital = TradingConfig.INITIAL_CAPITAL
                break
            capital = float(capital_input)
            if capital > 0:
                break
            else:
                print("❌ Capital must be greater than 0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Position size
    while True:
        try:
            pos_size_input = input(f"Position Size % (default: {TradingConfig.POSITION_SIZE*100}%): ").strip()
            if not pos_size_input:
                position_size = TradingConfig.POSITION_SIZE
                break
            position_size = float(pos_size_input) / 100
            if 0 < position_size <= 1:
                break
            else:
                print("❌ Position size must be between 0% and 100%")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return symbol, capital, position_size

def run_backtest_mode():
    """Run the bot in backtest mode"""
    print("\n🔍 BACKTEST MODE")
    print("-" * 20)
    
    # Get configuration
    symbol, capital, position_size = get_user_input()
    
    # Date range
    print("\n📅 BACKTEST DATE RANGE")
    print("-" * 25)
    
    # Start date
    while True:
        start_date = input(f"Start Date (YYYY-MM-DD, default: {TradingConfig.BACKTEST_START_DATE}): ").strip()
        if not start_date:
            start_date = TradingConfig.BACKTEST_START_DATE
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Please enter a valid date in YYYY-MM-DD format")
    
    # End date
    while True:
        end_date = input(f"End Date (YYYY-MM-DD, default: {TradingConfig.BACKTEST_END_DATE}): ").strip()
        if not end_date:
            end_date = TradingConfig.BACKTEST_END_DATE
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Please enter a valid date in YYYY-MM-DD format")
    
    # Initialize and run bot
    print(f"\n🚀 Starting backtest for {symbol} from {start_date} to {end_date}")
    print(f"💰 Initial Capital: ${capital:,.2f}")
    print(f"📈 Position Size: {position_size*100}%")
    print("-" * 50)
    
    bot = BullishOrderBlockBot(
        symbol=symbol,
        timeframe=TradingConfig.TIMEFRAME,
        initial_capital=capital,
        position_size=position_size
    )
    
    try:
        bot.run_backtest(start_date, end_date)
    except Exception as e:
        print(f"❌ Error during backtest: {e}")
        return False
    
    return True

def run_live_mode():
    """Run the bot in live mode"""
    print("\n⚡ LIVE TRADING MODE")
    print("-" * 20)
    print("⚠️  WARNING: This is a simulation mode. No real money is at risk.")
    print("⚠️  For real trading, additional broker integration is required.")
    print("-" * 50)
    
    # Get configuration
    symbol, capital, position_size = get_user_input()
    
    # Update interval
    while True:
        try:
            interval_input = input(f"Update Interval in seconds (default: {TradingConfig.UPDATE_INTERVAL}): ").strip()
            if not interval_input:
                update_interval = TradingConfig.UPDATE_INTERVAL
                break
            update_interval = int(interval_input)
            if update_interval > 0:
                break
            else:
                print("❌ Update interval must be greater than 0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Initialize and run bot
    print(f"\n🚀 Starting live trading simulation for {symbol}")
    print(f"💰 Initial Capital: ${capital:,.2f}")
    print(f"📈 Position Size: {position_size*100}%")
    print(f"⏱️  Update Interval: {update_interval} seconds")
    print("-" * 50)
    print("Press Ctrl+C to stop the bot")
    print("-" * 50)
    
    bot = BullishOrderBlockBot(
        symbol=symbol,
        timeframe=TradingConfig.TIMEFRAME,
        initial_capital=capital,
        position_size=position_size
    )
    
    try:
        bot.run_live(update_interval)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error during live trading: {e}")
        return False
    
    return True

def show_strategy_info():
    """Show information about the strategy"""
    print("\n📚 STRATEGY INFORMATION")
    print("=" * 50)
    print("🐂 BULLISH ORDER BLOCK STRATEGY")
    print("-" * 30)
    print("This strategy identifies bullish order blocks on 1-minute charts")
    print("and implements an automatic long/short cycling system.")
    print()
    print("🔍 SIGNAL DETECTION:")
    print("• Green Dot: Bullish Order Block detected")
    print("• Red Dot: Price closes below bullish order block level")
    print()
    print("🔄 TRADING CYCLE:")
    print("1. Enter LONG when green dot appears")
    print("2. Exit LONG and enter SHORT when red dot appears")
    print("3. Exit SHORT and enter LONG when price hits green dot level")
    print("4. Repeat cycle indefinitely")
    print()
    print("⚙️  RISK MANAGEMENT:")
    print("• Position sizing based on capital percentage")
    print("• Stop losses at order block levels")
    print("• Automatic position cycling")
    print()
    print("📊 PERFORMANCE METRICS:")
    print("• Total P&L tracking")
    print("• Win rate calculation")
    print("• Trade history logging")
    print("• Risk-adjusted returns")
    print("=" * 50)

def main():
    """Main function"""
    print_banner()
    
    while True:
        print("\n🎯 SELECT MODE:")
        print("1. 📊 Run Backtest")
        print("2. ⚡ Run Live Trading (Simulation)")
        print("3. 📚 Strategy Information")
        print("4. ⚙️  Configuration")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            success = run_backtest_mode()
            if success:
                input("\nPress Enter to continue...")
        
        elif choice == "2":
            success = run_live_mode()
            if success:
                input("\nPress Enter to continue...")
        
        elif choice == "3":
            show_strategy_info()
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            show_configuration()
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            print("\n👋 Thank you for using the Bullish Order Block Trading Bot!")
            print("Good luck with your trading! 🚀")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def show_configuration():
    """Show current configuration"""
    print("\n⚙️  CURRENT CONFIGURATION")
    print("=" * 40)
    print(f"Symbol: {TradingConfig.SYMBOL}")
    print(f"Timeframe: {TradingConfig.TIMEFRAME}")
    print(f"Initial Capital: ${TradingConfig.INITIAL_CAPITAL:,.2f}")
    print(f"Position Size: {TradingConfig.POSITION_SIZE*100}%")
    print(f"Max Position Size: {TradingConfig.MAX_POSITION_SIZE*100}%")
    print(f"Default Stop Loss: {TradingConfig.DEFAULT_STOP_LOSS_PCT*100}%")
    print(f"Trailing Stop: {'Enabled' if TradingConfig.TRAILING_STOP else 'Disabled'}")
    print(f"Enable Shorting: {'Yes' if TradingConfig.ENABLE_SHORTING else 'No'}")
    print(f"Auto Cycle: {'Yes' if TradingConfig.AUTO_CYCLE else 'No'}")
    print(f"Update Interval: {TradingConfig.UPDATE_INTERVAL} seconds")
    print(f"Data Source: {TradingConfig.DATA_SOURCE}")
    print(f"Log Level: {TradingConfig.LOG_LEVEL}")
    print("=" * 40)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)