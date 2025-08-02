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
        
    def parse_thinkorswim_report(self, report_text: str, strategy_name: str = "Strategy") -> pd.DataFrame:
        """
        Parse ThinkorSwim strategy report text into a pandas DataFrame
        """
        lines = report_text.strip().split('\n')
        
        # Find the data section (after the header)
        data_start = None
        for i, line in enumerate(lines):
            if 'Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;' in line:
                data_start = i + 1
                break
        
        if data_start is None:
            # Try to find any line with semicolons that might be data
            for i, line in enumerate(lines):
                if ';' in line and any(char.isdigit() for char in line):
                    # Check if it looks like a trade line
                    parts = line.split(';')
                    if len(parts) >= 5 and parts[0].strip().isdigit():
                        data_start = i
                        break
        
        if data_start is None:
            print(f"Debug: Available lines in report:")
            for i, line in enumerate(lines[:10]):  # Show first 10 lines
                print(f"  Line {i}: {line[:100]}...")
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
                # Split by semicolon and clean up
                parts = [part.strip() for part in line.split(';')]
                if len(parts) >= 9:
                    try:
                        trade = {
                            'id': int(parts[0]),
                            'strategy': parts[1],
                            'side': parts[2],
                            'amount': float(parts[3]),
                            'price': float(parts[4].replace('$', '').replace(',', '')),
                            'datetime': parts[5],
                            'trade_pl': parts[6],
                            'cumulative_pl': parts[7],
                            'position': float(parts[8])
                        }
                        trades.append(trade)
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Could not parse line: {line}")
                        continue
        
        if not trades:
            print("No valid trades found in report")
            # Create empty DataFrame with expected columns
            df = pd.DataFrame(columns=[
                'id', 'strategy', 'side', 'amount', 'price', 'datetime', 
                'trade_pl', 'cumulative_pl', 'position', 'strategy_name'
            ])
        else:
            df = pd.DataFrame(trades)
            
            # Clean up P&L columns
            df['trade_pl'] = df['trade_pl'].apply(self._parse_pl)
            df['cumulative_pl'] = df['cumulative_pl'].apply(self._parse_pl)
            
            # Convert datetime
            df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%y %I:%M %p')
            
            # Add strategy name
            df['strategy_name'] = strategy_name
        
        return df
    
    def _parse_pl(self, pl_str: str) -> float:
        """Parse P&L string to float"""
        if pd.isna(pl_str) or pl_str == '':
            return 0.0
        
        # Remove parentheses and $ signs
        pl_str = str(pl_str).replace('$', '').replace(',', '')
        
        if '(' in pl_str and ')' in pl_str:
            # Negative value in parentheses
            pl_str = pl_str.replace('(', '').replace(')', '')
            return -float(pl_str)
        else:
            return float(pl_str)
    
    def load_data(self, long_report: str, short_report: str):
        """Load both long and short strategy reports"""
        print("Loading trading data...")
        
        self.long_data = self.parse_thinkorswim_report(long_report, "Long Strategy")
        self.short_data = self.parse_thinkorswim_report(short_report, "Short Strategy")
        
        # Combine data
        self.combined_data = pd.concat([self.long_data, self.short_data], ignore_index=True)
        self.combined_data = self.combined_data.sort_values('datetime')
        
        print(f"Loaded {len(self.long_data)} long trades and {len(self.short_data)} short trades")
        print(f"Total trades: {len(self.combined_data)}")
    
    def calculate_basic_metrics(self) -> Dict:
        """Calculate basic trading performance metrics"""
        if self.combined_data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Get completed trades (trades with non-zero P&L)
        long_completed = self.long_data[self.long_data['trade_pl'] != 0]
        short_completed = self.short_data[self.short_data['trade_pl'] != 0]
        
        # Calculate metrics for each strategy
        long_metrics = self._calculate_strategy_metrics(long_completed, "Long")
        short_metrics = self._calculate_strategy_metrics(short_completed, "Short")
        
        # Combined metrics
        all_completed = pd.concat([long_completed, short_completed], ignore_index=True)
        combined_metrics = self._calculate_strategy_metrics(all_completed, "Combined")
        
        return {
            'long': long_metrics,
            'short': short_metrics,
            'combined': combined_metrics
        }
    
    def _calculate_strategy_metrics(self, trades: pd.DataFrame, strategy_name: str) -> Dict:
        """Calculate metrics for a specific strategy"""
        if len(trades) == 0:
            return {
                'strategy': strategy_name,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pl': 0,
                'average_winner': 0,
                'average_loser': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0
            }
        
        # Calculate trade P&L
        trades = trades.copy()
        trades['trade_pl'] = trades['trade_pl'].fillna(0)
        
        # Basic counts
        total_trades = len(trades)
        winning_trades = len(trades[trades['trade_pl'] > 0])
        losing_trades = len(trades[trades['trade_pl'] < 0])
        
        # Win rate
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # P&L metrics
        total_pl = trades['trade_pl'].sum()
        average_winner = trades[trades['trade_pl'] > 0]['trade_pl'].mean() if winning_trades > 0 else 0
        average_loser = trades[trades['trade_pl'] < 0]['trade_pl'].mean() if losing_trades > 0 else 0
        
        # Profit factor
        gross_profit = trades[trades['trade_pl'] > 0]['trade_pl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades[trades['trade_pl'] < 0]['trade_pl'].sum()) if losing_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0
        
        # Max drawdown
        cumulative_pl = trades['trade_pl'].cumsum()
        running_max = cumulative_pl.expanding().max()
        drawdown = cumulative_pl - running_max
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (assuming daily returns)
        returns = trades['trade_pl'] / trades['price']  # Simple return
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Consecutive wins/losses
        max_consecutive_wins = self._max_consecutive(trades['trade_pl'] > 0)
        max_consecutive_losses = self._max_consecutive(trades['trade_pl'] < 0)
        
        return {
            'strategy': strategy_name,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pl': total_pl,
            'average_winner': average_winner,
            'average_loser': average_loser,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses
        }
    
    def _max_consecutive(self, condition_series: pd.Series) -> int:
        """Calculate maximum consecutive True values"""
        max_consecutive = 0
        current_consecutive = 0
        
        for value in condition_series:
            if value:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def calculate_time_analysis(self) -> Dict:
        """Analyze performance by time of day, day of week, and month"""
        if self.combined_data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Add time-based columns
        df = self.combined_data.copy()
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_name()
        df['month'] = df['datetime'].dt.month_name()
        df['date'] = df['datetime'].dt.date
        
        # Time of day analysis
        hourly_pl = df.groupby('hour')['trade_pl'].agg(['sum', 'mean', 'count']).reset_index()
        hourly_pl.columns = ['hour', 'total_pl', 'avg_pl', 'trade_count']
        
        # Day of week analysis
        daily_pl = df.groupby('day_of_week')['trade_pl'].agg(['sum', 'mean', 'count']).reset_index()
        daily_pl.columns = ['day', 'total_pl', 'avg_pl', 'trade_count']
        
        # Monthly analysis
        monthly_pl = df.groupby('month')['trade_pl'].agg(['sum', 'mean', 'count']).reset_index()
        monthly_pl.columns = ['month', 'total_pl', 'avg_pl', 'trade_count']
        
        # Daily P&L
        daily_cumulative = df.groupby('date')['trade_pl'].sum().cumsum().reset_index()
        daily_cumulative.columns = ['date', 'cumulative_pl']
        
        return {
            'hourly': hourly_pl,
            'daily': daily_pl,
            'monthly': monthly_pl,
            'daily_cumulative': daily_cumulative
        }
    
    def generate_visualizations(self, save_path: str = "trading_analysis"):
        """Generate comprehensive trading analysis visualizations"""
        if self.combined_data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Cumulative P&L
        ax1 = plt.subplot(4, 2, 1)
        self._plot_cumulative_pl(ax1)
        
        # 2. Trade P&L Distribution
        ax2 = plt.subplot(4, 2, 2)
        self._plot_pl_distribution(ax2)
        
        # 3. Win Rate by Strategy
        ax3 = plt.subplot(4, 2, 3)
        self._plot_win_rate(ax3)
        
        # 4. Profit Factor Comparison
        ax4 = plt.subplot(4, 2, 4)
        self._plot_profit_factor(ax4)
        
        # 5. Time of Day Analysis
        ax5 = plt.subplot(4, 2, 5)
        self._plot_hourly_analysis(ax5)
        
        # 6. Day of Week Analysis
        ax6 = plt.subplot(4, 2, 6)
        self._plot_daily_analysis(ax6)
        
        # 7. Drawdown Analysis
        ax7 = plt.subplot(4, 2, 7)
        self._plot_drawdown(ax7)
        
        # 8. Trade Duration Analysis
        ax8 = plt.subplot(4, 2, 8)
        self._plot_trade_duration(ax8)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}_overview.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Generate additional detailed plots
        self._generate_detailed_plots(save_path)
    
    def _plot_cumulative_pl(self, ax):
        """Plot cumulative P&L over time"""
        long_cumulative = self.long_data['cumulative_pl'].fillna(0)
        short_cumulative = self.short_data['cumulative_pl'].fillna(0)
        
        ax.plot(self.long_data['datetime'], long_cumulative, label='Long Strategy', linewidth=2, color='green')
        ax.plot(self.short_data['datetime'], short_cumulative, label='Short Strategy', linewidth=2, color='red')
        
        # Combined cumulative
        combined_cumulative = self.combined_data['cumulative_pl'].fillna(0)
        ax.plot(self.combined_data['datetime'], combined_cumulative, label='Combined', linewidth=3, color='blue', alpha=0.7)
        
        ax.set_title('Cumulative P&L Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative P&L ($)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    def _plot_pl_distribution(self, ax):
        """Plot distribution of trade P&L"""
        long_pl = self.long_data['trade_pl'].fillna(0)
        short_pl = self.short_data['trade_pl'].fillna(0)
        
        ax.hist(long_pl, bins=30, alpha=0.7, label='Long Strategy', color='green', edgecolor='black')
        ax.hist(short_pl, bins=30, alpha=0.7, label='Short Strategy', color='red', edgecolor='black')
        
        ax.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Trade P&L ($)')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add vertical line at zero
        ax.axvline(x=0, color='black', linestyle='--', alpha=0.7)
    
    def _plot_win_rate(self, ax):
        """Plot win rate comparison"""
        metrics = self.calculate_basic_metrics()
        
        strategies = ['Long', 'Short', 'Combined']
        win_rates = [metrics['long']['win_rate'], metrics['short']['win_rate'], metrics['combined']['win_rate']]
        colors = ['green', 'red', 'blue']
        
        bars = ax.bar(strategies, win_rates, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar, rate in zip(bars, win_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Win Rate by Strategy', fontsize=14, fontweight='bold')
        ax.set_ylabel('Win Rate')
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_profit_factor(self, ax):
        """Plot profit factor comparison"""
        metrics = self.calculate_basic_metrics()
        
        strategies = ['Long', 'Short', 'Combined']
        profit_factors = [metrics['long']['profit_factor'], metrics['short']['profit_factor'], metrics['combined']['profit_factor']]
        colors = ['green', 'red', 'blue']
        
        # Cap infinite values for display
        max_display = 10
        profit_factors_display = [min(pf, max_display) if pf != float('inf') else max_display for pf in profit_factors]
        
        bars = ax.bar(strategies, profit_factors_display, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar, pf in zip(bars, profit_factors):
            height = bar.get_height()
            label = f'{pf:.2f}' if pf != float('inf') else '∞'
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   label, ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Profit Factor by Strategy', fontsize=14, fontweight='bold')
        ax.set_ylabel('Profit Factor')
        ax.axhline(y=1, color='black', linestyle='--', alpha=0.7, label='Break-even')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_hourly_analysis(self, ax):
        """Plot hourly P&L analysis"""
        time_analysis = self.calculate_time_analysis()
        hourly_data = time_analysis['hourly']
        
        ax.bar(hourly_data['hour'], hourly_data['total_pl'], 
               color=['green' if x > 0 else 'red' for x in hourly_data['total_pl']], 
               alpha=0.7, edgecolor='black')
        
        ax.set_title('P&L by Hour of Day', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Total P&L ($)')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.7)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    def _plot_daily_analysis(self, ax):
        """Plot day of week P&L analysis"""
        time_analysis = self.calculate_time_analysis()
        daily_data = time_analysis['daily']
        
        # Order days correctly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_data['day'] = pd.Categorical(daily_data['day'], categories=day_order, ordered=True)
        daily_data = daily_data.sort_values('day')
        
        ax.bar(daily_data['day'], daily_data['total_pl'], 
               color=['green' if x > 0 else 'red' for x in daily_data['total_pl']], 
               alpha=0.7, edgecolor='black')
        
        ax.set_title('P&L by Day of Week', fontsize=14, fontweight='bold')
        ax.set_xlabel('Day')
        ax.set_ylabel('Total P&L ($)')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.7)
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    def _plot_drawdown(self, ax):
        """Plot drawdown analysis"""
        # Calculate drawdown for combined strategy
        combined_pl = self.combined_data['trade_pl'].fillna(0)
        cumulative_pl = combined_pl.cumsum()
        running_max = cumulative_pl.expanding().max()
        drawdown = cumulative_pl - running_max
        
        ax.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.3, color='red')
        ax.plot(drawdown, color='red', linewidth=2)
        
        ax.set_title('Drawdown Analysis', fontsize=14, fontweight='bold')
        ax.set_xlabel('Trade Number')
        ax.set_ylabel('Drawdown ($)')
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    def _plot_trade_duration(self, ax):
        """Plot trade duration analysis"""
        # Calculate trade duration (time between entry and exit)
        # This is a simplified version - you might want to enhance this
        trade_durations = []
        
        # For long strategy
        long_entries = self.long_data[self.long_data['side'].str.contains('Buy to Open')]
        long_exits = self.long_data[self.long_data['side'].str.contains('Sell to Close')]
        
        for i in range(min(len(long_entries), len(long_exits))):
            duration = (long_exits.iloc[i]['datetime'] - long_entries.iloc[i]['datetime']).total_seconds() / 60  # minutes
            trade_durations.append(duration)
        
        # For short strategy
        short_entries = self.short_data[self.short_data['side'].str.contains('Sell to Open')]
        short_exits = self.short_data[self.short_data['side'].str.contains('Buy to Close')]
        
        for i in range(min(len(short_entries), len(short_exits))):
            duration = (short_exits.iloc[i]['datetime'] - short_entries.iloc[i]['datetime']).total_seconds() / 60  # minutes
            trade_durations.append(duration)
        
        if trade_durations:
            ax.hist(trade_durations, bins=30, alpha=0.7, color='blue', edgecolor='black')
            ax.set_title('Trade Duration Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Duration (minutes)')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No trade duration data available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Trade Duration Distribution', fontsize=14, fontweight='bold')
    
    def _generate_detailed_plots(self, save_path: str):
        """Generate additional detailed analysis plots"""
        # Monthly performance
        fig, ax = plt.subplots(figsize=(12, 6))
        time_analysis = self.calculate_time_analysis()
        monthly_data = time_analysis['monthly']
        
        ax.bar(monthly_data['month'], monthly_data['total_pl'], 
               color=['green' if x > 0 else 'red' for x in monthly_data['total_pl']], 
               alpha=0.7, edgecolor='black')
        
        ax.set_title('Monthly Performance', fontsize=14, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total P&L ($)')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.7)
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        plt.savefig(f"{save_path}_monthly.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self, save_path: str = "trading_report.txt"):
        """Generate a comprehensive text report"""
        if self.combined_data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        metrics = self.calculate_basic_metrics()
        time_analysis = self.calculate_time_analysis()
        
        with open(save_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("THINKORSWIM TRADING STRATEGY ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Trades: {len(self.combined_data)}\n")
            f.write(f"Long Strategy Trades: {len(self.long_data)}\n")
            f.write(f"Short Strategy Trades: {len(self.short_data)}\n")
            f.write(f"Date Range: {self.combined_data['datetime'].min()} to {self.combined_data['datetime'].max()}\n\n")
            
            # Strategy Performance
            for strategy in ['long', 'short', 'combined']:
                f.write(f"{strategy.upper()} STRATEGY PERFORMANCE\n")
                f.write("-" * 40 + "\n")
                m = metrics[strategy]
                f.write(f"Total Trades: {m['total_trades']}\n")
                f.write(f"Winning Trades: {m['winning_trades']}\n")
                f.write(f"Losing Trades: {m['losing_trades']}\n")
                f.write(f"Win Rate: {m['win_rate']:.2%}\n")
                f.write(f"Total P&L: ${m['total_pl']:,.2f}\n")
                f.write(f"Average Winner: ${m['average_winner']:,.2f}\n")
                f.write(f"Average Loser: ${m['average_loser']:,.2f}\n")
                f.write(f"Profit Factor: {m['profit_factor']:.2f}\n")
                f.write(f"Max Drawdown: ${m['max_drawdown']:,.2f}\n")
                f.write(f"Sharpe Ratio: {m['sharpe_ratio']:.2f}\n")
                f.write(f"Max Consecutive Wins: {m['max_consecutive_wins']}\n")
                f.write(f"Max Consecutive Losses: {m['max_consecutive_losses']}\n\n")
            
            # Time Analysis
            f.write("TIME-BASED ANALYSIS\n")
            f.write("-" * 40 + "\n")
            
            # Best/Worst hours
            hourly_data = time_analysis['hourly']
            best_hour = hourly_data.loc[hourly_data['total_pl'].idxmax()]
            worst_hour = hourly_data.loc[hourly_data['total_pl'].idxmin()]
            
            f.write(f"Best Hour: {int(best_hour['hour']):02d}:00 (P&L: ${best_hour['total_pl']:,.2f})\n")
            f.write(f"Worst Hour: {int(worst_hour['hour']):02d}:00 (P&L: ${worst_hour['total_pl']:,.2f})\n\n")
            
            # Best/Worst days
            daily_data = time_analysis['daily']
            best_day = daily_data.loc[daily_data['total_pl'].idxmax()]
            worst_day = daily_data.loc[daily_data['total_pl'].idxmin()]
            
            f.write(f"Best Day: {best_day['day']} (P&L: ${best_day['total_pl']:,.2f})\n")
            f.write(f"Worst Day: {worst_day['day']} (P&L: ${worst_day['total_pl']:,.2f})\n\n")
            
            # Risk Metrics
            f.write("RISK METRICS\n")
            f.write("-" * 40 + "\n")
            
            # Calculate additional risk metrics
            all_trades = pd.concat([
                self.long_data[self.long_data['side'].str.contains('Buy to Open')],
                self.short_data[self.short_data['side'].str.contains('Sell to Open')]
            ], ignore_index=True)
            
            if len(all_trades) > 0:
                returns = all_trades['trade_pl'] / all_trades['price']
                volatility = returns.std()
                var_95 = np.percentile(returns, 5)  # 95% VaR
                
                f.write(f"Volatility: {volatility:.4f}\n")
                f.write(f"95% Value at Risk: {var_95:.4f}\n")
                f.write(f"Largest Single Loss: ${all_trades['trade_pl'].min():,.2f}\n")
                f.write(f"Largest Single Win: ${all_trades['trade_pl'].max():,.2f}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"Report saved to {save_path}")

def main():
    """Main function to run the analysis"""
    # Your trading data (replace with actual data)
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0; 2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0; Total P/L: $1 326.97; Total order(s): 620;"""
    
    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0; 2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0; Total P/L: ($843.03); Total order(s): 619;"""
    
    # Create analyzer and run analysis
    analyzer = TradingAnalyzer()
    
    try:
        analyzer.load_data(long_report, short_report)
        
        # Calculate metrics
        metrics = analyzer.calculate_basic_metrics()
        
        # Print summary
        print("\n" + "="*60)
        print("TRADING STRATEGY ANALYSIS SUMMARY")
        print("="*60)
        
        for strategy in ['long', 'short', 'combined']:
            print(f"\n{strategy.upper()} STRATEGY:")
            m = metrics[strategy]
            print(f"  Total Trades: {m['total_trades']}")
            print(f"  Win Rate: {m['win_rate']:.2%}")
            print(f"  Total P&L: ${m['total_pl']:,.2f}")
            print(f"  Profit Factor: {m['profit_factor']:.2f}")
            print(f"  Max Drawdown: ${m['max_drawdown']:,.2f}")
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        analyzer.generate_visualizations()
        
        # Generate report
        print("\nGenerating detailed report...")
        analyzer.generate_report()
        
        print("\nAnalysis complete! Check the generated files for detailed results.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()