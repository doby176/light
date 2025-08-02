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
            # Try alternative header formats
            for i, line in enumerate(lines):
                if 'Id;' in line and 'Strategy;' in line and 'Side;' in line:
                    data_start = i + 1
                    break
        
        if data_start is None:
            print(f"Debug: Available lines in report:")
            for i, line in enumerate(lines[:5]):  # Show first 5 lines
                print(f"  Line {i}: {line[:100]}...")
            raise ValueError("Could not find data section in report")
        
        # Extract data lines
        data_lines = []
        for line in lines[data_start:]:
            if line.strip() and not line.startswith('Total'):
                data_lines.append(line)
        
        # Parse CSV-like data
        trades = []
        print(f"Processing {len(data_lines)} data lines...")
        
        for i, line in enumerate(data_lines):
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
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line {i+1}: {line[:50]}... - {str(e)}")
                    continue
        
        print(f"Successfully parsed {len(trades)} trades")
        
        df = pd.DataFrame(trades)
        
        # Clean and process data
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%y %I:%M %p')
        except:
            # Try alternative format
            df['datetime'] = pd.to_datetime(df['datetime'])
        
        df['date'] = df['datetime'].dt.date
        df['time'] = df['datetime'].dt.time
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_name()
        df['month'] = df['datetime'].dt.month
        
        # Process P&L columns
        df['trade_pl_clean'] = df['trade_pl'].apply(self._parse_pl)
        df['cumulative_pl_clean'] = df['cumulative_pl'].apply(self._parse_pl)
        
        # Add strategy identifier
        df['strategy_type'] = strategy_name
        
        return df
    
    def _parse_pl(self, pl_str):
        """Parse P&L string to float"""
        if pd.isna(pl_str) or pl_str == '':
            return 0.0
        
        # Remove parentheses and $ signs
        pl_str = str(pl_str).replace('$', '').replace(',', '')
        
        if '(' in pl_str and ')' in pl_str:
            # Negative value
            return -float(pl_str.replace('(', '').replace(')', ''))
        else:
            # Positive value
            return float(pl_str)
    
    def load_data(self, long_report_text, short_report_text):
        """Load both long and short strategy reports"""
        print("Loading trading data...")
        
        try:
            self.long_data = self.parse_thinkorswim_report(long_report_text, "Long")
            print(f"Successfully parsed long strategy data: {len(self.long_data)} trades")
        except Exception as e:
            print(f"Error parsing long strategy data: {str(e)}")
            self.long_data = pd.DataFrame()
        
        try:
            self.short_data = self.parse_thinkorswim_report(short_report_text, "Short")
            print(f"Successfully parsed short strategy data: {len(self.short_data)} trades")
        except Exception as e:
            print(f"Error parsing short strategy data: {str(e)}")
            self.short_data = pd.DataFrame()
        
        # Combine data
        if len(self.long_data) > 0 or len(self.short_data) > 0:
            self.combined_data = pd.concat([self.long_data, self.short_data], ignore_index=True)
            if len(self.combined_data) > 0:
                self.combined_data = self.combined_data.sort_values('datetime')
                print(f"Combined data: {len(self.combined_data)} total trades")
                print(f"Date range: {self.combined_data['datetime'].min()} to {self.combined_data['datetime'].max()}")
            else:
                print("No valid trades found in combined data")
        else:
            print("No valid data found in either strategy")
            self.combined_data = pd.DataFrame()
    
    def calculate_basic_metrics(self, data):
        """Calculate basic trading metrics"""
        # Filter for completed trades (non-zero P&L)
        completed_trades = data[data['trade_pl_clean'] != 0].copy()
        
        if len(completed_trades) == 0:
            return {}
        
        # Basic metrics
        total_trades = len(completed_trades)
        winning_trades = completed_trades[completed_trades['trade_pl_clean'] > 0]
        losing_trades = completed_trades[completed_trades['trade_pl_clean'] < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_pl = completed_trades['trade_pl_clean'].sum()
        
        avg_winner = winning_trades['trade_pl_clean'].mean() if len(winning_trades) > 0 else 0
        avg_loser = losing_trades['trade_pl_clean'].mean() if len(losing_trades) > 0 else 0
        
        gross_profit = winning_trades['trade_pl_clean'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['trade_pl_clean'].sum()) if len(losing_trades) > 0 else 0
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Risk metrics
        max_winner = completed_trades['trade_pl_clean'].max()
        max_loser = completed_trades['trade_pl_clean'].min()
        
        # Calculate drawdown
        cumulative_pl = completed_trades['cumulative_pl_clean'].values
        running_max = np.maximum.accumulate(cumulative_pl)
        drawdown = cumulative_pl - running_max
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (simplified - assuming daily returns)
        daily_returns = completed_trades.groupby('date')['trade_pl_clean'].sum()
        sharpe_ratio = daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pl': total_pl,
            'avg_winner': avg_winner,
            'avg_loser': avg_loser,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'profit_factor': profit_factor,
            'max_winner': max_winner,
            'max_loser': max_loser,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_trade': total_pl / total_trades if total_trades > 0 else 0
        }
    
    def analyze_time_performance(self, data):
        """Analyze performance by time of day"""
        completed_trades = data[data['trade_pl_clean'] != 0].copy()
        
        if len(completed_trades) == 0:
            return pd.DataFrame()
        
        # Hourly analysis
        hourly_analysis = completed_trades.groupby('hour').agg({
            'trade_pl_clean': ['count', 'sum', 'mean'],
            'datetime': 'count'
        }).round(2)
        
        hourly_analysis.columns = ['trade_count', 'total_pl', 'avg_pl', 'total_trades']
        hourly_analysis = hourly_analysis.reset_index()
        
        # Day of week analysis
        daily_analysis = completed_trades.groupby('day_of_week').agg({
            'trade_pl_clean': ['count', 'sum', 'mean']
        }).round(2)
        
        daily_analysis.columns = ['trade_count', 'total_pl', 'avg_pl']
        daily_analysis = daily_analysis.reset_index()
        
        return hourly_analysis, daily_analysis
    
    def generate_visualizations(self, save_path='trading_analysis_plots.png'):
        """Generate comprehensive visualizations"""
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        fig.suptitle('ThinkorSwim Trading Strategy Analysis', fontsize=16, fontweight='bold')
        
        # 1. Cumulative P&L
        ax1 = axes[0, 0]
        for strategy in ['Long', 'Short']:
            data = self.long_data if strategy == 'Long' else self.short_data
            completed_trades = data[data['trade_pl_clean'] != 0]
            if len(completed_trades) > 0:
                ax1.plot(completed_trades['datetime'], completed_trades['cumulative_pl_clean'], 
                        label=f'{strategy} Strategy', linewidth=2)
        ax1.set_title('Cumulative P&L Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Cumulative P&L ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Trade P&L Distribution
        ax2 = axes[0, 1]
        all_trades = pd.concat([
            self.long_data[self.long_data['trade_pl_clean'] != 0]['trade_pl_clean'],
            self.short_data[self.short_data['trade_pl_clean'] != 0]['trade_pl_clean']
        ])
        ax2.hist(all_trades, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.axvline(all_trades.mean(), color='red', linestyle='--', label=f'Mean: ${all_trades.mean():.2f}')
        ax2.set_title('Trade P&L Distribution')
        ax2.set_xlabel('Trade P&L ($)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        
        # 3. Win Rate Comparison
        ax3 = axes[0, 2]
        long_metrics = self.calculate_basic_metrics(self.long_data)
        short_metrics = self.calculate_basic_metrics(self.short_data)
        
        strategies = ['Long', 'Short']
        win_rates = [long_metrics.get('win_rate', 0), short_metrics.get('win_rate', 0)]
        colors = ['green', 'red']
        
        bars = ax3.bar(strategies, win_rates, color=colors, alpha=0.7)
        ax3.set_title('Win Rate by Strategy')
        ax3.set_ylabel('Win Rate')
        ax3.set_ylim(0, 1)
        
        # Add percentage labels on bars
        for bar, rate in zip(bars, win_rates):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{rate:.1%}', ha='center', va='bottom')
        
        # 4. Hourly Performance
        ax4 = axes[1, 0]
        hourly_long, _ = self.analyze_time_performance(self.long_data)
        hourly_short, _ = self.analyze_time_performance(self.short_data)
        
        if len(hourly_long) > 0:
            ax4.plot(hourly_long['hour'], hourly_long['total_pl'], 'o-', label='Long', color='green')
        if len(hourly_short) > 0:
            ax4.plot(hourly_short['hour'], hourly_short['total_pl'], 'o-', label='Short', color='red')
        
        ax4.set_title('P&L by Hour of Day')
        ax4.set_xlabel('Hour')
        ax4.set_ylabel('Total P&L ($)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Daily Performance
        ax5 = axes[1, 1]
        _, daily_long = self.analyze_time_performance(self.long_data)
        _, daily_short = self.analyze_time_performance(self.short_data)
        
        if len(daily_long) > 0:
            ax5.bar([f"{d} (L)" for d in daily_long['day_of_week']], daily_long['total_pl'], 
                   alpha=0.7, color='green', label='Long')
        if len(daily_short) > 0:
            ax5.bar([f"{d} (S)" for d in daily_short['day_of_week']], daily_short['total_pl'], 
                   alpha=0.7, color='red', label='Short')
        
        ax5.set_title('P&L by Day of Week')
        ax5.set_xlabel('Day of Week')
        ax5.set_ylabel('Total P&L ($)')
        ax5.legend()
        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
        
        # 6. Drawdown Analysis
        ax6 = axes[1, 2]
        for strategy in ['Long', 'Short']:
            data = self.long_data if strategy == 'Long' else self.short_data
            completed_trades = data[data['trade_pl_clean'] != 0]
            if len(completed_trades) > 0:
                cumulative_pl = completed_trades['cumulative_pl_clean'].values
                running_max = np.maximum.accumulate(cumulative_pl)
                drawdown = cumulative_pl - running_max
                ax6.plot(completed_trades['datetime'], drawdown, label=f'{strategy} Strategy', linewidth=2)
        
        ax6.set_title('Drawdown Over Time')
        ax6.set_xlabel('Date')
        ax6.set_ylabel('Drawdown ($)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. Trade Size Analysis
        ax7 = axes[2, 0]
        long_trades = self.long_data[self.long_data['trade_pl_clean'] != 0]['trade_pl_clean']
        short_trades = self.short_data[self.short_data['trade_pl_clean'] != 0]['trade_pl_clean']
        
        if len(long_trades) > 0:
            ax7.boxplot(long_trades, positions=[1], labels=['Long'], patch_artist=True, 
                       boxprops=dict(facecolor='lightgreen'))
        if len(short_trades) > 0:
            ax7.boxplot(short_trades, positions=[2], labels=['Short'], patch_artist=True,
                       boxprops=dict(facecolor='lightcoral'))
        
        ax7.set_title('Trade P&L Distribution by Strategy')
        ax7.set_ylabel('Trade P&L ($)')
        ax7.grid(True, alpha=0.3)
        
        # 8. Monthly Performance
        ax8 = axes[2, 1]
        monthly_pl = self.combined_data[self.combined_data['trade_pl_clean'] != 0].groupby('month')['trade_pl_clean'].sum()
        ax8.bar(monthly_pl.index, monthly_pl.values, alpha=0.7, color='steelblue')
        ax8.set_title('Monthly P&L')
        ax8.set_xlabel('Month')
        ax8.set_ylabel('Total P&L ($)')
        ax8.set_xticks(range(1, 13))
        ax8.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        
        # 9. Strategy Comparison
        ax9 = axes[2, 2]
        metrics = ['total_pl', 'win_rate', 'profit_factor', 'avg_trade']
        long_values = [long_metrics.get(m, 0) for m in metrics]
        short_values = [short_metrics.get(m, 0) for m in metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        ax9.bar(x - width/2, long_values, width, label='Long', alpha=0.7, color='green')
        ax9.bar(x + width/2, short_values, width, label='Short', alpha=0.7, color='red')
        
        ax9.set_title('Strategy Comparison')
        ax9.set_xticks(x)
        ax9.set_xticklabels(['Total P&L', 'Win Rate', 'Profit Factor', 'Avg Trade'])
        ax9.legend()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Visualizations saved to {save_path}")
    
    def print_comprehensive_report(self):
        """Print comprehensive trading analysis report"""
        print("=" * 80)
        print("THINKORSWIM TRADING STRATEGY ANALYSIS REPORT")
        print("=" * 80)
        
        # Overall statistics
        print(f"\n📊 OVERALL STATISTICS")
        print(f"Date Range: {self.combined_data['datetime'].min().strftime('%Y-%m-%d')} to {self.combined_data['datetime'].max().strftime('%Y-%m-%d')}")
        print(f"Total Trading Days: {(self.combined_data['datetime'].max() - self.combined_data['datetime'].min()).days}")
        print(f"Total Trades: {len(self.combined_data[self.combined_data['trade_pl_clean'] != 0])}")
        
        # Strategy-specific analysis
        for strategy_name, data in [("LONG STRATEGY", self.long_data), ("SHORT STRATEGY", self.short_data)]:
            print(f"\n{'='*50}")
            print(f"{strategy_name} ANALYSIS")
            print(f"{'='*50}")
            
            metrics = self.calculate_basic_metrics(data)
            
            if not metrics:
                print("No completed trades found.")
                continue
            
            print(f"📈 PERFORMANCE METRICS:")
            print(f"   Total Trades: {metrics['total_trades']}")
            print(f"   Winning Trades: {metrics['winning_trades']}")
            print(f"   Losing Trades: {metrics['losing_trades']}")
            print(f"   Win Rate: {metrics['win_rate']:.2%}")
            print(f"   Total P&L: ${metrics['total_pl']:,.2f}")
            print(f"   Average Winner: ${metrics['avg_winner']:,.2f}")
            print(f"   Average Loser: ${metrics['avg_loser']:,.2f}")
            print(f"   Average Trade: ${metrics['avg_trade']:,.2f}")
            print(f"   Gross Profit: ${metrics['gross_profit']:,.2f}")
            print(f"   Gross Loss: ${metrics['gross_loss']:,.2f}")
            print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"   Max Winner: ${metrics['max_winner']:,.2f}")
            print(f"   Max Loser: ${metrics['max_loser']:,.2f}")
            print(f"   Max Drawdown: ${metrics['max_drawdown']:,.2f}")
            print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            
            # Time-based analysis
            hourly_analysis, daily_analysis = self.analyze_time_performance(data)
            
            if len(hourly_analysis) > 0:
                print(f"\n⏰ TIME-BASED ANALYSIS:")
                print(f"   Best Hour: {hourly_analysis.loc[hourly_analysis['total_pl'].idxmax(), 'hour']}:00 ({hourly_analysis['total_pl'].max():.2f})")
                print(f"   Worst Hour: {hourly_analysis.loc[hourly_analysis['total_pl'].idxmin(), 'hour']}:00 ({hourly_analysis['total_pl'].min():.2f})")
            
            if len(daily_analysis) > 0:
                best_day = daily_analysis.loc[daily_analysis['total_pl'].idxmax()]
                worst_day = daily_analysis.loc[daily_analysis['total_pl'].idxmin()]
                print(f"   Best Day: {best_day['day_of_week']} (${best_day['total_pl']:.2f})")
                print(f"   Worst Day: {worst_day['day_of_week']} (${worst_day['total_pl']:.2f})")
        
        # Combined analysis
        print(f"\n{'='*50}")
        print("COMBINED STRATEGY ANALYSIS")
        print(f"{'='*50}")
        
        combined_metrics = self.calculate_basic_metrics(self.combined_data)
        if combined_metrics:
            print(f"📊 COMBINED PERFORMANCE:")
            print(f"   Total P&L: ${combined_metrics['total_pl']:,.2f}")
            print(f"   Win Rate: {combined_metrics['win_rate']:.2%}")
            print(f"   Profit Factor: {combined_metrics['profit_factor']:.2f}")
            print(f"   Max Drawdown: ${combined_metrics['max_drawdown']:,.2f}")
            print(f"   Sharpe Ratio: {combined_metrics['sharpe_ratio']:.2f}")
        
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}")

def main():
    """Main function to run the analysis"""
    # Sample data (replace with your actual data)
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0; 2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0; Total P/L: $1 326.97; Total order(s): 620;"""
    
    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0; 2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0; Total P/L: ($843.03); Total order(s): 619;"""
    
    # Initialize analyzer
    analyzer = TradingAnalyzer()
    
    try:
        # Load data
        analyzer.load_data(long_report, short_report)
        
        # Generate comprehensive report
        analyzer.print_comprehensive_report()
        
        # Generate visualizations
        analyzer.generate_visualizations()
        
        print("\n✅ Analysis complete! Check the generated plots for visual insights.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("Please check your data format and try again.")

if __name__ == "__main__":
    main()