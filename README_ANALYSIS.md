# ThinkorSwim Trading Analysis Tool

A comprehensive Python tool to analyze ThinkorSwim strategy reports and calculate detailed trading performance metrics.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Analysis:**
   ```bash
   python3 analyze_my_trades.py
   ```

3. **Replace Sample Data:**
   - Open `analyze_my_trades.py`
   - Replace the sample data in the `long_report` and `short_report` variables with your actual ThinkorSwim data
   - Run the script again

## 📊 Metrics Calculated

### Basic Performance Metrics
- **Total Trades**: Number of completed trades
- **Total P&L**: Sum of all trade profits/losses
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Average Winner/Loser**: Mean profit/loss per trade

### Risk Metrics
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Sortino Ratio**: Downside risk-adjusted return
- **Recovery Factor**: Total profit / Maximum drawdown

### Advanced Metrics
- **Expectancy**: Expected value per trade
- **Max Win/Loss Streaks**: Longest consecutive wins/losses
- **Risk of Ruin**: Probability of losing entire capital
- **Average Trade Duration**: Mean time per trade

### Time-Based Analysis
- **Hourly Performance**: P&L by hour of day
- **Daily Performance**: P&L by day of week
- **Best/Worst Times**: Optimal trading hours

## 📁 Generated Files

### Text Reports
- `trading_analysis_report.txt`: Detailed analysis with all metrics

### Visual Charts
- **Cumulative P&L Chart**: Shows profit growth over time
- **Time Analysis Charts**: Performance by hour/day
- **Trade Distribution Charts**: P&L distribution and strategy comparison

## 🔧 How to Use Your Data

### Step 1: Get Your ThinkorSwim Report
1. In ThinkorSwim, go to the **Strategies** tab
2. Right-click on your strategy
3. Select **"Export Strategy Report"**
4. Copy the text content

### Step 2: Format Your Data
Your data should look like this:
```
Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
Total P/L: $1 326.97; Total order(s): 620;
```

### Step 3: Paste Your Data
1. Open `analyze_my_trades.py`
2. Find the `long_report` and `short_report` variables
3. Replace the sample data with your actual reports
4. Save and run the script

## 📈 Sample Results

```
================================================================================
THINKORSWIM TRADING STRATEGY ANALYSIS REPORT
================================================================================

📊 OVERALL PERFORMANCE:
   Total Trades: 620
   Total P&L: $1,326.97
   Total Return: 2.49%
   Win Rate: 58.7%
   Profit Factor: 1.42
   Max Drawdown: $234.50

💰 TRADE METRICS:
   Average Winner: $45.23
   Average Loser: $32.15
   Average Trade: $2.14
   Average Return: 0.004%
   Average Duration: 15.3 minutes

📈 RISK METRICS:
   Sharpe Ratio: 1.85
   Sortino Ratio: 2.12

🎯 STRATEGY BREAKDOWN:
   Long Strategy:
     Trades: 310
     P&L: $678.45
     Win Rate: 62.3%
   Short Strategy:
     Trades: 310
     P&L: $648.52
     Win Rate: 55.1%

⏰ TIME ANALYSIS:
   Best Hour: 10 ($234.50)
   Worst Hour: 15 ($-89.20)
   Best Day: Tuesday
   Worst Day: Friday
```

## 🎯 Key Features

### Comprehensive Analysis
- **Multi-strategy support**: Analyze long and short strategies separately and combined
- **Advanced metrics**: Beyond basic win rate and profit factor
- **Risk assessment**: Drawdown, Sharpe ratio, and risk of ruin calculations
- **Time optimization**: Identify best trading hours and days

### Professional Visualizations
- **Cumulative P&L charts**: Track performance over time
- **Drawdown analysis**: Visualize risk periods
- **Time-based charts**: Performance by hour and day
- **Distribution analysis**: Understand trade patterns

### Easy to Use
- **Simple data input**: Just paste your ThinkorSwim reports
- **Automatic parsing**: Handles various data formats
- **Clear output**: Easy-to-read reports and charts
- **No coding required**: Ready-to-run script

## 🔍 Troubleshooting

### Common Issues

**"No valid trades found"**
- Check that your data includes the header line with column names
- Ensure each trade has both entry and exit records
- Verify the data format matches the expected structure

**"Could not parse line"**
- Make sure your data uses semicolons (;) as separators
- Check that dates are in MM/DD/YY format
- Verify P&L values are properly formatted

**"Module not found"**
- Install required packages: `pip install -r requirements.txt`
- Ensure you're using Python 3.7 or higher

### Data Format Requirements
- **Separator**: Semicolons (;)
- **Date Format**: MM/DD/YY HH:MM AM/PM
- **Price Format**: $XXX.XX (with dollar sign)
- **P&L Format**: ($XXX.XX) for losses, $XXX.XX for gains

## 📚 Advanced Usage

### Custom Analysis
You can also use the `TradingAnalyzer` class directly:

```python
from trading_analysis import TradingAnalyzer

# Create analyzer
analyzer = TradingAnalyzer()

# Load your data
analyzer.load_data(long_report_text, short_report_text)

# Calculate metrics
metrics = analyzer.calculate_metrics()

# Generate custom reports
analyzer.print_summary_report()
analyzer.plot_cumulative_pnl()
analyzer.save_detailed_report("my_report.txt")
```

### Adding Custom Metrics
The tool is extensible - you can add custom calculations by modifying the `calculate_metrics()` method in `trading_analysis.py`.

## 🤝 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify your data format matches the requirements
3. Ensure all dependencies are installed
4. Check the generated error messages for specific issues

## 📄 License

This tool is provided as-is for educational and analysis purposes. Use at your own risk when making trading decisions.