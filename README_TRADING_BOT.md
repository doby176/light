# 🐂 Bullish Order Block Trading Bot

A Python-based automated trading bot that implements the Bullish Order Block strategy with automatic long/short cycling for QQQ shares.

## 📋 Overview

This trading bot converts your ThinkorSwim Bullish Order Block indicator into a fully automated trading system that:

- **Detects Bullish Order Blocks** on 1-minute charts
- **Automatically cycles** between long and short positions
- **Implements risk management** with position sizing and stop losses
- **Provides comprehensive backtesting** capabilities
- **Offers live trading simulation** (paper trading)

## 🔄 Trading Strategy

### Signal Detection
- **Green Dot**: Bullish Order Block detected (enter LONG)
- **Red Dot**: Price closes below bullish order block level (exit LONG, enter SHORT)

### Trading Cycle
1. **Enter LONG** when green dot appears
2. **Exit LONG and enter SHORT** when red dot appears  
3. **Exit SHORT and enter LONG** when price hits green dot level (stop loss)
4. **Repeat cycle** indefinitely

### Risk Management
- Position sizing based on capital percentage
- Stop losses at order block levels
- Automatic position cycling
- Daily/weekly loss limits

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Bot

```bash
python run_bot.py
```

### 3. Choose Your Mode

The bot offers two main modes:

#### 📊 Backtest Mode
- Test the strategy on historical data
- Analyze performance metrics
- Optimize parameters

#### ⚡ Live Trading Mode (Simulation)
- Real-time trading simulation
- Paper trading with no real money at risk
- Monitor live performance

## 📁 File Structure

```
├── trading_bot.py          # Main trading bot implementation
├── trading_config.py       # Configuration settings
├── run_bot.py             # User-friendly launcher
├── requirements.txt       # Python dependencies
└── README_TRADING_BOT.md  # This file
```

## ⚙️ Configuration

### Basic Settings (`trading_config.py`)

```python
class TradingConfig:
    SYMBOL = "QQQ"                    # Trading symbol
    TIMEFRAME = "1m"                  # Data timeframe
    INITIAL_CAPITAL = 10000.0         # Starting capital
    POSITION_SIZE = 0.1               # Risk per trade (10%)
    ENABLE_SHORTING = True            # Enable short positions
    AUTO_CYCLE = True                 # Enable automatic cycling
```

### Strategy Parameters

```python
class BullishOrderBlockConfig:
    INEFFICIENCY_MULTIPLIER = 1.5     # Shadow gap multiplier
    LOOKBACK_PERIODS = 3              # BOS/CHOCH lookback
    MAX_DAILY_LOSS = 0.05             # Max daily loss (5%)
    MAX_WEEKLY_LOSS = 0.15            # Max weekly loss (15%)
```

## 📊 Performance Metrics

The bot tracks comprehensive performance metrics:

- **Total P&L**: Overall profit/loss
- **Win Rate**: Percentage of winning trades
- **Total Trades**: Number of completed trades
- **Average Win/Loss**: Average profit/loss per trade
- **Profit Factor**: Ratio of gross profit to gross loss
- **Maximum Drawdown**: Largest peak-to-trough decline

## 🔍 Strategy Logic

### Bullish Order Block Detection

```python
# Inefficiency: Shadow gap > 1.5x candle body
inefficiency = abs(high1[1] - low1) > abs(close1[1] - open1[1]) * 1.5

# Bullish Break of Structure (BOS) and Change of Character (CHOCH)
bos_up = high1 > Highest(high1[2], 3)
choch_up = low1 < Lowest(low1[2], 3) and high1 > Highest(high1[2], 3)

# Bullish Order Block
is_bullish_order_block = inefficiency[1] and (bos_up or choch_up)
```

### Trading Rules

1. **Long Entry**: When bullish order block is detected
2. **Long Exit/Short Entry**: When price closes below order block level
3. **Short Exit/Long Entry**: When price hits order block level (stop loss)

## 🛡️ Risk Management

### Position Sizing
- Risk-based position sizing
- Maximum position size limits
- Dynamic position adjustment based on volatility

### Stop Losses
- Automatic stop loss placement
- Trailing stop functionality
- Order block level stops

### Loss Limits
- Daily loss limits (5% default)
- Weekly loss limits (15% default)
- Maximum consecutive losses

## 📈 Usage Examples

### Basic Backtest

```python
from trading_bot import BullishOrderBlockBot

# Initialize bot
bot = BullishOrderBlockBot(
    symbol="QQQ",
    initial_capital=10000.0,
    position_size=0.1
)

# Run backtest
bot.run_backtest("2024-01-01", "2024-12-31")
```

### Live Trading Simulation

```python
# Run live trading (simulation)
bot.run_live(update_interval=60)  # Update every 60 seconds
```

### Custom Configuration

```python
# Custom bot with different parameters
bot = BullishOrderBlockBot(
    symbol="SPY",           # Different symbol
    initial_capital=50000,  # More capital
    position_size=0.05      # Smaller position size
)
```

## 🔧 Advanced Features

### Data Sources
- **Yahoo Finance**: Free real-time and historical data
- **Extensible**: Easy to add other data sources (Alpaca, Interactive Brokers, etc.)

### Notifications
- Email alerts for trade signals
- Discord/Telegram integration
- Daily performance summaries

### Logging
- Comprehensive trade logging
- Performance tracking
- Error handling and recovery

## ⚠️ Important Notes

### Disclaimer
- This is for educational and research purposes
- Past performance does not guarantee future results
- Always test thoroughly before using real money
- Consider consulting with a financial advisor

### Limitations
- Current version uses Yahoo Finance data (may have delays)
- Paper trading only (no real broker integration)
- 1-minute timeframe optimized for QQQ

### Future Enhancements
- Real broker integration (Alpaca, Interactive Brokers)
- Additional technical indicators
- Machine learning optimization
- Multi-timeframe analysis

## 🐛 Troubleshooting

### Common Issues

1. **No data received**
   - Check internet connection
   - Verify symbol is valid
   - Try different date ranges

2. **Import errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Performance issues**
   - Reduce update frequency
   - Use shorter backtest periods
   - Check system resources

### Log Files
- Check `trading_bot.log` for detailed error messages
- Review trade history in console output

## 📞 Support

For questions or issues:
1. Check the log files for error details
2. Review the configuration settings
3. Test with different parameters
4. Consider running in backtest mode first

## 📚 Additional Resources

- **ThinkorSwim Platform**: Original indicator development
- **Order Block Theory**: Understanding market structure
- **Risk Management**: Position sizing and stop losses
- **Python Trading**: Advanced bot development

---

**Happy Trading! 🚀**

*Remember: The best trading strategy is the one you understand and can execute consistently.*