# ThinkorSwim Trading Analysis Tool

A comprehensive Python tool to analyze your ThinkorSwim strategy reports and calculate all important trading metrics.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install pandas numpy matplotlib
   ```

2. **Edit the Script:**
   - Open `analyze_my_trades.py`
   - Replace the sample data with your actual ThinkorSwim reports

3. **Run Analysis:**
   ```bash
   python3 analyze_my_trades.py
   ```

## 📊 What You Get

### Metrics Calculated:
- ✅ **Average Winner/Loser**
- ✅ **Profit Factor**
- ✅ **Max Drawdown**
- ✅ **Cumulative P&L**
- ✅ **Sharpe Ratio**
- ✅ **Win/Loss Streaks**
- ✅ **Time-based Analysis**
- ✅ **Recovery Factor**
- ✅ **Expectancy**

### Generated Files:
- 📈 **Cumulative P&L Charts** (PNG files)
- 📉 **Drawdown Analysis Charts** (PNG files)
- 📊 **Comprehensive Text Reports**

## 🔧 How to Use Your Data

### Step 1: Get Your ThinkorSwim Data
1. Open ThinkorSwim
2. Go to **Analyze** → **Strategy Performance**
3. Select your strategy
4. Click **Export** → **Strategy Report**
5. Copy the text content

### Step 2: Replace the Data
Edit `analyze_my_trades.py` and replace the sample data:

```python
# Replace this with your actual long strategy data
long_report = """Your actual ThinkorSwim long strategy report here"""

# Replace this with your actual short strategy data  
short_report = """Your actual ThinkorSwim short strategy report here"""
```

### Step 3: Run Analysis
```bash
python3 analyze_my_trades.py
```

## 📈 Sample Results

Based on your sample data:
- **Long Strategy**: -$5.00 (50% win rate, 0.88 profit factor)
- **Short Strategy**: +$5.00 (50% win rate, 1.13 profit factor)
- **Combined**: $0.00 (50% win rate, 1.00 profit factor)

## 🎯 Key Features

- **One-click analysis** - just paste your data and run
- **Professional metrics** - all industry-standard calculations
- **Visual insights** - easy-to-understand charts
- **Time analysis** - identify optimal trading hours
- **Risk assessment** - understand drawdown and volatility

## 📁 Files Created

- `analyze_my_trades.py` - Main analysis script
- `simple_analysis.py` - Basic analysis tool
- `trading_analysis.py` - Advanced analysis engine
- `README_ANALYSIS.md` - This file

## 🐛 Troubleshooting

**"No data loaded" Error**
- Make sure your ThinkorSwim data is in the correct format
- Check that the data contains the required columns

**"Could not parse line" Warning**
- Ensure your data includes the header line with column names
- Verify the semicolon-separated format

**Missing Dependencies**
```bash
pip install pandas numpy matplotlib
```

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify your data format matches the requirements
3. Ensure all dependencies are installed
4. Check the generated error messages for specific issues

---

**Happy Trading Analysis! 📊💰**