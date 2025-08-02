#!/usr/bin/env python3
"""
ThinkorSwim Trading Analysis Tool - Standalone Version
Reads directly from your CSV files - No external dependencies needed
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

class TradingAnalyzer:
    def __init__(self):
        self.long_data = None
        self.short_data = None
        self.combined_data = None
        self.metrics = {}
        
    def _parse_pl(self, pl_str: str) -> float:
        """Parse P&L string to float value"""
        if not pl_str or pl_str.strip() == '':
            return 0.0
        
        # Remove parentheses, $ signs, commas, and tabs
        pl_str = pl_str.replace('$', '').replace(',', '').replace('(', '').replace(')', '').replace('\t', '')
        
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
    
    def parse_thinkorswim_csv(self, file_path: str, strategy_name: str = "Strategy") -> pd.DataFrame:
        """
        Parse ThinkorSwim CSV file into a pandas DataFrame
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
            
            # Check if we have the expected columns
            expected_columns = ['Id', 'Strategy', 'Side', 'Amount', 'Price', 'Date/Time', 'Trade P/L', 'P/L', 'Position']
            
            if not all(col in df.columns for col in expected_columns):
                print(f"Warning: Expected columns not found in {file_path}")
                print(f"Found columns: {list(df.columns)}")
                return pd.DataFrame()
            
            # Clean and parse the data
            trades = []
            for _, row in df.iterrows():
                try:
                    # Clean price value (remove tabs and other characters)
                    price_str = str(row['Price']).replace('$', '').replace(',', '').replace('\t', '')
                    price = float(price_str)
                    
                    # Parse datetime
                    dt = pd.to_datetime(row['Date/Time'], format='%m/%d/%y %I:%M %p')
                    
                    # Parse P&L values
                    trade_pl_value = self._parse_pl(str(row['Trade P/L']))
                    cumulative_pl_value = self._parse_pl(str(row['P/L']))
                    
                    trades.append({
                        'id': int(row['Id']),
                        'strategy': str(row['Strategy']),
                        'side': str(row['Side']),
                        'amount': float(row['Amount']),
                        'price': price,
                        'datetime': dt,
                        'trade_pl': trade_pl_value,
                        'cumulative_pl': cumulative_pl_value,
                        'position': float(row['Position'])
                    })
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse row {row['Id']}: {e}")
                    continue
            
            if not trades:
                print(f"No valid trades found in {file_path}")
                return pd.DataFrame()
            
            df = pd.DataFrame(trades)
            
            # Create trade pairs (entry/exit)
            df = self._create_trade_pairs(df)
            
            return df
            
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {e}")
            return pd.DataFrame()
    
    def load_data_from_files(self, long_file_path: str, short_file_path: str):
        """Load and parse both long and short strategy reports from CSV files"""
        print("Parsing Long Strategy Report...")
        self.long_data = self.parse_thinkorswim_csv(long_file_path, "Long Strategy")
        
        print("Parsing Short Strategy Report...")
        self.short_data = self.parse_thinkorswim_csv(short_file_path, "Short Strategy")
        
        # Combine data
        if not self.long_data.empty and not self.short_data.empty:
            self.combined_data = pd.concat([
                self.long_data.assign(strategy_type='Long'),
                self.short_data.assign(strategy_type='Short')
            ], ignore_index=True)
        elif not self.long_data.empty:
            self.combined_data = self.long_data.assign(strategy_type='Long')
        elif not self.short_data.empty:
            self.combined_data = self.short_data.assign(strategy_type='Short')
        else:
            self.combined_data = pd.DataFrame()
        
        print(f"Loaded {len(self.long_data)} long trades and {len(self.short_data)} short trades")
    
    def calculate_metrics(self):
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
    
    def generate_time_analysis(self):
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
    print("🎯 ThinkorSwim Trading Analysis Tool - Standalone Version")
    print("=" * 60)
    
    # File paths - update these to match your actual file names
    base_path = r"C:\Users\ASUS"
    long_file = os.path.join(base_path, "StrategyReports_QQQ_8225long1.csv").replace('/', '\\')
    short_file = os.path.join(base_path, "StrategyReports_QQQ_8225short.csv").replace('/', '\\')
    
    print(f"📁 Looking for files:")
    print(f"   Long strategy: {long_file}")
    print(f"   Short strategy: {short_file}")
    print("=" * 60)
    
    # Check if files exist
    if not os.path.exists(long_file):
        print(f"❌ Long strategy file not found: {long_file}")
        return
    
    if not os.path.exists(short_file):
        print(f"❌ Short strategy file not found: {short_file}")
        return
    
    print("✅ Files found! Starting analysis...")
    
    try:
        # Create analyzer and load data
        analyzer = TradingAnalyzer()
        analyzer.load_data_from_files(long_file, short_file)
        
        if analyzer.combined_data.empty:
            print("❌ No valid data loaded. Check your CSV file format.")
            return
        
        # Calculate metrics
        metrics = analyzer.calculate_metrics()
        
        # Print summary
        analyzer.print_summary_report()
        
        # Generate plots
        print("\n📈 Generating visualizations...")
        analyzer.plot_cumulative_pnl()
        analyzer.plot_time_analysis()
        analyzer.plot_trade_distribution()
        
        # Save detailed report
        analyzer.save_detailed_report()
        
        print("\n🎉 Analysis Complete!")
        print("=" * 60)
        print("📁 Generated Files:")
        print("  • trading_analysis_report.txt - Detailed text report")
        print("  • Multiple PNG charts - Visual analysis")
        print("\n📊 Key Metrics Calculated:")
        print("  • Average Winner/Loser")
        print("  • Profit Factor")
        print("  • Max Drawdown")
        print("  • Sharpe/Sortino Ratios")
        print("  • Win/Loss Rates")
        print("  • Time-based Analysis")
        print("  • Strategy Comparison")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure your CSV files are in the correct ThinkorSwim format")
        print("2. Check that the file paths are correct")
        print("3. Ensure the files have the expected column headers")
        print("4. Verify all dependencies are installed: pip install pandas numpy matplotlib")

if __name__ == "__main__":
    main()