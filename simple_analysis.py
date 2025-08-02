#!/usr/bin/env python3
"""
Simple ThinkorSwim Trading Analysis
Handles the actual data format from your reports
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

def calculate_metrics(data):
    """Calculate trading metrics"""
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
    
    # Sharpe ratio
    returns = completed_trades['trade_pl'].values
    sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
    
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
        'sharpe_ratio': sharpe_ratio
    }

def print_report(metrics, strategy_name):
    """Print trading report"""
    print(f"\n{'='*60}")
    print(f"TRADING ANALYSIS - {strategy_name.upper()}")
    print(f"{'='*60}")
    
    if not metrics:
        print("No completed trades found for analysis.")
        return
    
    print(f"\n📊 BASIC METRICS:")
    print(f"{'Total Trades:':<25} {metrics['total_trades']}")
    print(f"{'Winning Trades:':<25} {metrics['winning_trades']}")
    print(f"{'Losing Trades:':<25} {metrics['losing_trades']}")
    print(f"{'Win Rate:':<25} {metrics['win_rate']:.2%}")
    print(f"{'Total P&L:':<25} ${metrics['total_pl']:,.2f}")
    print(f"{'Gross Profit:':<25} ${metrics['gross_profit']:,.2f}")
    print(f"{'Gross Loss:':<25} ${metrics['gross_loss']:,.2f}")
    print(f"{'Average Winner:':<25} ${metrics['avg_winner']:,.2f}")
    print(f"{'Average Loser:':<25} ${metrics['avg_loser']:,.2f}")
    print(f"{'Profit Factor:':<25} {metrics['profit_factor']:.2f}")
    print(f"{'Max Winner:':<25} ${metrics['max_winner']:,.2f}")
    print(f"{'Max Loser:':<25} ${metrics['max_loser']:,.2f}")
    print(f"{'Max Drawdown:':<25} ${metrics['max_drawdown']:,.2f}")
    print(f"{'Sharpe Ratio:':<25} {metrics['sharpe_ratio']:.2f}")
    
    print(f"\n{'='*60}")

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
    plt.show()

def main():
    """Main analysis function"""
    print("🚀 ThinkorSwim Trading Analysis")
    print("=" * 50)
    
    # Your actual data (replace with your real data)
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.47;6/20/25 9:33 AM;;$38.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.85;6/20/25 9:34 AM;$38.00;$38.00;0.0;
Total P/L: $1 326.97; Total order(s): 620;"""

    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.85;6/20/25 9:34 AM;;$43.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.42;6/20/25 9:35 AM;$43.00;$43.00;0.0;
Total P/L: ($843.03); Total order(s): 619;"""
    
    try:
        # Parse data
        print("📊 Parsing trading data...")
        long_data = parse_thinkorswim_data(long_report)
        short_data = parse_thinkorswim_data(short_report)
        
        print(f"Loaded {len(long_data)} long trades and {len(short_data)} short trades")
        
        # Analyze long strategy
        if not long_data.empty:
            long_metrics = calculate_metrics(long_data)
            print_report(long_metrics, "Long Strategy")
            plot_cumulative_pl(long_data, "Long Strategy")
        
        # Analyze short strategy
        if not short_data.empty:
            short_metrics = calculate_metrics(short_data)
            print_report(short_metrics, "Short Strategy")
            plot_cumulative_pl(short_data, "Short Strategy")
        
        # Analyze combined
        if not long_data.empty and not short_data.empty:
            combined_data = pd.concat([long_data, short_data], ignore_index=True)
            combined_data = combined_data.sort_values('datetime')
            combined_metrics = calculate_metrics(combined_data)
            print_report(combined_metrics, "Combined Strategy")
            plot_cumulative_pl(combined_data, "Combined Strategy")
        
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your data format and try again.")

if __name__ == "__main__":
    main()