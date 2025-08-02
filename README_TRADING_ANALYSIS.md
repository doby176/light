# ThinkorSwim Trading Analysis Tool

A comprehensive Python tool to analyze ThinkorSwim strategy reports and calculate all important trading metrics.

## 🎯 Features

### 📊 Performance Metrics
- **Average Winner/Loser**: Mean profit/loss per winning/losing trade
- **Profit Factor**: Gross profit divided by gross loss
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Total P&L**: Overall profit/loss

### 📈 Visualizations
- **Cumulative P&L Graph**: Shows equity curve over time
- **Trade Distribution**: Histogram of individual trade P&L
- **Win Rate Comparison**: Bar chart comparing strategies
- **Time-based Analysis**: Performance by hour/day/month
- **Drawdown Analysis**: Risk visualization
- **Strategy Comparison**: Side-by-side metrics

### ⏰ Time Analysis
- **Hourly Performance**: Best/worst trading hours
- **Daily Performance**: Day-of-week analysis
- **Monthly Trends**: Seasonal patterns

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn
```

### 2. Prepare Your Data
Copy your ThinkorSwim strategy reports into the script. The format should be:
```
Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
...
```

### 3. Run Analysis
```bash
python run_analysis.py
```

## 📁 Files

- **`trading_analysis.py`**: Main analysis engine with all metrics and visualizations
- **`run_analysis.py`**: Simple script to run the analysis with your data
- **`README_TRADING_ANALYSIS.md`**: This documentation

## 🔧 How to Use

### Step 1: Get Your ThinkorSwim Data
1. Open ThinkorSwim
2. Go to **Analyze** → **Strategy Performance**
3. Select your strategy
4. Click **Export** → **Strategy Report**
5. Copy the text content

### Step 2: Update the Script
Edit `run_analysis.py` and replace the sample data with your actual reports:

```python
long_strategy_data = """YOUR_LONG_STRATEGY_REPORT_HERE"""
short_strategy_data = """YOUR_SHORT_STRATEGY_REPORT_HERE"""
```

### Step 3: Run the Analysis
```bash
python run_analysis.py
```

## 📊 Output

The script will generate:

1. **Console Report**: Detailed metrics printed to terminal
2. **Visualization File**: `my_trading_analysis.png` with 9 comprehensive charts

### Sample Output
```
================================================================================
THINKORSWIM TRADING STRATEGY ANALYSIS REPORT
================================================================================

📊 OVERALL STATISTICS
Date Range: 2025-06-20 to 2025-08-01
Total Trading Days: 42
Total Trades: 1239

==================================================
LONG STRATEGY ANALYSIS
==================================================
📈 PERFORMANCE METRICS:
   Total Trades: 620
   Winning Trades: 310
   Losing Trades: 310
   Win Rate: 50.00%
   Total P&L: $1,326.97
   Average Winner: $45.20
   Average Loser: -$38.15
   Profit Factor: 1.18
   Max Drawdown: -$1,245.30
   Sharpe Ratio: 0.85

⏰ TIME-BASED ANALYSIS:
   Best Hour: 10:00 ($245.30)
   Worst Hour: 15:00 (-$180.45)
   Best Day: Monday ($320.15)
   Worst Day: Friday (-$95.20)
```

## 🎯 Key Metrics Explained

### Profit Factor
- **> 1.5**: Excellent strategy
- **1.2 - 1.5**: Good strategy  
- **1.0 - 1.2**: Marginal strategy
- **< 1.0**: Losing strategy

### Win Rate
- **> 60%**: High accuracy
- **50-60%**: Good accuracy
- **40-50%**: Average accuracy
- **< 40%**: Low accuracy

### Max Drawdown
- **< 10%**: Low risk
- **10-20%**: Moderate risk
- **20-30%**: High risk
- **> 30%**: Very high risk

## 🔍 Advanced Analysis

### Time-based Insights
- **Best Trading Hours**: Focus your manual trading during profitable hours
- **Day-of-Week Patterns**: Identify market behavior patterns
- **Monthly Trends**: Seasonal strategy adjustments

### Risk Management
- **Drawdown Analysis**: Understand maximum risk exposure
- **Trade Distribution**: Identify outlier trades
- **Sharpe Ratio**: Risk-adjusted performance

## 🛠️ Customization

### Adding New Metrics
Edit `trading_analysis.py` and add new calculations to the `calculate_basic_metrics` method.

### Custom Visualizations
Modify the `generate_visualizations` method to add new charts or modify existing ones.

### Data Format Support
The parser supports ThinkorSwim's standard export format. For other formats, modify the `parse_thinkorswim_report` method.

## 📈 Example Results

Based on your sample data:
- **Long Strategy**: $1,326.97 profit (620 trades)
- **Short Strategy**: -$843.03 loss (619 trades)
- **Combined**: $483.94 net profit

## 🎉 Benefits

1. **Comprehensive Analysis**: All major trading metrics in one place
2. **Visual Insights**: Easy-to-understand charts and graphs
3. **Time Analysis**: Identify optimal trading windows
4. **Risk Assessment**: Understand drawdown and volatility
5. **Strategy Comparison**: Compare long vs short performance
6. **Professional Reports**: Ready-to-use analysis for presentations

## 🚨 Important Notes

- **Data Quality**: Ensure your ThinkorSwim export is complete and accurate
- **Time Zones**: All times are processed as shown in the export
- **P&L Format**: The script handles both positive and negative P&L values
- **Missing Data**: Incomplete trades are automatically filtered out

## 💡 Tips for Best Results

1. **Use Complete Data**: Export full strategy history for accurate analysis
2. **Check Data Format**: Ensure the export format matches the expected structure
3. **Review Outliers**: Large winning/losing trades may indicate data issues
4. **Compare Strategies**: Use both long and short data for complete picture
5. **Save Results**: The visualization file can be used for reports/presentations

## 🔧 Troubleshooting

### Common Issues

**"Could not find data section"**
- Check that your export includes the header line with column names
- Ensure the format matches the expected ThinkorSwim export

**"No completed trades found"**
- Verify that P&L values are properly formatted
- Check for empty or invalid trade data

**Visualization errors**
- Install required packages: `pip install matplotlib seaborn`
- Ensure you have write permissions in the current directory

### Getting Help

If you encounter issues:
1. Check the data format matches the example
2. Verify all required packages are installed
3. Review the error message for specific details
4. Ensure your ThinkorSwim export is complete

---

**Happy Trading Analysis! 📊📈**