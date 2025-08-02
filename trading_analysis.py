#!/usr/bin/env python3
"""
ThinkorSwim Trading Results Analysis Tool
Analyzes trading strategy performance from ThinkorSwim strategy reports
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TradingAnalyzer:
    def __init__(self):
        self.long_data = None
        self.short_data = None
        self.combined_data = None
        self.metrics = {}
        
    def parse_thinkorswim_report(self, report_text: str, strategy_name: str = "Strategy") -> pd.DataFrame:
        """
        Parse ThinkorSwim strategy report text into a pandas DataFrame
        """
        lines = report_text.strip().split('\n')
        
        # Find the data section (after the header)
        data_start = None
        for i, line in enumerate(lines):
            if 'Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position' in line:
                data_start = i + 1
                break
        
        if data_start is None:
            raise ValueError("Could not find data section in report")
        
        # Extract data lines
        data_lines = []
        for line in lines[data_start:]:
            if line.strip() and not line.startswith('Total'):
                data_lines.append(line)
        
        # Parse CSV-like data
        trades = []
        for line in data_lines:
            if line.strip():
                parts = line.split(';')
                if len(parts) >= 9:
                    try:
                        trade_id = int(parts[0])
                        strategy = parts[1]
                        side = parts[2]
                        amount = float(parts[3])
                        price = float(parts[4].replace('$', '').replace(',', ''))
                        date_time = parts[5]
                        trade_pl = parts[6]
                        cumulative_pl = parts[7]
                        position = float(parts[8])
                        
                        # Parse P&L values
                        trade_pl_value = self._parse_pl(trade_pl)
                        cumulative_pl_value = self._parse_pl(cumulative_pl)
                        
                        # Parse datetime
                        dt = datetime.strptime(date_time, '%m/%d/%y %I:%M %p')
                        
                        trades.append({
                            'id': trade_id,
                            'strategy': strategy,
                            'side': side,
                            'amount': amount,
                            'price': price,
                            'datetime': dt,
                            'trade_pl': trade_pl_value,
                            'cumulative_pl': cumulative_pl_value,
                            'position': position
                        })
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Could not parse line: {line[:50]}... Error: {e}")
                        continue
        
        df = pd.DataFrame(trades)
        
        # Create trade pairs (entry/exit)
        df = self._create_trade_pairs(df)
        
        return df
    
    def _parse_pl(self, pl_str: str) -> float:
        """Parse P&L string to float value"""
        if not pl_str or pl_str.strip() == '':
            return 0.0
        
        # Remove parentheses and $ signs
        pl_str = pl_str.replace('$', '').replace(',', '').replace('(', '').replace(')', '')
        
        try:
            return float(pl_str)
        except ValueError:
            return 0.0
    
    def _create_trade_pairs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Group entry and exit trades into trade pairs
        """
        trades = []
        i = 0
        
        while i < len(df):
            entry_trade = df.iloc[i]
            
            # Find corresponding exit trade
            if i + 1 < len(df):
                exit_trade = df.iloc[i + 1]
                
                # Create trade pair
                trade = {
                    'entry_id': entry_trade['id'],
                    'exit_id': exit_trade['id'],
                    'strategy': entry_trade['strategy'],
                    'side': entry_trade['side'],
                    'entry_price': entry_trade['price'],
                    'exit_price': exit_trade['price'],
                    'entry_time': entry_trade['datetime'],
                    'exit_time': exit_trade['datetime'],
                    'amount': abs(entry_trade['amount']),
                    'trade_pl': exit_trade['trade_pl'],
                    'duration': (exit_trade['datetime'] - entry_trade['datetime']).total_seconds() / 60,  # minutes
                    'return_pct': ((exit_trade['price'] - entry_trade['price']) / entry_trade['price']) * 100
                }
                
                # Determine if it's a long or short trade
                if 'Buy to Open' in entry_trade['side']:
                    trade['trade_type'] = 'Long'
                elif 'Sell to Open' in entry_trade['side']:
                    trade['trade_type'] = 'Short'
                else:
                    trade['trade_type'] = 'Unknown'
                
                trades.append(trade)
                i += 2  # Skip both entry and exit
            else:
                # Unclosed trade
                trade = {
                    'entry_id': entry_trade['id'],
                    'exit_id': None,
                    'strategy': entry_trade['strategy'],
                    'side': entry_trade['side'],
                    'entry_price': entry_trade['price'],
                    'exit_price': None,
                    'entry_time': entry_trade['datetime'],
                    'exit_time': None,
                    'amount': abs(entry_trade['amount']),
                    'trade_pl': 0,
                    'duration': None,
                    'return_pct': 0,
                    'trade_type': 'Open'
                }
                trades.append(trade)
                i += 1
        
        return pd.DataFrame(trades)
    
    def load_data(self, long_report: str, short_report: str):
        """Load and parse both long and short strategy reports"""
        print("Parsing Long Strategy Report...")
        self.long_data = self.parse_thinkorswim_report(long_report, "Long Strategy")
        
        print("Parsing Short Strategy Report...")
        self.short_data = self.parse_thinkorswim_report(short_report, "Short Strategy")
        
        # Combine data
        self.combined_data = pd.concat([
            self.long_data.assign(strategy_type='Long'),
            self.short_data.assign(strategy_type='Short')
        ], ignore_index=True)
        
        print(f"Loaded {len(self.long_data)} long trades and {len(self.short_data)} short trades")
    
    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive trading metrics"""
        metrics = {}
        
        # Overall metrics
        metrics['total_trades'] = len(self.combined_data)
        metrics['total_pnl'] = self.combined_data['trade_pl'].sum()
        metrics['total_return_pct'] = self.combined_data['return_pct'].sum()
        
        # Win/Loss metrics
        winning_trades = self.combined_data[self.combined_data['trade_pl'] > 0]
        losing_trades = self.combined_data[self.combined_data['trade_pl'] < 0]
        
        metrics['winning_trades'] = len(winning_trades)
        metrics['losing_trades'] = len(losing_trades)
        metrics['win_rate'] = len(winning_trades) / len(self.combined_data) * 100 if len(self.combined_data) > 0 else 0
        
        # Average metrics
        metrics['avg_winner'] = winning_trades['trade_pl'].mean() if len(winning_trades) > 0 else 0
        metrics['avg_loser'] = losing_trades['trade_pl'].mean() if len(losing_trades) > 0 else 0
        metrics['avg_trade'] = self.combined_data['trade_pl'].mean()
        metrics['avg_return_pct'] = self.combined_data['return_pct'].mean()
        
        # Profit factor
        total_wins = winning_trades['trade_pl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['trade_pl'].sum()) if len(losing_trades) > 0 else 0
        metrics['profit_factor'] = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Risk metrics
        metrics['max_drawdown'] = self._calculate_max_drawdown()
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio()
        metrics['sortino_ratio'] = self._calculate_sortino_ratio()
        
        # Duration metrics
        closed_trades = self.combined_data[self.combined_data['duration'].notna()]
        metrics['avg_duration_minutes'] = closed_trades['duration'].mean() if len(closed_trades) > 0 else 0
        metrics['median_duration_minutes'] = closed_trades['duration'].median() if len(closed_trades) > 0 else 0
        
        # Strategy-specific metrics
        long_trades = self.combined_data[self.combined_data['strategy_type'] == 'Long']
        short_trades = self.combined_data[self.combined_data['strategy_type'] == 'Short']
        
        metrics['long_trades'] = len(long_trades)
        metrics['short_trades'] = len(short_trades)
        metrics['long_pnl'] = long_trades['trade_pl'].sum()
        metrics['short_pnl'] = short_trades['trade_pl'].sum()
        metrics['long_win_rate'] = len(long_trades[long_trades['trade_pl'] > 0]) / len(long_trades) * 100 if len(long_trades) > 0 else 0
        metrics['short_win_rate'] = len(short_trades[short_trades['trade_pl'] > 0]) / len(short_trades) * 100 if len(short_trades) > 0 else 0
        
        self.metrics = metrics
        return metrics
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        cumulative = self.combined_data['trade_pl'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = cumulative - running_max
        return abs(drawdown.min())
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        returns = self.combined_data['return_pct']
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return excess_returns.mean() / returns.std() if returns.std() > 0 else 0
    
    def _calculate_sortino_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        returns = self.combined_data['return_pct']
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() if len(negative_returns) > 0 else 0
        
        return excess_returns.mean() / downside_deviation if downside_deviation > 0 else 0
    
    def generate_time_analysis(self) -> Dict:
        """Analyze performance by time of day"""
        time_analysis = {}
        
        # Add hour column
        self.combined_data['hour'] = self.combined_data['entry_time'].dt.hour
        self.combined_data['day_of_week'] = self.combined_data['entry_time'].dt.day_name()
        
        # Hourly analysis
        hourly_stats = self.combined_data.groupby('hour').agg({
            'trade_pl': ['count', 'sum', 'mean'],
            'return_pct': 'mean'
        }).round(2)
        
        hourly_stats.columns = ['trades', 'total_pnl', 'avg_pnl', 'avg_return_pct']
        time_analysis['hourly'] = hourly_stats
        
        # Day of week analysis
        daily_stats = self.combined_data.groupby('day_of_week').agg({
            'trade_pl': ['count', 'sum', 'mean'],
            'return_pct': 'mean'
        }).round(2)
        
        daily_stats.columns = ['trades', 'total_pnl', 'avg_pnl', 'avg_return_pct']
        time_analysis['daily'] = daily_stats
        
        return time_analysis
    
    def plot_cumulative_pnl(self, save_path: str = None):
        """Plot cumulative P&L over time"""
        plt.figure(figsize=(15, 8))
        
        # Calculate cumulative P&L
        self.combined_data['cumulative_pnl'] = self.combined_data['trade_pl'].cumsum()
        
        # Plot by strategy type
        for strategy in ['Long', 'Short']:
            strategy_data = self.combined_data[self.combined_data['strategy_type'] == strategy]
            if len(strategy_data) > 0:
                strategy_data = strategy_data.sort_values('entry_time')
                strategy_data['cumulative_pnl'] = strategy_data['trade_pl'].cumsum()
                plt.plot(strategy_data['entry_time'], strategy_data['cumulative_pnl'], 
                        label=f'{strategy} Strategy', linewidth=2, marker='o', markersize=4)
        
        # Plot combined
        combined_sorted = self.combined_data.sort_values('entry_time')
        combined_sorted['cumulative_pnl'] = combined_sorted['trade_pl'].cumsum()
        plt.plot(combined_sorted['entry_time'], combined_sorted['cumulative_pnl'], 
                label='Combined', linewidth=3, color='black', alpha=0.7)
        
        plt.title('Cumulative P&L Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Cumulative P&L ($)', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_time_analysis(self, save_path: str = None):
        """Plot time-based analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Hourly P&L
        hourly_stats = self.generate_time_analysis()['hourly']
        axes[0, 0].bar(hourly_stats.index, hourly_stats['total_pnl'], color='skyblue', alpha=0.7)
        axes[0, 0].set_title('Total P&L by Hour', fontweight='bold')
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('Total P&L ($)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Hourly trade count
        axes[0, 1].bar(hourly_stats.index, hourly_stats['trades'], color='lightgreen', alpha=0.7)
        axes[0, 1].set_title('Number of Trades by Hour', fontweight='bold')
        axes[0, 1].set_xlabel('Hour of Day')
        axes[0, 1].set_ylabel('Number of Trades')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Daily P&L
        daily_stats = self.generate_time_analysis()['daily']
        axes[1, 0].bar(range(len(daily_stats)), daily_stats['total_pnl'], color='salmon', alpha=0.7)
        axes[1, 0].set_title('Total P&L by Day of Week', fontweight='bold')
        axes[1, 0].set_xlabel('Day of Week')
        axes[1, 0].set_ylabel('Total P&L ($)')
        axes[1, 0].set_xticks(range(len(daily_stats)))
        axes[1, 0].set_xticklabels(daily_stats.index, rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Win rate by strategy
        strategies = ['Long', 'Short']
        win_rates = [self.metrics['long_win_rate'], self.metrics['short_win_rate']]
        colors = ['green', 'red']
        axes[1, 1].bar(strategies, win_rates, color=colors, alpha=0.7)
        axes[1, 1].set_title('Win Rate by Strategy', fontweight='bold')
        axes[1, 1].set_ylabel('Win Rate (%)')
        axes[1, 1].set_ylim(0, 100)
        for i, v in enumerate(win_rates):
            axes[1, 1].text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_trade_distribution(self, save_path: str = None):
        """Plot trade P&L distribution"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # P&L distribution
        axes[0, 0].hist(self.combined_data['trade_pl'], bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].axvline(self.combined_data['trade_pl'].mean(), color='red', linestyle='--', 
                          label=f'Mean: ${self.combined_data["trade_pl"].mean():.2f}')
        axes[0, 0].set_title('Trade P&L Distribution', fontweight='bold')
        axes[0, 0].set_xlabel('P&L ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Return distribution
        axes[0, 1].hist(self.combined_data['return_pct'], bins=30, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].axvline(self.combined_data['return_pct'].mean(), color='red', linestyle='--',
                          label=f'Mean: {self.combined_data["return_pct"].mean():.2f}%')
        axes[0, 1].set_title('Trade Return Distribution', fontweight='bold')
        axes[0, 1].set_xlabel('Return (%)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Duration vs P&L scatter
        closed_trades = self.combined_data[self.combined_data['duration'].notna()]
        if len(closed_trades) > 0:
            axes[1, 0].scatter(closed_trades['duration'], closed_trades['trade_pl'], alpha=0.6)
            axes[1, 0].set_title('Trade Duration vs P&L', fontweight='bold')
            axes[1, 0].set_xlabel('Duration (minutes)')
            axes[1, 0].set_ylabel('P&L ($)')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Strategy comparison
        strategies = ['Long', 'Short']
        avg_pnls = [
            self.combined_data[self.combined_data['strategy_type'] == 'Long']['trade_pl'].mean(),
            self.combined_data[self.combined_data['strategy_type'] == 'Short']['trade_pl'].mean()
        ]
        colors = ['green', 'red']
        axes[1, 1].bar(strategies, avg_pnls, color=colors, alpha=0.7)
        axes[1, 1].set_title('Average P&L by Strategy', fontweight='bold')
        axes[1, 1].set_ylabel('Average P&L ($)')
        for i, v in enumerate(avg_pnls):
            axes[1, 1].text(i, v + (0.1 if v >= 0 else -0.1), f'${v:.2f}', ha='center', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_summary_report(self):
        """Print comprehensive summary report"""
        print("=" * 80)
        print("THINKORSWIM TRADING STRATEGY ANALYSIS REPORT")
        print("=" * 80)
        
        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"   Total Trades: {self.metrics['total_trades']}")
        print(f"   Total P&L: ${self.metrics['total_pnl']:,.2f}")
        print(f"   Total Return: {self.metrics['total_return_pct']:.2f}%")
        print(f"   Win Rate: {self.metrics['win_rate']:.1f}%")
        print(f"   Profit Factor: {self.metrics['profit_factor']:.2f}")
        print(f"   Max Drawdown: ${self.metrics['max_drawdown']:,.2f}")
        
        print(f"\n💰 TRADE METRICS:")
        print(f"   Average Winner: ${self.metrics['avg_winner']:.2f}")
        print(f"   Average Loser: ${self.metrics['avg_loser']:.2f}")
        print(f"   Average Trade: ${self.metrics['avg_trade']:.2f}")
        print(f"   Average Return: {self.metrics['avg_return_pct']:.2f}%")
        print(f"   Average Duration: {self.metrics['avg_duration_minutes']:.1f} minutes")
        
        print(f"\n📈 RISK METRICS:")
        print(f"   Sharpe Ratio: {self.metrics['sharpe_ratio']:.2f}")
        print(f"   Sortino Ratio: {self.metrics['sortino_ratio']:.2f}")
        
        print(f"\n🎯 STRATEGY BREAKDOWN:")
        print(f"   Long Strategy:")
        print(f"     Trades: {self.metrics['long_trades']}")
        print(f"     P&L: ${self.metrics['long_pnl']:,.2f}")
        print(f"     Win Rate: {self.metrics['long_win_rate']:.1f}%")
        
        print(f"   Short Strategy:")
        print(f"     Trades: {self.metrics['short_trades']}")
        print(f"     P&L: ${self.metrics['short_pnl']:,.2f}")
        print(f"     Win Rate: {self.metrics['short_win_rate']:.1f}%")
        
        # Time analysis
        time_analysis = self.generate_time_analysis()
        
        print(f"\n⏰ TIME ANALYSIS:")
        print(f"   Best Hour: {time_analysis['hourly']['total_pnl'].idxmax()} ({time_analysis['hourly']['total_pnl'].max():.0f})")
        print(f"   Worst Hour: {time_analysis['hourly']['total_pnl'].idxmin()} ({time_analysis['hourly']['total_pnl'].min():.0f})")
        print(f"   Best Day: {time_analysis['daily']['total_pnl'].idxmax()}")
        print(f"   Worst Day: {time_analysis['daily']['total_pnl'].idxmin()}")
        
        print("\n" + "=" * 80)
    
    def save_detailed_report(self, filename: str = "trading_analysis_report.txt"):
        """Save detailed analysis to text file"""
        with open(filename, 'w') as f:
            f.write("THINKORSWIM TRADING STRATEGY ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Overall metrics
            f.write("OVERALL PERFORMANCE:\n")
            f.write("-" * 20 + "\n")
            for key, value in self.metrics.items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.2f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            
            # Time analysis
            f.write("\nTIME ANALYSIS:\n")
            f.write("-" * 20 + "\n")
            f.write("Hourly Performance:\n")
            f.write(self.generate_time_analysis()['hourly'].to_string())
            f.write("\n\nDaily Performance:\n")
            f.write(self.generate_time_analysis()['daily'].to_string())
            
            # Trade details
            f.write("\n\nTRADE DETAILS:\n")
            f.write("-" * 20 + "\n")
            f.write(self.combined_data.to_string())
        
        print(f"Detailed report saved to {filename}")

def main():
    """Main function to run the analysis"""
    # Sample data (replace with your actual data)
    long_report = """
Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
Total P/L: $1 326.97; Total order(s): 620;
"""
    
    short_report = """
Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
Total P/L: ($843.03); Total order(s): 619;
"""
    
    # Create analyzer and run analysis
    analyzer = TradingAnalyzer()
    
    try:
        analyzer.load_data(long_report, short_report)
        metrics = analyzer.calculate_metrics()
        
        # Print summary
        analyzer.print_summary_report()
        
        # Generate plots
        print("\nGenerating visualizations...")
        analyzer.plot_cumulative_pnl()
        analyzer.plot_time_analysis()
        analyzer.plot_trade_distribution()
        
        # Save detailed report
        analyzer.save_detailed_report()
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()