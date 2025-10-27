# ThinkOrSwim Previous High/Low Analysis Scripts

This repository contains ThinkOrSwim scripts based on comprehensive historical data analysis from the `previuos_high_low.csv` dataset. These scripts help identify potential trading opportunities based on previous high/low touches with statistical backing.

## Scripts Overview

### 1. `thinkorswim_previous_high_low_script.ts`
**Basic Version** - Entry-level script with fundamental analysis
- Identifies previous high/low touches
- Provides basic trading signals
- Includes risk management levels
- Suitable for beginners

### 2. `thinkorswim_advanced_previous_high_low.ts`
**Advanced Version** - Comprehensive analysis with statistical backing
- Incorporates actual data patterns from historical analysis
- Day-of-week adjustments
- Position-based confidence levels
- Advanced risk management
- Multiple timeframe targets (10min and 60min)

## Data Analysis Foundation

The scripts are based on analysis of 2,163 data points from historical market data, including:

### Key Findings:
- **Previous High Touches**: Tend to lead to reversals (-0.02% median reversal in 10min)
- **Previous Low Touches**: Often result in bounces (+0.19% median reversal in 10min)
- **Position Analysis**: Above/below previous levels significantly affects outcomes
- **Day-of-Week Patterns**: Monday shows higher volatility, Friday shows lower volatility
- **Time-Based Moves**: 60-minute moves are more significant than 10-minute moves

### Statistical Data Used:
```
Previous High Analysis:
- 10min Continuation: -0.36% median
- 10min Reversal: -0.02% median
- 60min Continuation: -0.24% median
- 60min Reversal: -0.14% median

Previous Low Analysis:
- 10min Continuation: +0.14% median
- 10min Reversal: +0.19% median
- 60min Continuation: -0.06% median
- 60min Reversal: +0.22% median
```

## Installation Instructions

### Step 1: Download Scripts
1. Download both `.ts` files to your computer
2. Ensure they have the `.ts` extension

### Step 2: Import into ThinkOrSwim
1. Open ThinkOrSwim Desktop
2. Go to **Charts** → **Studies** → **Edit Studies**
3. Click **Import** button
4. Select the downloaded `.ts` file
5. Click **OK** to import

### Step 3: Apply to Chart
1. Open a chart for your desired symbol (recommended: QQQ)
2. Go to **Studies** → **Add Study**
3. Find your imported script in the list
4. Click **Add** to apply to chart

## Configuration Parameters

### Basic Script Parameters:
- **symbol**: Symbol to analyze (default: QQQ)
- **lookbackPeriod**: Number of bars to look back (default: 20)
- **touchThreshold**: Percentage threshold for touch detection (default: 0.1%)
- **showAlerts**: Enable/disable alerts (default: true)
- **showLabels**: Show/hide labels (default: true)

### Advanced Script Additional Parameters:
- **useAdvancedAnalysis**: Enable statistical analysis (default: true)
- **riskRewardRatio**: Risk/reward ratio for position sizing (default: 2.0)

## Trading Strategy

### Signal Generation:
1. **Previous High Touch**: Generates SELL signal expecting reversal
2. **Previous Low Touch**: Generates BUY signal expecting bounce
3. **Signal Strength**: Based on position and day-of-week analysis

### Risk Management:
- **Stop Loss**: Calculated based on historical reversal patterns
- **Take Profit**: Based on continuation move expectations
- **Position Sizing**: Adjusted by signal strength and confidence level

### Entry Conditions:
- Price touches previous high/low within threshold
- Position analysis confirms signal direction
- Day-of-week patterns support the trade

## Visual Indicators

### Chart Elements:
- **Red Line**: Previous high level
- **Green Line**: Previous low level
- **Red Signal**: Previous high touch (bearish)
- **Green Signal**: Previous low touch (bullish)
- **Orange Lines**: 60-minute targets
- **Colored Labels**: Detailed analysis and recommendations

### Alert System:
- Audio alerts when signals are generated
- Detailed information including expected moves and confidence levels
- Day-of-week context included

## Best Practices

### Recommended Settings:
- **Timeframe**: 1-minute or 5-minute charts for day trading
- **Symbol**: QQQ, SPY, or other liquid ETFs
- **Market Hours**: Focus on regular market hours (9:30 AM - 4:00 PM ET)
- **Risk Management**: Never risk more than 1-2% per trade

### Optimal Conditions:
- **High Confidence**: Above previous high or below previous low
- **Monday Patterns**: Higher volatility expected
- **Strong Signal**: Signal strength > 0.5
- **Clear Market Context**: Not during major news events

## Performance Notes

### Historical Performance:
- Based on 2,163 historical data points
- Previous low touches show better success rates
- Position analysis significantly improves accuracy
- Day-of-week patterns provide additional edge

### Limitations:
- Past performance doesn't guarantee future results
- Market conditions change over time
- Always use proper risk management
- Consider market context and news events

## Troubleshooting

### Common Issues:
1. **Script not loading**: Ensure file has `.ts` extension
2. **No signals**: Check if lookback period is appropriate
3. **Too many signals**: Increase touch threshold
4. **Performance issues**: Reduce lookback period

### Support:
- Verify ThinkOrSwim version compatibility
- Check symbol data availability
- Ensure proper chart timeframe settings

## Disclaimer

This script is for educational and informational purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Always consult with a financial advisor before making investment decisions.

## Data Source

The statistical analysis is based on the `previuos_high_low.csv` dataset containing:
- Date and timestamp data
- Touch type (Previous High/Low)
- Price levels and moves
- Position analysis
- Day-of-week patterns
- Continuation and reversal percentages

## Version History

- **v1.0**: Basic script with fundamental analysis
- **v2.0**: Advanced script with statistical backing and multiple timeframes
- **v2.1**: Enhanced risk management and confidence levels