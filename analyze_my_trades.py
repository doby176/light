#!/usr/bin/env python3
"""
ThinkorSwim Trading Analysis Tool
Just paste your data and run!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def parse_thinkorswim_data(report_text):
    """Parse ThinkorSwim report text into DataFrame"""
    lines = report_text.strip().split('\n')
    
    trades = []
    for line in lines:
        if ';' in line and any(char.isdigit() for char in line):
            parts = line.split(';')
            if len(parts) >= 9 and parts[0].strip().isdigit():
                try:
                    # Parse trade data
                    trade_id = int(parts[0])
                    strategy = parts[1]
                    side = parts[2]
                    amount = float(parts[3])
                    price = float(parts[4].replace('$', '').replace(',', ''))
                    
                    # Parse datetime
                    datetime_str = parts[5].strip()
                    trade_datetime = datetime.strptime(datetime_str, '%m/%d/%y %I:%M %p')
                    
                    # Parse P&L
                    trade_pl_str = parts[6].strip()
                    cumulative_pl_str = parts[7].strip()
                    
                    # Convert P&L strings to numbers
                    trade_pl = parse_pl_string(trade_pl_str)
                    cumulative_pl = parse_pl_string(cumulative_pl_str)
                    
                    position = float(parts[8])
                    
                    trades.append({
                        'id': trade_id,
                        'strategy': strategy,
                        'side': side,
                        'amount': amount,
                        'price': price,
                        'datetime': trade_datetime,
                        'trade_pl': trade_pl,
                        'cumulative_pl': cumulative_pl,
                        'position': position
                    })
                except Exception as e:
                    print(f"Warning: Could not parse line: {line[:50]}... Error: {e}")
                    continue
    
    return pd.DataFrame(trades)

def parse_pl_string(pl_str):
    """Parse P&L string to float"""
    if not pl_str or pl_str.strip() == '':
        return 0.0
    
    pl_str = pl_str.strip()
    # Remove $ and commas
    pl_str = pl_str.replace('$', '').replace(',', '')
    
    # Handle parentheses (negative values)
    if pl_str.startswith('(') and pl_str.endswith(')'):
        return -float(pl_str[1:-1])
    else:
        return float(pl_str)

def calculate_comprehensive_metrics(data):
    """Calculate comprehensive trading metrics"""
    if data.empty:
        return {}
    
    # Filter completed trades
    completed_trades = data[data['trade_pl'] != 0].copy()
    
    if completed_trades.empty:
        return {}
    
    # Basic metrics
    total_trades = len(completed_trades)
    winning_trades = completed_trades[completed_trades['trade_pl'] > 0]
    losing_trades = completed_trades[completed_trades['trade_pl'] < 0]
    
    total_pl = completed_trades['trade_pl'].sum()
    gross_profit = winning_trades['trade_pl'].sum() if not winning_trades.empty else 0
    gross_loss = abs(losing_trades['trade_pl'].sum()) if not losing_trades.empty else 0
    
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
    avg_winner = winning_trades['trade_pl'].mean() if not winning_trades.empty else 0
    avg_loser = losing_trades['trade_pl'].mean() if not losing_trades.empty else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Risk metrics
    max_winner = completed_trades['trade_pl'].max()
    max_loser = completed_trades['trade_pl'].min()
    
    # Calculate drawdown
    cumulative_pl = completed_trades['cumulative_pl'].values
    running_max = np.maximum.accumulate(cumulative_pl)
    drawdown = cumulative_pl - running_max
    max_drawdown = drawdown.min()
    
    # Advanced metrics
    sharpe_ratio = np.mean(completed_trades['trade_pl']) / np.std(completed_trades['trade_pl']) if np.std(completed_trades['trade_pl']) > 0 else 0
    
    # Expectancy
    expectancy = (win_rate * avg_winner) + ((1 - win_rate) * avg_loser)
    
    # Recovery factor
    recovery_factor = total_pl / abs(max_drawdown) if max_drawdown != 0 else float('inf')
    
    # Consecutive wins/losses
    completed_trades['is_win'] = completed_trades['trade_pl'] > 0
    completed_trades['streak'] = (completed_trades['is_win'] != completed_trades['is_win'].shift()).cumsum()
    
    win_streaks = completed_trades[completed_trades['is_win']].groupby('streak').size()
    loss_streaks = completed_trades[~completed_trades['is_win']].groupby('streak').size()
    
    max_win_streak = win_streaks.max() if not win_streaks.empty else 0
    max_loss_streak = loss_streaks.max() if not loss_streaks.empty else 0
    
    # Time-based analysis
    completed_trades['hour'] = completed_trades['datetime'].dt.hour
    completed_trades['day_of_week'] = completed_trades['datetime'].dt.day_name()
    
    hourly_pl = completed_trades.groupby('hour')['trade_pl'].sum()
    daily_pl = completed_trades.groupby('day_of_week')['trade_pl'].sum()
    
    best_hour = hourly_pl.idxmax() if not hourly_pl.empty else None
    worst_hour = hourly_pl.idxmin() if not hourly_pl.empty else None
    best_day = daily_pl.idxmax() if not daily_pl.empty else None
    worst_day = daily_pl.idxmin() if not daily_pl.empty else None
    
    return {
        'total_trades': total_trades,
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': win_rate,
        'total_pl': total_pl,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'avg_winner': avg_winner,
        'avg_loser': avg_loser,
        'profit_factor': profit_factor,
        'max_winner': max_winner,
        'max_loser': max_loser,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'expectancy': expectancy,
        'recovery_factor': recovery_factor,
        'max_win_streak': max_win_streak,
        'max_loss_streak': max_loss_streak,
        'best_hour': best_hour,
        'worst_hour': worst_hour,
        'best_day': best_day,
        'worst_day': worst_day
    }

def print_comprehensive_report(metrics, strategy_name):
    """Print comprehensive trading report"""
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE TRADING ANALYSIS - {strategy_name.upper()}")
    print(f"{'='*80}")
    
    if not metrics:
        print("No completed trades found for analysis.")
        return
    
    print(f"\n📊 BASIC PERFORMANCE METRICS:")
    print(f"{'Total Trades:':<30} {metrics['total_trades']}")
    print(f"{'Winning Trades:':<30} {metrics['winning_trades']}")
    print(f"{'Losing Trades:':<30} {metrics['losing_trades']}")
    print(f"{'Win Rate:':<30} {metrics['win_rate']:.2%}")
    print(f"{'Total P&L:':<30} ${metrics['total_pl']:,.2f}")
    print(f"{'Gross Profit:':<30} ${metrics['gross_profit']:,.2f}")
    print(f"{'Gross Loss:':<30} ${metrics['gross_loss']:,.2f}")
    
    print(f"\n💰 TRADE ANALYSIS:")
    print(f"{'Average Winner:':<30} ${metrics['avg_winner']:,.2f}")
    print(f"{'Average Loser:':<30} ${metrics['avg_loser']:,.2f}")
    print(f"{'Largest Winner:':<30} ${metrics['max_winner']:,.2f}")
    print(f"{'Largest Loser:':<30} ${metrics['max_loser']:,.2f}")
    print(f"{'Profit Factor:':<30} {metrics['profit_factor']:.2f}")
    print(f"{'Expectancy:':<30} ${metrics['expectancy']:,.2f}")
    
    print(f"\n📉 RISK METRICS:")
    print(f"{'Maximum Drawdown:':<30} ${metrics['max_drawdown']:,.2f}")
    print(f"{'Sharpe Ratio:':<30} {metrics['sharpe_ratio']:.2f}")
    print(f"{'Recovery Factor:':<30} {metrics['recovery_factor']:.2f}")
    print(f"{'Max Win Streak:':<30} {metrics['max_win_streak']}")
    print(f"{'Max Loss Streak:':<30} {metrics['max_loss_streak']}")
    
    print(f"\n⏰ TIME-BASED ANALYSIS:")
    if metrics['best_hour'] is not None:
        print(f"{'Best Hour:':<30} {metrics['best_hour']}:00")
    if metrics['worst_hour'] is not None:
        print(f"{'Worst Hour:':<30} {metrics['worst_hour']}:00")
    if metrics['best_day'] is not None:
        print(f"{'Best Day:':<30} {metrics['best_day']}")
    if metrics['worst_day'] is not None:
        print(f"{'Worst Day:':<30} {metrics['worst_day']}")
    
    print(f"\n{'='*80}")

def plot_cumulative_pl(data, strategy_name):
    """Plot cumulative P&L"""
    if data.empty:
        return
    
    completed_trades = data[data['trade_pl'] != 0].copy()
    
    if completed_trades.empty:
        return
    
    plt.figure(figsize=(12, 6))
    plt.plot(completed_trades['datetime'], completed_trades['cumulative_pl'], 
            linewidth=2, color='blue', alpha=0.8)
    
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    plt.title(f'Cumulative P&L - {strategy_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Date/Time', fontsize=12)
    plt.ylabel('Cumulative P&L ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot instead of showing (for non-interactive environments)
    plt.savefig(f'{strategy_name.replace(" ", "_")}_cumulative_pl.png', dpi=300, bbox_inches='tight')
    print(f"📈 Chart saved: {strategy_name.replace(' ', '_')}_cumulative_pl.png")

def plot_drawdown(data, strategy_name):
    """Plot drawdown analysis"""
    if data.empty:
        return
    
    completed_trades = data[data['trade_pl'] != 0].copy()
    
    if completed_trades.empty:
        return
    
    cumulative_pl = completed_trades['cumulative_pl'].values
    running_max = np.maximum.accumulate(cumulative_pl)
    drawdown = cumulative_pl - running_max
    
    plt.figure(figsize=(12, 6))
    plt.fill_between(completed_trades['datetime'], drawdown, 0, 
                    color='red', alpha=0.3, label='Drawdown')
    plt.plot(completed_trades['datetime'], drawdown, color='red', linewidth=1)
    
    plt.title(f'Drawdown Analysis - {strategy_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Date/Time', fontsize=12)
    plt.ylabel('Drawdown ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(f'{strategy_name.replace(" ", "_")}_drawdown.png', dpi=300, bbox_inches='tight')
    print(f"📉 Drawdown chart saved: {strategy_name.replace(' ', '_')}_drawdown.png")

def main():
    """Main analysis function"""
    print("🎯 ThinkorSwim Trading Analysis Tool")
    print("=" * 60)
    print("📋 Instructions:")
    print("1. Replace the sample data below with your actual ThinkorSwim reports")
    print("2. Run this script to get comprehensive analysis")
    print("3. Check the generated charts and metrics")
    print("=" * 60)
    
    # ========================================
    # 🔄 REPLACE THIS DATA WITH YOUR ACTUAL DATA
    # ========================================
    
    # Your Long Strategy Data (from ThinkorSwim)
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.47;6/20/25 9:33 AM;;$38.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.85;6/20/25 9:34 AM;$38.00;$38.00;0.0;
Total P/L: $1 326.97; Total order(s): 620;"""

    # Your Short Strategy Data (from ThinkorSwim)
    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.85;6/20/25 9:34 AM;;$43.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.42;6/20/25 9:35 AM;$43.00;$43.00;0.0;
Total P/L: ($843.03); Total order(s): 619;"""
    
    # ========================================
    # 🚀 DON'T CHANGE ANYTHING BELOW THIS LINE
    # ========================================
    
    try:
        print("\n📊 Parsing trading data...")
        long_data = parse_thinkorswim_data(long_report)
        short_data = parse_thinkorswim_data(short_report)
        
        print(f"✅ Loaded {len(long_data)} long trades and {len(short_data)} short trades")
        
        # Analyze long strategy
        if not long_data.empty:
            print("\n" + "="*60)
            print("ANALYZING LONG STRATEGY")
            print("="*60)
            long_metrics = calculate_comprehensive_metrics(long_data)
            print_comprehensive_report(long_metrics, "Long Strategy")
            plot_cumulative_pl(long_data, "Long Strategy")
            plot_drawdown(long_data, "Long Strategy")
        
        # Analyze short strategy
        if not short_data.empty:
            print("\n" + "="*60)
            print("ANALYZING SHORT STRATEGY")
            print("="*60)
            short_metrics = calculate_comprehensive_metrics(short_data)
            print_comprehensive_report(short_metrics, "Short Strategy")
            plot_cumulative_pl(short_data, "Short Strategy")
            plot_drawdown(short_data, "Short Strategy")
        
        # Analyze combined
        if not long_data.empty and not short_data.empty:
            print("\n" + "="*60)
            print("ANALYZING COMBINED STRATEGY")
            print("="*60)
            combined_data = pd.concat([long_data, short_data], ignore_index=True)
            combined_data = combined_data.sort_values('datetime')
            combined_metrics = calculate_comprehensive_metrics(combined_data)
            print_comprehensive_report(combined_metrics, "Combined Strategy")
            plot_cumulative_pl(combined_data, "Combined Strategy")
            plot_drawdown(combined_data, "Combined Strategy")
        
        print("\n🎉 Analysis Complete!")
        print("=" * 60)
        print("📁 Generated Files:")
        print("  • Long_Strategy_cumulative_pl.png")
        print("  • Long_Strategy_drawdown.png")
        print("  • Short_Strategy_cumulative_pl.png")
        print("  • Short_Strategy_drawdown.png")
        print("  • Combined_Strategy_cumulative_pl.png")
        print("  • Combined_Strategy_drawdown.png")
        print("\n📊 Key Metrics Calculated:")
        print("  • Average Winner/Loser")
        print("  • Profit Factor")
        print("  • Max Drawdown")
        print("  • Sharpe Ratio")
        print("  • Win/Loss Streaks")
        print("  • Time-based Analysis")
        print("  • Recovery Factor")
        print("  • Expectancy")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure your data is in the correct ThinkorSwim format")
        print("2. Check that you have all required columns")
        print("3. Verify the data includes the header line")
        print("4. Ensure all dependencies are installed: pip install pandas numpy matplotlib")

if __name__ == "__main__":
    main()