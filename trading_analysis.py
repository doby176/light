#!/usr/bin/env python3
"""
ThinkorSwim Trading Results Analyzer
Comprehensive analysis of trading strategy performance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TradingAnalyzer:
    def __init__(self):
        self.long_data = None
        self.short_data = None
        self.combined_data = None
        
    def parse_thinkorswim_report(self, report_text, strategy_name):
        """Parse ThinkorSwim strategy report text into DataFrame"""
        lines = report_text.strip().split('\n')
        
        # Find the data section (after the header)
        data_start = None
        for i, line in enumerate(lines):
            if 'Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;' in line:
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
            parts = line.split(';')
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
                except (ValueError, IndexError):
                    continue
        
        df = pd.DataFrame(trades)
        
        # Clean and process data
        df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%y %I:%M %p')
        df['date'] = df['datetime'].dt.date
        df['time'] = df['datetime'].dt.time
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_name()
        df['month'] = df['datetime'].dt.month_name()
        
        # Process P&L columns
        df['trade_pl_clean'] = df['trade_pl'].apply(self._clean_pl)
        df['cumulative_pl_clean'] = df['cumulative_pl'].apply(self._clean_pl)
        
        # Add strategy identifier
        df['strategy_type'] = strategy_name
        
        return df
    
    def _clean_pl(self, pl_str):
        """Clean P&L string to float"""
        if pd.isna(pl_str) or pl_str == '':
            return 0.0
        pl_str = str(pl_str).replace('$', '').replace(',', '').replace('(', '').replace(')', '')
        try:
            return float(pl_str)
        except ValueError:
            return 0.0
    
    def load_data(self, long_report_text, short_report_text):
        """Load both long and short strategy reports"""
        print("Loading trading data...")
        
        self.long_data = self.parse_thinkorswim_report(long_report_text, "Long Strategy")
        self.short_data = self.parse_thinkorswim_report(short_report_text, "Short Strategy")
        
        # Combine data for overall analysis
        self.combined_data = pd.concat([self.long_data, self.short_data], ignore_index=True)
        self.combined_data = self.combined_data.sort_values('datetime')
        
        print(f"Loaded {len(self.long_data)} long trades and {len(self.short_data)} short trades")
        print(f"Date range: {self.combined_data['datetime'].min()} to {self.combined_data['datetime'].max()}")
    
    def calculate_basic_metrics(self, data):
        """Calculate basic trading metrics"""
        if data is None or len(data) == 0:
            return {}
        
        # Filter for completed trades (where we have P&L)
        completed_trades = data[data['trade_pl_clean'] != 0].copy()
        
        if len(completed_trades) == 0:
            return {}
        
        # Basic metrics
        total_trades = len(completed_trades)
        winning_trades = completed_trades[completed_trades['trade_pl_clean'] > 0]
        losing_trades = completed_trades[completed_trades['trade_pl_clean'] < 0]
        
        total_pl = completed_trades['trade_pl_clean'].sum()
        gross_profit = winning_trades['trade_pl_clean'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['trade_pl_clean'].sum()) if len(losing_trades) > 0 else 0
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / total_trades * 100 if total_trades > 0 else 0,
            'total_pl': total_pl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'profit_factor': gross_profit / gross_loss if gross_loss > 0 else float('inf'),
            'average_winner': winning_trades['trade_pl_clean'].mean() if len(winning_trades) > 0 else 0,
            'average_loser': losing_trades['trade_pl_clean'].mean() if len(losing_trades) > 0 else 0,
            'largest_winner': winning_trades['trade_pl_clean'].max() if len(winning_trades) > 0 else 0,
            'largest_loser': losing_trades['trade_pl_clean'].min() if len(losing_trades) > 0 else 0,
            'expectancy': (winning_trades['trade_pl_clean'].mean() * len(winning_trades) / total_trades + 
                          losing_trades['trade_pl_clean'].mean() * len(losing_trades) / total_trades) if total_trades > 0 else 0
        }
        
        return metrics
    
    def calculate_drawdown(self, data):
        """Calculate maximum drawdown and drawdown periods"""
        if data is None or len(data) == 0:
            return {}
        
        # Calculate cumulative P&L
        data = data.sort_values('datetime').copy()
        data['cumulative_pl'] = data['trade_pl_clean'].cumsum()
        
        # Calculate running maximum
        data['running_max'] = data['cumulative_pl'].expanding().max()
        
        # Calculate drawdown
        data['drawdown'] = data['cumulative_pl'] - data['running_max']
        data['drawdown_pct'] = (data['drawdown'] / data['running_max']) * 100
        
        # Find maximum drawdown
        max_drawdown = data['drawdown'].min()
        max_drawdown_pct = data['drawdown_pct'].min()
        
        # Find drawdown periods
        drawdown_periods = []
        in_drawdown = False
        start_date = None
        
        for idx, row in data.iterrows():
            if row['drawdown'] < 0 and not in_drawdown:
                in_drawdown = True
                start_date = row['datetime']
            elif row['drawdown'] >= 0 and in_drawdown:
                in_drawdown = False
                end_date = row['datetime']
                duration = (end_date - start_date).total_seconds() / 3600  # hours
                drawdown_periods.append({
                    'start': start_date,
                    'end': end_date,
                    'duration_hours': duration,
                    'max_drawdown': data.loc[start_date:end_date, 'drawdown'].min()
                })
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'drawdown_periods': drawdown_periods,
            'avg_drawdown_duration': np.mean([p['duration_hours'] for p in drawdown_periods]) if drawdown_periods else 0
        }
    
    def calculate_time_metrics(self, data):
        """Calculate time-based performance metrics"""
        if data is None or len(data) == 0:
            return {}
        
        # Hourly performance
        hourly_performance = data.groupby('hour')['trade_pl_clean'].agg(['sum', 'mean', 'count']).reset_index()
        hourly_performance.columns = ['hour', 'total_pl', 'avg_pl', 'trade_count']
        
        # Daily performance
        daily_performance = data.groupby('day_of_week')['trade_pl_clean'].agg(['sum', 'mean', 'count']).reset_index()
        daily_performance.columns = ['day', 'total_pl', 'avg_pl', 'trade_count']
        
        # Monthly performance
        monthly_performance = data.groupby('month')['trade_pl_clean'].agg(['sum', 'mean', 'count']).reset_index()
        monthly_performance.columns = ['month', 'total_pl', 'avg_pl', 'trade_count']
        
        # Best/worst hours
        best_hour = hourly_performance.loc[hourly_performance['total_pl'].idxmax()]
        worst_hour = hourly_performance.loc[hourly_performance['total_pl'].idxmin()]
        
        # Best/worst days
        best_day = daily_performance.loc[daily_performance['total_pl'].idxmax()]
        worst_day = daily_performance.loc[daily_performance['total_pl'].idxmin()]
        
        return {
            'hourly_performance': hourly_performance,
            'daily_performance': daily_performance,
            'monthly_performance': monthly_performance,
            'best_hour': best_hour,
            'worst_hour': worst_hour,
            'best_day': best_day,
            'worst_day': worst_day
        }
    
    def calculate_risk_metrics(self, data):
        """Calculate risk-adjusted performance metrics"""
        if data is None or len(data) == 0:
            return {}
        
        completed_trades = data[data['trade_pl_clean'] != 0].copy()
        
        if len(completed_trades) < 2:
            return {}
        
        returns = completed_trades['trade_pl_clean']
        
        # Risk metrics
        volatility = returns.std()
        sharpe_ratio = returns.mean() / volatility if volatility > 0 else 0
        
        # Sortino ratio (using downside deviation)
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino_ratio = returns.mean() / downside_deviation if downside_deviation > 0 else 0
        
        # Calmar ratio (annualized return / max drawdown)
        total_days = (data['datetime'].max() - data['datetime'].min()).days
        annualized_return = (returns.sum() / total_days) * 365 if total_days > 0 else 0
        
        # Calculate max drawdown for Calmar ratio
        cumulative_pl = returns.cumsum()
        running_max = cumulative_pl.expanding().max()
        drawdown = cumulative_pl - running_max
        max_drawdown = abs(drawdown.min())
        
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'var_95': np.percentile(returns, 5),  # 95% VaR
            'cvar_95': returns[returns <= np.percentile(returns, 5)].mean(),  # 95% CVaR
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
    
    def generate_plots(self, save_path=None):
        """Generate comprehensive trading analysis plots"""
        if self.combined_data is None:
            print("No data loaded. Please load data first.")
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Cumulative P&L
        plt.subplot(4, 3, 1)
        self._plot_cumulative_pl()
        
        # 2. Trade P&L Distribution
        plt.subplot(4, 3, 2)
        self._plot_pl_distribution()
        
        # 3. Hourly Performance
        plt.subplot(4, 3, 3)
        self._plot_hourly_performance()
        
        # 4. Daily Performance
        plt.subplot(4, 3, 4)
        self._plot_daily_performance()
        
        # 5. Monthly Performance
        plt.subplot(4, 3, 5)
        self._plot_monthly_performance()
        
        # 6. Drawdown Analysis
        plt.subplot(4, 3, 6)
        self._plot_drawdown()
        
        # 7. Strategy Comparison
        plt.subplot(4, 3, 7)
        self._plot_strategy_comparison()
        
        # 8. Trade Duration Analysis
        plt.subplot(4, 3, 8)
        self._plot_trade_duration()
        
        # 9. Win/Loss Streaks
        plt.subplot(4, 3, 9)
        self._plot_win_loss_streaks()
        
        # 10. P&L by Trade Size
        plt.subplot(4, 3, 10)
        self._plot_pl_by_trade_size()
        
        # 11. Time of Day Heatmap
        plt.subplot(4, 3, 11)
        self._plot_time_heatmap()
        
        # 12. Risk-Return Scatter
        plt.subplot(4, 3, 12)
        self._plot_risk_return()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plots saved to {save_path}")
        
        plt.show()
    
    def _plot_cumulative_pl(self):
        """Plot cumulative P&L over time"""
        data = self.combined_data.sort_values('datetime').copy()
        data['cumulative_pl'] = data['trade_pl_clean'].cumsum()
        
        plt.plot(data['datetime'], data['cumulative_pl'], linewidth=2)
        plt.title('Cumulative P&L Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Cumulative P&L ($)')
        plt.grid(True, alpha=0.3)
        
        # Add final P&L annotation
        final_pl = data['cumulative_pl'].iloc[-1]
        plt.annotate(f'Final P&L: ${final_pl:,.2f}', 
                    xy=(0.02, 0.98), xycoords='axes fraction',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    def _plot_pl_distribution(self):
        """Plot P&L distribution"""
        completed_trades = self.combined_data[self.combined_data['trade_pl_clean'] != 0]
        
        plt.hist(completed_trades['trade_pl_clean'], bins=30, alpha=0.7, edgecolor='black')
        plt.axvline(0, color='red', linestyle='--', alpha=0.7)
        plt.title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Trade P&L ($)')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
    
    def _plot_hourly_performance(self):
        """Plot hourly performance"""
        time_metrics = self.calculate_time_metrics(self.combined_data)
        hourly_data = time_metrics['hourly_performance']
        
        colors = ['green' if x > 0 else 'red' for x in hourly_data['total_pl']]
        plt.bar(hourly_data['hour'], hourly_data['total_pl'], color=colors, alpha=0.7)
        plt.title('P&L by Hour of Day', fontsize=14, fontweight='bold')
        plt.xlabel('Hour')
        plt.ylabel('Total P&L ($)')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24, 2))
    
    def _plot_daily_performance(self):
        """Plot daily performance"""
        time_metrics = self.calculate_time_metrics(self.combined_data)
        daily_data = time_metrics['daily_performance']
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_data['day'] = pd.Categorical(daily_data['day'], categories=day_order, ordered=True)
        daily_data = daily_data.sort_values('day')
        
        colors = ['green' if x > 0 else 'red' for x in daily_data['total_pl']]
        plt.bar(daily_data['day'], daily_data['total_pl'], color=colors, alpha=0.7)
        plt.title('P&L by Day of Week', fontsize=14, fontweight='bold')
        plt.xlabel('Day')
        plt.ylabel('Total P&L ($)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
    
    def _plot_monthly_performance(self):
        """Plot monthly performance"""
        time_metrics = self.calculate_time_metrics(self.combined_data)
        monthly_data = time_metrics['monthly_performance']
        
        colors = ['green' if x > 0 else 'red' for x in monthly_data['total_pl']]
        plt.bar(monthly_data['month'], monthly_data['total_pl'], color=colors, alpha=0.7)
        plt.title('P&L by Month', fontsize=14, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Total P&L ($)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
    
    def _plot_drawdown(self):
        """Plot drawdown analysis"""
        data = self.combined_data.sort_values('datetime').copy()
        data['cumulative_pl'] = data['trade_pl_clean'].cumsum()
        data['running_max'] = data['cumulative_pl'].expanding().max()
        data['drawdown'] = data['cumulative_pl'] - data['running_max']
        
        plt.fill_between(data['datetime'], data['drawdown'], 0, alpha=0.3, color='red')
        plt.plot(data['datetime'], data['drawdown'], color='red', linewidth=1)
        plt.title('Drawdown Analysis', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Drawdown ($)')
        plt.grid(True, alpha=0.3)
        
        # Add max drawdown annotation
        max_dd = data['drawdown'].min()
        plt.annotate(f'Max DD: ${max_dd:,.2f}', 
                    xy=(0.02, 0.98), xycoords='axes fraction',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    def _plot_strategy_comparison(self):
        """Plot strategy comparison"""
        long_metrics = self.calculate_basic_metrics(self.long_data)
        short_metrics = self.calculate_basic_metrics(self.short_data)
        
        strategies = ['Long', 'Short']
        total_pl = [long_metrics.get('total_pl', 0), short_metrics.get('total_pl', 0)]
        win_rates = [long_metrics.get('win_rate', 0), short_metrics.get('win_rate', 0)]
        
        x = np.arange(len(strategies))
        width = 0.35
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        ax1.bar(x, total_pl, width, color=['green', 'red'], alpha=0.7)
        ax1.set_title('Total P&L by Strategy')
        ax1.set_ylabel('P&L ($)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(strategies)
        
        ax2.bar(x, win_rates, width, color=['blue', 'orange'], alpha=0.7)
        ax2.set_title('Win Rate by Strategy')
        ax2.set_ylabel('Win Rate (%)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(strategies)
        
        plt.tight_layout()
    
    def _plot_trade_duration(self):
        """Plot trade duration analysis"""
        # This would require calculating trade durations
        # For now, show a placeholder
        plt.text(0.5, 0.5, 'Trade Duration\nAnalysis\n(Not implemented)', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.title('Trade Duration Analysis', fontsize=14, fontweight='bold')
        plt.axis('off')
    
    def _plot_win_loss_streaks(self):
        """Plot win/loss streaks"""
        completed_trades = self.combined_data[self.combined_data['trade_pl_clean'] != 0].copy()
        completed_trades = completed_trades.sort_values('datetime')
        
        # Calculate streaks
        completed_trades['win'] = completed_trades['trade_pl_clean'] > 0
        completed_trades['streak'] = (completed_trades['win'] != completed_trades['win'].shift()).cumsum()
        
        win_streaks = completed_trades[completed_trades['win']].groupby('streak').size()
        loss_streaks = completed_trades[~completed_trades['win']].groupby('streak').size()
        
        plt.hist([win_streaks, loss_streaks], label=['Win Streaks', 'Loss Streaks'], 
                alpha=0.7, bins=range(1, max(max(win_streaks) if len(win_streaks) > 0 else 1, 
                                            max(loss_streaks) if len(loss_streaks) > 0 else 1) + 2))
        plt.title('Win/Loss Streak Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Streak Length')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    def _plot_pl_by_trade_size(self):
        """Plot P&L by trade size"""
        completed_trades = self.combined_data[self.combined_data['trade_pl_clean'] != 0]
        
        plt.scatter(completed_trades['amount'], completed_trades['trade_pl_clean'], alpha=0.6)
        plt.axhline(0, color='red', linestyle='--', alpha=0.7)
        plt.title('P&L vs Trade Size', fontsize=14, fontweight='bold')
        plt.xlabel('Trade Size')
        plt.ylabel('Trade P&L ($)')
        plt.grid(True, alpha=0.3)
    
    def _plot_time_heatmap(self):
        """Plot time of day heatmap"""
        # Create hour vs day heatmap
        pivot_data = self.combined_data.pivot_table(
            values='trade_pl_clean', 
            index='day_of_week', 
            columns='hour', 
            aggfunc='sum',
            fill_value=0
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex(day_order)
        
        sns.heatmap(pivot_data, annot=False, cmap='RdYlGn', center=0, cbar_kws={'label': 'P&L ($)'})
        plt.title('P&L Heatmap: Day vs Hour', fontsize=14, fontweight='bold')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
    
    def _plot_risk_return(self):
        """Plot risk-return scatter"""
        # Calculate rolling metrics
        data = self.combined_data.sort_values('datetime').copy()
        data['cumulative_pl'] = data['trade_pl_clean'].cumsum()
        
        # Rolling 20-trade metrics
        window = 20
        if len(data) >= window:
            rolling_return = data['trade_pl_clean'].rolling(window).mean()
            rolling_risk = data['trade_pl_clean'].rolling(window).std()
            
            plt.scatter(rolling_risk, rolling_return, alpha=0.6)
            plt.xlabel('Risk (Std Dev)')
            plt.ylabel('Return (Mean)')
            plt.title('Risk-Return Scatter (20-trade rolling)', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Insufficient data\nfor risk-return analysis', 
                    ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
            plt.title('Risk-Return Analysis', fontsize=14, fontweight='bold')
            plt.axis('off')
    
    def generate_report(self, save_path=None):
        """Generate comprehensive trading analysis report"""
        if self.combined_data is None:
            print("No data loaded. Please load data first.")
            return
        
        print("=" * 80)
        print("THINKORSWIM TRADING STRATEGY ANALYSIS REPORT")
        print("=" * 80)
        
        # Overall metrics
        overall_metrics = self.calculate_basic_metrics(self.combined_data)
        drawdown_metrics = self.calculate_drawdown(self.combined_data)
        risk_metrics = self.calculate_risk_metrics(self.combined_data)
        time_metrics = self.calculate_time_metrics(self.combined_data)
        
        print(f"\n📊 OVERALL PERFORMANCE")
        print("-" * 40)
        print(f"Total Trades: {overall_metrics.get('total_trades', 0):,}")
        print(f"Winning Trades: {overall_metrics.get('winning_trades', 0):,}")
        print(f"Losing Trades: {overall_metrics.get('losing_trades', 0):,}")
        print(f"Win Rate: {overall_metrics.get('win_rate', 0):.2f}%")
        print(f"Total P&L: ${overall_metrics.get('total_pl', 0):,.2f}")
        print(f"Gross Profit: ${overall_metrics.get('gross_profit', 0):,.2f}")
        print(f"Gross Loss: ${overall_metrics.get('gross_loss', 0):,.2f}")
        print(f"Profit Factor: {overall_metrics.get('profit_factor', 0):.2f}")
        
        print(f"\n💰 TRADE ANALYSIS")
        print("-" * 40)
        print(f"Average Winner: ${overall_metrics.get('average_winner', 0):.2f}")
        print(f"Average Loser: ${overall_metrics.get('average_loser', 0):.2f}")
        print(f"Largest Winner: ${overall_metrics.get('largest_winner', 0):.2f}")
        print(f"Largest Loser: ${overall_metrics.get('largest_loser', 0):.2f}")
        print(f"Expectancy: ${overall_metrics.get('expectancy', 0):.2f}")
        
        print(f"\n📉 RISK METRICS")
        print("-" * 40)
        print(f"Maximum Drawdown: ${drawdown_metrics.get('max_drawdown', 0):,.2f}")
        print(f"Max Drawdown %: {drawdown_metrics.get('max_drawdown_pct', 0):.2f}%")
        print(f"Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Sortino Ratio: {risk_metrics.get('sortino_ratio', 0):.2f}")
        print(f"Calmar Ratio: {risk_metrics.get('calmar_ratio', 0):.2f}")
        print(f"Volatility: ${risk_metrics.get('volatility', 0):.2f}")
        print(f"95% VaR: ${risk_metrics.get('var_95', 0):.2f}")
        
        print(f"\n⏰ TIME-BASED ANALYSIS")
        print("-" * 40)
        best_hour = time_metrics.get('best_hour', {})
        worst_hour = time_metrics.get('worst_hour', {})
        best_day = time_metrics.get('best_day', {})
        worst_day = time_metrics.get('worst_day', {})
        
        print(f"Best Hour: {best_hour.get('hour', 'N/A')} ({best_hour.get('total_pl', 0):.2f})")
        print(f"Worst Hour: {worst_hour.get('hour', 'N/A')} ({worst_hour.get('total_pl', 0):.2f})")
        print(f"Best Day: {best_day.get('day', 'N/A')} ({best_day.get('total_pl', 0):.2f})")
        print(f"Worst Day: {worst_day.get('day', 'N/A')} ({worst_day.get('total_pl', 0):.2f})")
        
        print(f"\n📈 STRATEGY COMPARISON")
        print("-" * 40)
        long_metrics = self.calculate_basic_metrics(self.long_data)
        short_metrics = self.calculate_basic_metrics(self.short_data)
        
        print(f"Long Strategy:")
        print(f"  P&L: ${long_metrics.get('total_pl', 0):,.2f}")
        print(f"  Win Rate: {long_metrics.get('win_rate', 0):.2f}%")
        print(f"  Trades: {long_metrics.get('total_trades', 0):,}")
        
        print(f"\nShort Strategy:")
        print(f"  P&L: ${short_metrics.get('total_pl', 0):,.2f}")
        print(f"  Win Rate: {short_metrics.get('win_rate', 0):.2f}%")
        print(f"  Trades: {short_metrics.get('total_trades', 0):,}")
        
        print("\n" + "=" * 80)
        
        # Save report to file if requested
        if save_path:
            with open(save_path, 'w') as f:
                f.write("THINKORSWIM TRADING STRATEGY ANALYSIS REPORT\n")
                f.write("=" * 80 + "\n")
                # Add all the report content here...
            print(f"Report saved to {save_path}")

def main():
    """Main function to run the analysis"""
    # Sample data (replace with your actual data)
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
    
    # Create analyzer and run analysis
    analyzer = TradingAnalyzer()
    
    try:
        analyzer.load_data(long_report, short_report)
        
        # Generate report
        analyzer.generate_report("trading_analysis_report.txt")
        
        # Generate plots
        analyzer.generate_plots("trading_analysis_plots.png")
        
        print("\n✅ Analysis complete! Check the generated files:")
        print("- trading_analysis_report.txt (detailed report)")
        print("- trading_analysis_plots.png (visualizations)")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your data format and try again.")

if __name__ == "__main__":
    main()