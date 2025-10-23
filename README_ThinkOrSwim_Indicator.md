# QQQ Gap Analysis Indicator for ThinkOrSwim

## Overview

This ThinkOrSwim indicator provides real-time gap analysis for QQQ (Nasdaq ETF) based on historical data from 1MChart. The indicator analyzes current gap conditions and provides:

- **Gap Fill Probability**: Real-time probability of gap filling based on 1929 historical records
- **Price Targets**: Entry, exit, and stop-loss levels based on historical patterns
- **Risk/Reward Ratios**: Calculated risk-reward ratios for trade planning
- **Visual Alerts**: Color-coded signals and audio alerts for high-probability setups

## Features

### 📊 Real Historical Data
- Based on 1,929 QQQ gap records from 2015-2024
- Analyzes gaps by size, day of week, and direction
- Provides statistically significant probabilities

### 🎯 Price Targets
- **Entry Price**: Current open price
- **Target Price**: Based on median moves before gap fill
- **Stop Loss**: Based on median max moves for unfilled gaps

### 📈 Gap Size Bins
- **Bin 1**: 0.15-0.35% gaps
- **Bin 2**: 0.35-0.5% gaps  
- **Bin 3**: 0.5-1% gaps
- **Bin 4**: 1-1.5% gaps
- **Bin 5**: 1.5%+ gaps

### 🎨 Visual Indicators
- Color-coded probability levels (Green >60%, Yellow 50-60%, Red <50%)
- Horizontal price target lines
- Real-time labels with key metrics

## Installation

### Step 1: Download the Indicator
1. Copy the contents of `QQQ_Gap_Analysis_Indicator.ts`
2. Open ThinkOrSwim Desktop
3. Go to **Charts** → **Studies** → **Edit Studies**

### Step 2: Create New Study
1. Click **Create** → **ThinkScript Editor**
2. Paste the indicator code
3. Name it "QQQ Gap Analysis Indicator"
4. Click **OK**

### Step 3: Apply to Chart
1. Open a QQQ chart
2. Go to **Studies** → **Add Study**
3. Select "QQQ Gap Analysis Indicator"
4. Click **OK**

## Usage

### Basic Setup
1. **Apply to QQQ chart** (1-minute or higher timeframe recommended)
2. **Enable price targets** by setting `showPriceTargets = yes`
3. **Enable probability display** by setting `showProbability = yes`

### Reading the Indicator

#### Lower Panel
- **Gap Fill Probability Line**: Shows real-time probability of gap filling
- **Color Coding**: 
  - 🟢 Green: >60% probability (high confidence)
  - 🟡 Yellow: 50-60% probability (moderate confidence)
  - 🔴 Red: <50% probability (low confidence)

#### Main Chart
- **White Line**: Entry price (current open)
- **Green Line**: Target price (based on historical patterns)
- **Red Line**: Stop loss (based on unfilled gap moves)

#### Labels
- **Gap Direction**: Shows gap size and direction (UP/DOWN)
- **Fill Probability**: Current probability percentage
- **Price Targets**: Entry, target, and stop prices
- **Risk/Reward**: Calculated R/R ratio

### Trading Signals

#### High Probability Setups (>70%)
- **Gap Up with >70% fill rate**: Consider shorting at resistance
- **Gap Down with >70% fill rate**: Consider buying at support
- Audio alerts will trigger for these setups

#### Low Probability Setups (<30%)
- **Gap Up with <30% fill rate**: Consider going long (gap may not fill)
- **Gap Down with <30% fill rate**: Consider shorting (gap may not fill)

#### Moderate Probability (30-70%)
- Use additional technical analysis
- Consider smaller position sizes
- Monitor for breakouts/breakdowns

## Data Analysis Insights

### Key Findings from Historical Data

#### Small Gaps (0.15-0.35%)
- **Highest fill rates**: 70-82% across most days
- **Best days**: Thursday gap downs (80%), Friday gap downs (81%)
- **Quick fills**: Often fill within first 30 minutes

#### Medium Gaps (0.35-0.5%)
- **Moderate fill rates**: 48-70%
- **Best setups**: Tuesday gap ups (70.5%), Wednesday gap ups (69.2%)
- **Good risk/reward**: Balanced probability and move size

#### Large Gaps (0.5-1%)
- **Lower fill rates**: 38-65%
- **Best opportunities**: Thursday gap downs (65.2%)
- **Higher volatility**: Larger moves when gaps don't fill

#### Very Large Gaps (1%+)
- **Lowest fill rates**: 10-35%
- **High risk**: Large adverse moves when gaps don't fill
- **Best for**: Fade trades (betting against gap fill)

### Day of Week Patterns
- **Monday**: Generally lower fill rates, especially for large gaps
- **Tuesday**: Good for medium gap ups
- **Wednesday**: Mixed results, moderate fill rates
- **Thursday**: Best day for gap downs across all sizes
- **Friday**: Good for small gap downs, poor for large gaps

## Risk Management

### Position Sizing
- **High probability (>70%)**: Normal position size
- **Moderate probability (50-70%)**: 50-75% position size
- **Low probability (<50%)**: 25-50% position size

### Stop Losses
- Use the red stop loss line as initial stop
- Consider tightening stops on high-probability setups
- Monitor for gap expansion beyond historical norms

### Time Management
- **Small gaps**: Often fill within first 30-60 minutes
- **Medium gaps**: May take 1-2 hours to fill
- **Large gaps**: Can take several hours or not fill at all

## Customization

### Input Parameters
```thinkorscript
input showLabels = yes;        // Show/hide labels
input showPriceTargets = yes;  // Show/hide price lines
input showProbability = yes;   // Show/hide probability
```

### Alert Settings
The indicator includes built-in alerts for:
- High probability gap fills (>70%)
- Low probability setups (<30%)
- Customizable alert sounds and conditions

## Technical Notes

### Data Source
- **Period**: 2015-2024
- **Records**: 1,929 QQQ gap observations
- **Methodology**: 1-minute candlestick analysis
- **Gap Definition**: Open vs Previous Close

### Calculations
- **Fill Rate**: Percentage of gaps that close during the day
- **Median Move**: 50th percentile of moves before gap fill
- **Max Move**: 50th percentile of maximum moves for unfilled gaps
- **Risk/Reward**: (Target - Entry) / (Entry - Stop)

### Limitations
- Historical data may not predict future performance
- Market conditions change over time
- Use as part of comprehensive trading strategy
- Always use proper risk management

## Support

For questions or issues:
1. Check ThinkOrSwim's ThinkScript documentation
2. Verify QQQ symbol is loaded correctly
3. Ensure sufficient historical data is available
4. Test on paper trading first

## Disclaimer

This indicator is for educational and informational purposes only. Past performance does not guarantee future results. Always use proper risk management and consider consulting with a financial advisor before making trading decisions.

---

**Data Source**: 1MChart Historical Gap Analysis Database (1929 records, 2015-2024)
**Last Updated**: December 2024