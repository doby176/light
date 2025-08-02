#!/usr/bin/env python3
"""
ThinkorSwim Trading Analysis - One Simple Script
Just run this and get all your trading metrics!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

def parse_pl(pl_str):
    """Parse P&L string to float"""
    if not pl_str or str(pl_str).strip() == '':
        return 0.0
    pl_str = str(pl_str).replace('$', '').replace(',', '').replace('(', '').replace(')', '').replace('\t', '')
    try:
        return float(pl_str)
    except:
        return 0.0

def analyze_trades():
    print("🎯 ThinkorSwim Trading Analysis")
    print("=" * 50)
    
    # File paths
    long_file = r"C:\Users\ASUS\StrategyReports_QQQ_8225long1.csv"
    short_file = r"C:\Users\ASUS\StrategyReports_QQQ_8225short.csv"
    
    # Check files exist
    if not os.path.exists(long_file):
        print(f"❌ Long file not found: {long_file}")
        return
    if not os.path.exists(short_file):
        print(f"❌ Short file not found: {short_file}")
        return
    
    print("✅ Files found! Analyzing...")
    
    # Load and parse data
    all_trades = []
    
    for file_path, strategy_type in [(long_file, 'Long'), (short_file, 'Short')]:
        try:
            print(f"Reading {file_path}...")
            
            # Read file as text and parse manually
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"File has {len(lines)} lines")
            
            # Skip first 6 lines (header info) and parse from line 7
            data_lines = lines[6:]  # Start from line 7 (index 6)
            
            for line_num, line in enumerate(data_lines, start=7):
                line = line.strip()
                if not line or line.startswith('Total'):  # Skip empty lines and totals
                    continue
                
                # Parse semicolon-separated data
                if ';' in line:
                    parts = line.split(';')
                    if len(parts) >= 9:  # Expected: Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
                        try:
                            trade_id = int(parts[0])
                            strategy = parts[1]
                            side = parts[2]
                            amount = float(parts[3])
                            
                            # Clean price (remove $, commas, tabs)
                            price_str = parts[4].replace('$', '').replace(',', '').replace('\t', '')
                            price = float(price_str)
                            
                            datetime_str = parts[5]
                            trade_pl_str = parts[6]
                            cumulative_pl_str = parts[7]
                            position = float(parts[8])
                            
                            # Parse datetime
                            dt = pd.to_datetime(datetime_str, format='%m/%d/%y %I:%M %p')
                            
                            # Parse P&L
                            trade_pl = parse_pl(trade_pl_str)
                            
                            all_trades.append({
                                'id': trade_id,
                                'strategy': strategy_type,
                                'side': side,
                                'price': price,
                                'datetime': dt,
                                'trade_pl': trade_pl,
                                'amount': abs(amount)
                            })
                            
                        except Exception as e:
                            print(f"Warning: Could not parse line {line_num}: {line[:50]}... Error: {e}")
                            continue
            
            print(f"Parsed {len([t for t in all_trades if t['strategy'] == strategy_type])} {strategy_type} trades")
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    if not all_trades:
        print("❌ No valid trades found!")
        return
    
    print(f"✅ Successfully parsed {len(all_trades)} total trades")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_trades)
    
    # Create trade pairs (entry/exit)
    trades = []
    i = 0
    while i < len(df) - 1:
        entry = df.iloc[i]
        exit = df.iloc[i + 1]
        
        # Calculate trade metrics
        duration = (exit['datetime'] - entry['datetime']).total_seconds() / 60  # minutes
        return_pct = ((exit['price'] - entry['price']) / entry['price']) * 100
        
        trades.append({
            'strategy': entry['strategy'],
            'entry_price': entry['price'],
            'exit_price': exit['price'],
            'entry_time': entry['datetime'],
            'exit_time': exit['datetime'],
            'trade_pl': exit['trade_pl'],
            'duration': duration,
            'return_pct': return_pct,
            'amount': entry['amount']
        })
        i += 2
    
    if not trades:
        print("❌ No completed trades found!")
        return
    
    trades_df = pd.DataFrame(trades)
    
    # Calculate metrics
    total_trades = len(trades_df)
    winning_trades = trades_df[trades_df['trade_pl'] > 0]
    losing_trades = trades_df[trades_df['trade_pl'] < 0]
    
    total_pnl = trades_df['trade_pl'].sum()
    win_rate = len(winning_trades) / total_trades * 100
    avg_winner = winning_trades['trade_pl'].mean() if len(winning_trades) > 0 else 0
    avg_loser = losing_trades['trade_pl'].mean() if len(losing_trades) > 0 else 0
    
    # Profit factor
    gross_profit = winning_trades['trade_pl'].sum() if len(winning_trades) > 0 else 0
    gross_loss = abs(losing_trades['trade_pl'].sum()) if len(losing_trades) > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Max drawdown
    cumulative = trades_df['trade_pl'].cumsum()
    running_max = cumulative.expanding().max()
    drawdown = cumulative - running_max
    max_drawdown = abs(drawdown.min())
    
    # Strategy breakdown
    long_trades = trades_df[trades_df['strategy'] == 'Long']
    short_trades = trades_df[trades_df['strategy'] == 'Short']
    
    long_pnl = long_trades['trade_pl'].sum() if len(long_trades) > 0 else 0
    short_pnl = short_trades['trade_pl'].sum() if len(short_trades) > 0 else 0
    long_win_rate = len(long_trades[long_trades['trade_pl'] > 0]) / len(long_trades) * 100 if len(long_trades) > 0 else 0
    short_win_rate = len(short_trades[short_trades['trade_pl'] > 0]) / len(short_trades) * 100 if len(short_trades) > 0 else 0
    
    # Time analysis
    trades_df['hour'] = trades_df['entry_time'].dt.hour
    trades_df['day'] = trades_df['entry_time'].dt.day_name()
    
    hourly_pnl = trades_df.groupby('hour')['trade_pl'].sum()
    daily_pnl = trades_df.groupby('day')['trade_pl'].sum()
    
    best_hour = hourly_pnl.idxmax() if not hourly_pnl.empty else None
    worst_hour = hourly_pnl.idxmin() if not hourly_pnl.empty else None
    best_day = daily_pnl.idxmax() if not daily_pnl.empty else None
    worst_day = daily_pnl.idxmin() if not daily_pnl.empty else None
    
    # Print results
    print("\n" + "=" * 80)
    print("📊 TRADING ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"\n💰 OVERALL PERFORMANCE:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Total P&L: ${total_pnl:,.2f}")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Profit Factor: {profit_factor:.2f}")
    print(f"   Max Drawdown: ${max_drawdown:,.2f}")
    
    print(f"\n📈 TRADE METRICS:")
    print(f"   Average Winner: ${avg_winner:.2f}")
    print(f"   Average Loser: ${avg_loser:.2f}")
    print(f"   Average Trade: ${trades_df['trade_pl'].mean():.2f}")
    print(f"   Average Duration: {trades_df['duration'].mean():.1f} minutes")
    
    print(f"\n🎯 STRATEGY BREAKDOWN:")
    print(f"   Long Strategy:")
    print(f"     Trades: {len(long_trades)}")
    print(f"     P&L: ${long_pnl:,.2f}")
    print(f"     Win Rate: {long_win_rate:.1f}%")
    
    print(f"   Short Strategy:")
    print(f"     Trades: {len(short_trades)}")
    print(f"     P&L: ${short_pnl:,.2f}")
    print(f"     Win Rate: {short_win_rate:.1f}%")
    
    print(f"\n⏰ TIME ANALYSIS:")
    if best_hour is not None:
        print(f"   Best Hour: {best_hour}:00 (${hourly_pnl[best_hour]:.0f})")
        print(f"   Worst Hour: {worst_hour}:00 (${hourly_pnl[worst_hour]:.0f})")
    if best_day is not None:
        print(f"   Best Day: {best_day} (${daily_pnl[best_day]:.0f})")
        print(f"   Worst Day: {worst_day} (${daily_pnl[worst_day]:.0f})")
    
    # Create charts
    print(f"\n📊 Creating charts...")
    
    # Cumulative P&L chart
    plt.figure(figsize=(12, 6))
    cumulative_pnl = trades_df['trade_pl'].cumsum()
    plt.plot(trades_df['entry_time'], cumulative_pnl, linewidth=2, color='blue')
    plt.title('Cumulative P&L Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Cumulative P&L ($)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('cumulative_pnl.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # P&L distribution
    plt.figure(figsize=(10, 6))
    plt.hist(trades_df['trade_pl'], bins=30, alpha=0.7, color='green', edgecolor='black')
    plt.axvline(trades_df['trade_pl'].mean(), color='red', linestyle='--', 
                label=f'Mean: ${trades_df["trade_pl"].mean():.2f}')
    plt.title('Trade P&L Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('P&L ($)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('pnl_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Strategy comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # P&L by strategy
    strategies = ['Long', 'Short']
    pnls = [long_pnl, short_pnl]
    colors = ['green', 'red']
    ax1.bar(strategies, pnls, color=colors, alpha=0.7)
    ax1.set_title('P&L by Strategy', fontweight='bold')
    ax1.set_ylabel('P&L ($)')
    for i, v in enumerate(pnls):
        ax1.text(i, v + (10 if v >= 0 else -10), f'${v:.0f}', ha='center', fontweight='bold')
    
    # Win rate by strategy
    win_rates = [long_win_rate, short_win_rate]
    ax2.bar(strategies, win_rates, color=colors, alpha=0.7)
    ax2.set_title('Win Rate by Strategy', fontweight='bold')
    ax2.set_ylabel('Win Rate (%)')
    ax2.set_ylim(0, 100)
    for i, v in enumerate(win_rates):
        ax2.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save detailed report
    with open('trading_report.txt', 'w') as f:
        f.write("THINKORSWIM TRADING ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Trades: {total_trades}\n")
        f.write(f"Total P&L: ${total_pnl:,.2f}\n")
        f.write(f"Win Rate: {win_rate:.1f}%\n")
        f.write(f"Profit Factor: {profit_factor:.2f}\n")
        f.write(f"Max Drawdown: ${max_drawdown:,.2f}\n")
        f.write(f"Average Winner: ${avg_winner:.2f}\n")
        f.write(f"Average Loser: ${avg_loser:.2f}\n")
        f.write(f"Long Strategy P&L: ${long_pnl:,.2f}\n")
        f.write(f"Short Strategy P&L: ${short_pnl:,.2f}\n")
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📁 Generated files:")
    print(f"   • cumulative_pnl.png")
    print(f"   • pnl_distribution.png") 
    print(f"   • strategy_comparison.png")
    print(f"   • trading_report.txt")
    print(f"\n📊 Key Metrics:")
    print(f"   • Average Winner: ${avg_winner:.2f}")
    print(f"   • Average Loser: ${avg_loser:.2f}")
    print(f"   • Profit Factor: {profit_factor:.2f}")
    print(f"   • Max Drawdown: ${max_drawdown:,.2f}")
    print(f"   • Win Rate: {win_rate:.1f}%")

if __name__ == "__main__":
    analyze_trades()