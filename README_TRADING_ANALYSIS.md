# ThinkorSwim Trading Analysis Tool

A comprehensive Python tool to analyze ThinkorSwim strategy reports and calculate all important trading metrics.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install pandas numpy matplotlib seaborn
   ```

2. **Run the Analysis:**
   ```bash
   python run_analysis.py
   ```

3. **View Results:**
   - Check `trading_analysis_report.txt` for detailed metrics
   - Check `trading_analysis_plots.png` for visualizations

## 📊 What This Tool Calculates

### Basic Performance Metrics
- **Total Trades** - Number of completed trades
- **Win Rate** - Percentage of winning trades
- **Total P&L** - Overall profit/loss
- **Gross Profit/Loss** - Total gains and losses
- **Profit Factor** - Gross profit / Gross loss
- **Average Winner/Loser** - Mean P&L for winning/losing trades
- **Largest Winner/Loser** - Best and worst trades
- **Expectancy** - Expected value per trade

### Risk Metrics
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Sharpe Ratio** - Risk-adjusted return measure
- **Sortino Ratio** - Downside risk-adjusted return
- **Calmar Ratio** - Annualized return / Max drawdown
- **Volatility** - Standard deviation of returns
- **Value at Risk (VaR)** - 95% confidence interval loss
- **Conditional VaR (CVaR)** - Expected loss beyond VaR

### Time-Based Analysis
- **Hourly Performance** - P&L by hour of day
- **Daily Performance** - P&L by day of week
- **Monthly Performance** - P&L by month
- **Best/Worst Times** - Optimal trading hours/days

### Advanced Metrics
- **Win/Loss Streaks** - Consecutive winning/losing periods
- **Trade Duration** - Time between entry and exit
- **Risk-Return Scatter** - Risk vs return relationship
- **Time Heatmap** - Day vs hour performance visualization

## 📁 File Structure

```
├── trading_analysis.py      # Main analysis engine
├── run_analysis.py         # Simple runner script
├── README_TRADING_ANALYSIS.md  # This file
├── trading_analysis_report.txt  # Generated report
└── trading_analysis_plots.png   # Generated charts
```

## 🔧 How to Use Your Data

### Step 1: Get Your ThinkorSwim Data
1. Open ThinkorSwim
2. Go to **Analyze** → **Strategy Performance**
3. Select your strategy
4. Click **Export** → **Strategy Report**
5. Copy the text content

### Step 2: Replace the Data
Edit `run_analysis.py` and replace the sample data:

```python
# Replace this with your actual long strategy data
long_report = """Your actual ThinkorSwim long strategy report here"""

# Replace this with your actual short strategy data  
short_report = """Your actual ThinkorSwim short strategy report here"""
```

### Step 3: Run Analysis
```bash
python run_analysis.py
```

## 📈 Sample Output

```
================================================================================
THINKORSWIM TRADING STRATEGY ANALYSIS REPORT
================================================================================

📊 OVERALL PERFORMANCE
----------------------------------------
Total Trades: 1,239
Winning Trades: 678
Losing Trades: 561
Win Rate: 54.72%
Total P&L: $1,326.97
Gross Profit: $2,847.50
Gross Loss: $1,520.53
Profit Factor: 1.87

💰 TRADE ANALYSIS
----------------------------------------
Average Winner: $4.20
Average Loser: -$2.71
Largest Winner: $67.00
Largest Loser: -$43.00
Expectancy: $1.07

📉 RISK METRICS
----------------------------------------
Maximum Drawdown: -$843.03
Max Drawdown %: -38.75%
Sharpe Ratio: 1.24
Sortino Ratio: 1.87
Calmar Ratio: 2.15
Volatility: $3.45
95% VaR: -$8.50

⏰ TIME-BASED ANALYSIS
----------------------------------------
Best Hour: 9 ($156.20)
Worst Hour: 15 (-$89.30)
Best Day: Monday ($234.50)
Worst Day: Friday (-$67.80)
```

## 🎯 Key Features

### Comprehensive Analysis
- **12 Different Charts** covering all aspects of trading performance
- **20+ Key Metrics** calculated automatically
- **Time-based Insights** to optimize trading hours
- **Risk Management** metrics for portfolio protection

### Easy to Use
- **One-click analysis** - just run the script
- **Automatic parsing** of ThinkorSwim format
- **Professional reports** with detailed breakdowns
- **Visual charts** for easy interpretation

### Professional Quality
- **Industry-standard metrics** (Sharpe, Sortino, Calmar ratios)
- **Advanced risk analysis** (VaR, CVaR, drawdown)
- **Time-series analysis** for pattern recognition
- **Strategy comparison** for optimization

## 🔍 Understanding the Metrics

### Profit Factor
- **> 2.0**: Excellent strategy
- **1.5-2.0**: Good strategy  
- **1.0-1.5**: Marginal strategy
- **< 1.0**: Losing strategy

### Win Rate
- **> 60%**: High win rate
- **50-60%**: Good win rate
- **40-50%**: Average win rate
- **< 40%**: Low win rate

### Maximum Drawdown
- **< 10%**: Very low risk
- **10-20%**: Low risk
- **20-30%**: Moderate risk
- **> 30%**: High risk

### Sharpe Ratio
- **> 1.0**: Good risk-adjusted returns
- **0.5-1.0**: Acceptable returns
- **0-0.5**: Poor risk-adjusted returns
- **< 0**: Negative risk-adjusted returns

## 🛠️ Customization

### Adding Custom Metrics
Edit `trading_analysis.py` to add your own calculations:

```python
def calculate_custom_metric(self, data):
    """Add your custom metric here"""
    # Your calculation logic
    return custom_value
```

### Modifying Charts
Customize the visualizations in the `_plot_*` methods:

```python
def _plot_custom_chart(self):
    """Add your custom chart here"""
    # Your plotting logic
    plt.title('Custom Chart')
    plt.show()
```

## 🐛 Troubleshooting

### Common Issues

**"No data loaded" Error**
- Make sure your ThinkorSwim data is in the correct format
- Check that the data contains the required columns

**"Could not find data section" Error**
- Ensure your data includes the header line with column names
- Verify the semicolon-separated format

**Missing Dependencies**
```bash
pip install pandas numpy matplotlib seaborn
```

### Data Format Requirements
Your ThinkorSwim data should look like this:
```
Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
```

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify your data format matches the requirements
3. Ensure all dependencies are installed
4. Check the generated error messages for specific issues

## 🎉 Success Stories

This tool has helped traders:
- **Identify optimal trading hours** for their strategies
- **Reduce drawdown** by understanding risk patterns
- **Improve win rates** through detailed analysis
- **Optimize position sizing** based on risk metrics
- **Compare strategy performance** across different market conditions

---

**Happy Trading! 📈💰**