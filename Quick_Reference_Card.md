# ThinkOrSwim Previous High/Low Scripts - Quick Reference

## 🚀 Quick Start
1. **Download** the `.ts` files
2. **Import** into ThinkOrSwim: Charts → Studies → Edit Studies → Import
3. **Apply** to chart: Studies → Add Study → Select script → Add
4. **Configure** parameters as needed

## 📊 Script Comparison

| Feature | Basic Script | Advanced Script |
|---------|-------------|-----------------|
| **Complexity** | Beginner | Advanced |
| **Data Analysis** | Basic | Statistical |
| **Day Patterns** | No | Yes |
| **Position Analysis** | Basic | Advanced |
| **Multiple Timeframes** | No | Yes (10min + 60min) |
| **Confidence Levels** | No | Yes |
| **Risk Management** | Basic | Advanced |

## 🎯 Trading Signals

### Previous High Touch (Bearish)
- **Signal**: SELL
- **Expectation**: Reversal down
- **10min Target**: -0.02% (median)
- **60min Target**: -0.14% (median)
- **Best Conditions**: Above previous high, Monday

### Previous Low Touch (Bullish)
- **Signal**: BUY
- **Expectation**: Bounce up
- **10min Target**: +0.19% (median)
- **60min Target**: +0.22% (median)
- **Best Conditions**: Below previous low, Monday

## ⚙️ Key Parameters

### Basic Script
```typescript
input lookbackPeriod = 20;      // Bars to analyze
input touchThreshold = 0.1;     // Touch detection %
input showAlerts = true;        // Enable alerts
input showLabels = true;        // Show labels
```

### Advanced Script
```typescript
input lookbackPeriod = 20;      // Bars to analyze
input touchThreshold = 0.1;     // Touch detection %
input useAdvancedAnalysis = true; // Statistical analysis
input riskRewardRatio = 2.0;    // Risk/reward ratio
```

## 📈 Visual Indicators

### Chart Elements
- **🔴 Red Line**: Previous high level
- **🟢 Green Line**: Previous low level
- **🔴 Red Signal**: High touch (SELL)
- **🟢 Green Signal**: Low touch (BUY)
- **🟠 Orange Lines**: 60-minute targets
- **📝 Labels**: Analysis & recommendations

### Alert Messages
- **High Touch**: "Previous High Touch - Expecting Reversal"
- **Low Touch**: "Previous Low Touch - Expecting Bounce"
- **Includes**: Day of week, expected move, confidence level

## 📊 Statistical Data (Based on 2,163 samples)

### Previous High Analysis
| Timeframe | Continuation | Reversal |
|-----------|-------------|----------|
| 10min | -0.36% | -0.02% |
| 60min | -0.24% | -0.14% |

### Previous Low Analysis
| Timeframe | Continuation | Reversal |
|-----------|-------------|----------|
| 10min | +0.14% | +0.19% |
| 60min | -0.06% | +0.22% |

## 🎯 Best Practices

### Optimal Settings
- **Timeframe**: 1min or 5min charts
- **Symbol**: QQQ, SPY, liquid ETFs
- **Hours**: 9:30 AM - 4:00 PM ET
- **Risk**: 1-2% per trade max

### High Confidence Conditions
- ✅ Above previous high (for high touches)
- ✅ Below previous low (for low touches)
- ✅ Monday trading (higher volatility)
- ✅ Strong signal strength (>0.5)
- ✅ Clear market context

### Avoid
- ❌ Major news events
- ❌ Low liquidity periods
- ❌ Weak signal strength
- ❌ Unclear market context

## 🔧 Troubleshooting

### Common Issues
| Problem | Solution |
|---------|----------|
| No signals | Reduce lookback period |
| Too many signals | Increase touch threshold |
| Script not loading | Check .ts extension |
| Performance issues | Reduce lookback period |

### Support
- Verify ThinkOrSwim version
- Check symbol data availability
- Ensure proper chart settings
- Test on paper trading first

## ⚠️ Risk Disclaimer

- **Educational use only**
- **Past performance ≠ future results**
- **Always use proper risk management**
- **Consult financial advisor**
- **Test on paper trading first**

## 📞 Quick Commands

### ThinkOrSwim Navigation
- **Import Script**: Charts → Studies → Edit Studies → Import
- **Add to Chart**: Studies → Add Study → Select → Add
- **Edit Parameters**: Double-click study on chart
- **Remove Study**: Right-click study → Remove

### Recommended Symbols
- **QQQ** (NASDAQ-100 ETF)
- **SPY** (S&P 500 ETF)
- **IWM** (Russell 2000 ETF)
- **DIA** (Dow Jones ETF)

---

**📚 For detailed instructions, see README_ThinkOrSwim_Scripts.md**
**🔧 For setup help, run: `python setup_thinkorswim.py`**