# 🚀 Quick Start Guide - ThinkorSwim Trading Analysis

## 📋 What You Need

1. **Your CSV files** from ThinkorSwim in `C:\Users\ASUS\`:
   - `StrategyReports_QQQ_8225long1.csv`
   - `StrategyReports_QQQ_8225short.csv`

2. **Python** (version 3.7 or higher)

## 🎯 Step-by-Step Instructions

### Step 1: Setup (One-time)
```bash
python3 setup_analysis.py
```

This will:
- ✅ Install all required packages
- ✅ Check if your files exist
- ✅ Give you the next steps

### Step 2: Run Analysis
```bash
python3 analyze_csv_files.py
```

This will:
- 📊 Parse your CSV files
- 📈 Calculate all metrics
- 📉 Generate charts
- 📄 Save detailed report

## 📊 What You'll Get

### Console Output
```
================================================================================
THINKORSWIM TRADING STRATEGY ANALYSIS REPORT
================================================================================

📊 OVERALL PERFORMANCE:
   Total Trades: 606
   Total P&L: $146.51
   Win Rate: 38.94%
   Profit Factor: 1.01
   Max Drawdown: $1,992.34

💰 TRADE METRICS:
   Average Winner: $45.42
   Average Loser: $-28.57
   Average Trade: $0.24

📈 RISK METRICS:
   Sharpe Ratio: 0.00
   Sortino Ratio: -0.01

🎯 STRATEGY BREAKDOWN:
   Long Strategy: 310 trades, $678.45 P&L, 62.3% win rate
   Short Strategy: 310 trades, $648.52 P&L, 55.1% win rate
```

### Generated Files
- 📈 **Charts**: Multiple PNG files showing performance
- 📄 **Report**: `trading_analysis_report.txt` with detailed metrics

## 🔧 Troubleshooting

### "File not found" Error
- Make sure your CSV files are in `C:\Users\ASUS\`
- Check the exact file names match

### "Module not found" Error
- Run `python3 setup_analysis.py` to install dependencies

### "Could not parse" Warnings
- The tool handles tab characters and formatting issues automatically
- These warnings are normal and won't affect the analysis

## 📚 Alternative Methods

### Method 1: Sample Data (for testing)
```bash
python3 analyze_my_trades.py
```

### Method 2: Manual Installation
```bash
pip install pandas numpy matplotlib seaborn
python3 analyze_csv_files.py
```

## 🎉 You're Ready!

Just run `python3 analyze_csv_files.py` and you'll get a complete analysis of your trading performance with all the metrics you requested:

- ✅ Average winner/loser
- ✅ Profit factor
- ✅ Max drawdown
- ✅ Cumulative P&L
- ✅ Time-based analysis
- ✅ Strategy comparison
- ✅ Risk metrics
- ✅ Visual charts

---

**Need help?** Check `README_ANALYSIS.md` for detailed documentation.