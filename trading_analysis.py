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
        data_lines = []
        in_data_section = False
        
        for line in lines:
            if 'Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;' in line:
                in_data_section = True
                continue
            elif in_data_section and line.strip():
                if 'Total P/L:' in line:  # End of data
                    break
                data_lines.append(line)
        
        # Parse the data
        trades = []
        for line in data_lines:
            if line.strip():
                parts = line.split(';')
                if len(parts) >= 9:
                    try:
                        # Clean up the datetime string
                        datetime_str = parts[5].strip()
                        
                        trade = {
                            'id': int(parts[0]),
                            'strategy': parts[1],
                            'side': parts[2],
                            'amount': float(parts[3]),
                            'price': float(parts[4].replace('$', '').replace(',', '')),
                            'datetime_str': datetime_str,
                            'trade_pl': self._parse_pl(parts[6]),
                            'cumulative_pl': self._parse_pl(parts[7]),
                            'position': float(parts[8])
                        }
                        trades.append(trade)
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Could not parse line: {line[:50]}... Error: {e}")
                        continue
        
        if not trades:
            print(f"No valid trades found for {strategy_name}")
            return pd.DataFrame()
        
        df = pd.DataFrame(trades)
        
        # Convert datetime strings to datetime objects
        try:
            df['datetime'] = pd.to_datetime(df['datetime_str'], format='%m/%d/%y %I:%M %p')
        except Exception as e:
            print(f"Warning: Could not parse datetime for {strategy_name}: {e}")
            # Create a dummy datetime if parsing fails
            df['datetime'] = pd.Timestamp.now()
        
        df['strategy_name'] = strategy_name
        return df
    
    def _parse_pl(self, pl_str):
        """Parse P&L string to float"""
        if not pl_str or pl_str.strip() == '':
            return 0.0
        
        pl_str = pl_str.strip()
        # Remove parentheses and $ signs
        pl_str = pl_str.replace('$', '').replace(',', '')
        
        if pl_str.startswith('(') and pl_str.endswith(')'):
            # Negative value
            return -float(pl_str[1:-1])
        else:
            # Positive value
            return float(pl_str)
    
    def load_data(self, long_report_text, short_report_text):
        """Load both long and short strategy reports"""
        print("Loading trading data...")
        
        self.long_data = self.parse_thinkorswim_report(long_report_text, "Long Strategy")
        self.short_data = self.parse_thinkorswim_report(short_report_text, "Short Strategy")
        
        # Combine data only if both have data
        if not self.long_data.empty and not self.short_data.empty:
            self.combined_data = pd.concat([self.long_data, self.short_data], ignore_index=True)
            self.combined_data = self.combined_data.sort_values('datetime')
        elif not self.long_data.empty:
            self.combined_data = self.long_data.copy()
        elif not self.short_data.empty:
            self.combined_data = self.short_data.copy()
        else:
            self.combined_data = pd.DataFrame()
        
        print(f"Loaded {len(self.long_data)} long trades and {len(self.short_data)} short trades")
        return self.combined_data
    
    def calculate_basic_metrics(self, data):
        """Calculate basic trading metrics"""
        if data.empty:
            return {}
        
        # Filter for completed trades (trades with P&L)
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
        loss_rate = len(losing_trades) / total_trades if total_trades > 0 else 0
        
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
        
        # Sharpe ratio (simplified - assuming risk-free rate of 0)
        returns = completed_trades['trade_pl'].values
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        
        # Average trade duration
        completed_trades['duration'] = completed_trades['datetime'].diff()
        avg_duration = completed_trades['duration'].mean()
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'loss_rate': loss_rate,
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
            'avg_duration': avg_duration
        }
    
    def calculate_time_based_metrics(self, data):
        """Calculate time-based performance metrics"""
        if data.empty:
            return {}
        
        # Add time components
        data = data.copy()
        data['hour'] = data['datetime'].dt.hour
        data['day_of_week'] = data['datetime'].dt.day_name()
        data['month'] = data['datetime'].dt.month
        data['date'] = data['datetime'].dt.date
        
        # Hourly analysis
        hourly_pl = data.groupby('hour')['trade_pl'].agg(['sum', 'count', 'mean']).round(2)
        hourly_pl.columns = ['Total P&L', 'Trade Count', 'Avg P&L per Trade']
        
        # Daily analysis
        daily_pl = data.groupby('day_of_week')['trade_pl'].agg(['sum', 'count', 'mean']).round(2)
        daily_pl.columns = ['Total P&L', 'Trade Count', 'Avg P&L per Trade']
        
        # Monthly analysis
        monthly_pl = data.groupby('month')['trade_pl'].agg(['sum', 'count', 'mean']).round(2)
        monthly_pl.columns = ['Total P&L', 'Trade Count', 'Avg P&L per Trade']
        
        return {
            'hourly': hourly_pl,
            'daily': daily_pl,
            'monthly': monthly_pl
        }
    
    def calculate_advanced_metrics(self, data):
        """Calculate advanced trading metrics"""
        if data.empty:
            return {}
        
        completed_trades = data[data['trade_pl'] != 0].copy()
        
        if completed_trades.empty:
            return {}
        
        # Consecutive wins/losses
        completed_trades['is_win'] = completed_trades['trade_pl'] > 0
        completed_trades['win_streak'] = (completed_trades['is_win'] != completed_trades['is_win'].shift()).cumsum()
        completed_trades['loss_streak'] = (completed_trades['is_win'] == completed_trades['is_win'].shift()).cumsum()
        
        # Largest win/loss streaks
        win_streaks = completed_trades[completed_trades['is_win']].groupby('win_streak').size()
        loss_streaks = completed_trades[~completed_trades['is_win']].groupby('loss_streak').size()
        
        max_win_streak = win_streaks.max() if not win_streaks.empty else 0
        max_loss_streak = loss_streaks.max() if not loss_streaks.empty else 0
        
        # Recovery factor
        total_pl = completed_trades['trade_pl'].sum()
        max_dd = abs(self.calculate_basic_metrics(data)['max_drawdown'])
        recovery_factor = total_pl / max_dd if max_dd > 0 else float('inf')
        
        # Expectancy
        win_rate = self.calculate_basic_metrics(data)['win_rate']
        avg_winner = self.calculate_basic_metrics(data)['avg_winner']
        avg_loser = self.calculate_basic_metrics(data)['avg_loser']
        expectancy = (win_rate * avg_winner) + ((1 - win_rate) * avg_loser)
        
        # Risk of ruin (simplified)
        avg_win = avg_winner
        avg_loss = abs(avg_loser)
        win_rate = win_rate
        
        if avg_loss > 0 and win_rate > 0:
            risk_of_ruin = ((1 - win_rate) / win_rate) ** (total_pl / avg_loss)
        else:
            risk_of_ruin = 0
        
        return {
            'max_win_streak': max_win_streak,
            'max_loss_streak': max_loss_streak,
            'recovery_factor': recovery_factor,
            'expectancy': expectancy,
            'risk_of_ruin': risk_of_ruin
        }
    
    def plot_cumulative_pl(self, data, strategy_name="Combined"):
        """Plot cumulative P&L over time"""
        if data.empty:
            print(f"No data to plot for {strategy_name}")
            return
        
        completed_trades = data[data['trade_pl'] != 0].copy()
        
        if completed_trades.empty:
            print(f"No completed trades to plot for {strategy_name}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(completed_trades['datetime'], completed_trades['cumulative_pl'], 
                linewidth=2, color='blue', alpha=0.8)
        
        # Add zero line
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        plt.title(f'Cumulative P&L - {strategy_name}', fontsize=14, fontweight='bold')
        plt.xlabel('Date/Time', fontsize=12)
        plt.ylabel('Cumulative P&L ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_drawdown(self, data, strategy_name="Combined"):
        """Plot drawdown over time"""
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
        plt.show()
    
    def plot_time_analysis(self, time_data, analysis_type="hourly"):
        """Plot time-based analysis"""
        if time_data.empty:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # P&L by time
        time_data['Total P&L'].plot(kind='bar', ax=ax1, color='skyblue', alpha=0.7)
        ax1.set_title(f'{analysis_type.title()} P&L Analysis', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Total P&L ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Trade count by time
        time_data['Trade Count'].plot(kind='bar', ax=ax2, color='lightgreen', alpha=0.7)
        ax2.set_title(f'{analysis_type.title()} Trade Count', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Trades', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_pnl_distribution(self, data, strategy_name="Combined"):
        """Plot P&L distribution"""
        if data.empty:
            return
        
        completed_trades = data[data['trade_pl'] != 0].copy()
        
        if completed_trades.empty:
            return
        
        plt.figure(figsize=(12, 6))
        
        # Histogram
        plt.subplot(1, 2, 1)
        plt.hist(completed_trades['trade_pl'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        plt.title(f'P&L Distribution - {strategy_name}', fontsize=14, fontweight='bold')
        plt.xlabel('Trade P&L ($)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Box plot
        plt.subplot(1, 2, 2)
        plt.boxplot(completed_trades['trade_pl'], patch_artist=True, 
                   boxprops=dict(facecolor='lightgreen', alpha=0.7))
        plt.title(f'P&L Box Plot - {strategy_name}', fontsize=14, fontweight='bold')
        plt.ylabel('Trade P&L ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def generate_report(self, data, strategy_name="Combined"):
        """Generate comprehensive trading report"""
        print(f"\n{'='*60}")
        print(f"TRADING ANALYSIS REPORT - {strategy_name.upper()}")
        print(f"{'='*60}")
        
        # Basic metrics
        basic_metrics = self.calculate_basic_metrics(data)
        if not basic_metrics:
            print("No completed trades found for analysis.")
            return
        
        print(f"\n📊 BASIC METRICS:")
        print(f"{'Total Trades:':<25} {basic_metrics['total_trades']}")
        print(f"{'Winning Trades:':<25} {basic_metrics['winning_trades']}")
        print(f"{'Losing Trades:':<25} {basic_metrics['losing_trades']}")
        print(f"{'Win Rate:':<25} {basic_metrics['win_rate']:.2%}")
        print(f"{'Loss Rate:':<25} {basic_metrics['loss_rate']:.2%}")
        print(f"{'Total P&L:':<25} ${basic_metrics['total_pl']:,.2f}")
        print(f"{'Gross Profit:':<25} ${basic_metrics['gross_profit']:,.2f}")
        print(f"{'Gross Loss:':<25} ${basic_metrics['gross_loss']:,.2f}")
        print(f"{'Average Winner:':<25} ${basic_metrics['avg_winner']:,.2f}")
        print(f"{'Average Loser:':<25} ${basic_metrics['avg_loser']:,.2f}")
        print(f"{'Profit Factor:':<25} {basic_metrics['profit_factor']:.2f}")
        print(f"{'Max Winner:':<25} ${basic_metrics['max_winner']:,.2f}")
        print(f"{'Max Loser:':<25} ${basic_metrics['max_loser']:,.2f}")
        print(f"{'Max Drawdown:':<25} ${basic_metrics['max_drawdown']:,.2f}")
        print(f"{'Sharpe Ratio:':<25} {basic_metrics['sharpe_ratio']:.2f}")
        
        # Advanced metrics
        advanced_metrics = self.calculate_advanced_metrics(data)
        print(f"\n🎯 ADVANCED METRICS:")
        print(f"{'Max Win Streak:':<25} {advanced_metrics['max_win_streak']}")
        print(f"{'Max Loss Streak:':<25} {advanced_metrics['max_loss_streak']}")
        print(f"{'Recovery Factor:':<25} {advanced_metrics['recovery_factor']:.2f}")
        print(f"{'Expectancy:':<25} ${advanced_metrics['expectancy']:,.2f}")
        print(f"{'Risk of Ruin:':<25} {advanced_metrics['risk_of_ruin']:.4f}")
        
        # Time-based analysis
        time_metrics = self.calculate_time_based_metrics(data)
        if time_metrics:
            print(f"\n⏰ TIME-BASED ANALYSIS:")
            
            # Best/worst hours
            hourly = time_metrics['hourly']
            best_hour = hourly['Total P&L'].idxmax()
            worst_hour = hourly['Total P&L'].idxmin()
            print(f"{'Best Hour:':<25} {best_hour}:00 (${hourly.loc[best_hour, 'Total P&L']:,.2f})")
            print(f"{'Worst Hour:':<25} {worst_hour}:00 (${hourly.loc[worst_hour, 'Total P&L']:,.2f})")
            
            # Best/worst days
            daily = time_metrics['daily']
            best_day = daily['Total P&L'].idxmax()
            worst_day = daily['Total P&L'].idxmin()
            print(f"{'Best Day:':<25} {best_day} (${daily.loc[best_day, 'Total P&L']:,.2f})")
            print(f"{'Worst Day:':<25} {worst_day} (${daily.loc[worst_day, 'Total P&L']:,.2f})")
        
        print(f"\n{'='*60}")
    
    def run_complete_analysis(self, long_report_text, short_report_text):
        """Run complete analysis on both strategies"""
        print("🚀 Starting comprehensive trading analysis...")
        
        # Load data
        self.load_data(long_report_text, short_report_text)
        
        # Analyze each strategy separately
        if not self.long_data.empty:
            print("\n" + "="*60)
            print("ANALYZING LONG STRATEGY")
            print("="*60)
            self.generate_report(self.long_data, "Long Strategy")
        
        if not self.short_data.empty:
            print("\n" + "="*60)
            print("ANALYZING SHORT STRATEGY")
            print("="*60)
            self.generate_report(self.short_data, "Short Strategy")
        
        if not self.combined_data.empty:
            print("\n" + "="*60)
            print("ANALYZING COMBINED STRATEGY")
            print("="*60)
            self.generate_report(self.combined_data, "Combined Strategy")
        
        # Generate visualizations
        print("\n📈 Generating visualizations...")
        
        # Cumulative P&L plots
        if not self.long_data.empty:
            self.plot_cumulative_pl(self.long_data, "Long Strategy")
        if not self.short_data.empty:
            self.plot_cumulative_pl(self.short_data, "Short Strategy")
        if not self.combined_data.empty:
            self.plot_cumulative_pl(self.combined_data, "Combined Strategy")
        
        # Drawdown plots
        if not self.long_data.empty:
            self.plot_drawdown(self.long_data, "Long Strategy")
        if not self.short_data.empty:
            self.plot_drawdown(self.short_data, "Short Strategy")
        if not self.combined_data.empty:
            self.plot_drawdown(self.combined_data, "Combined Strategy")
        
        # P&L distribution plots
        if not self.long_data.empty:
            self.plot_pnl_distribution(self.long_data, "Long Strategy")
        if not self.short_data.empty:
            self.plot_pnl_distribution(self.short_data, "Short Strategy")
        if not self.combined_data.empty:
            self.plot_pnl_distribution(self.combined_data, "Combined Strategy")
        
        # Time-based analysis plots
        if not self.combined_data.empty:
            time_metrics = self.calculate_time_based_metrics(self.combined_data)
            if time_metrics:
                self.plot_time_analysis(time_metrics['hourly'], "Hourly")
                self.plot_time_analysis(time_metrics['daily'], "Daily")
                self.plot_time_analysis(time_metrics['monthly'], "Monthly")
        
        print("\n✅ Analysis complete! Check the generated plots and metrics above.")

def main():
    """Main function to run the analysis"""
    # Your trading data (replace with actual data)
    long_report_text = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0; 2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0; Total P/L: $1 326.97; Total order(s): 620;"""
    
    short_report_text = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0; 2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0; Total P/L: ($843.03); Total order(s): 619;"""
    
    # Create analyzer and run analysis
    analyzer = TradingAnalyzer()
    analyzer.run_complete_analysis(long_report_text, short_report_text)

if __name__ == "__main__":
    main()