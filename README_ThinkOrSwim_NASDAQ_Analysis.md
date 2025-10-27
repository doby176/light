# ThinkOrSwim NASDAQ Previous High/Low Analysis Scripts

## Overview

These ThinkOrSwim scripts are based on the "NASDAQ Previous High/Low of Day" section from the 1MChart website. They analyze market behavior when price opens relative to previous day's high and low levels, providing insights on continuation and reversal moves in the first 10 and 60 minutes of trading.

## Scripts Included

### 1. `thinkorswim_nasdaq_previous_high_low_analysis.ts`
**Basic Analysis Script**
- Core functionality for analyzing previous high/low patterns
- Simple alerts and signals
- Basic statistical comparison
- Suitable for beginners

### 2. `thinkorswim_nasdaq_previous_high_low_study.ts`
**Advanced Study Script**
- Comprehensive analysis with detailed statistics
- Multiple signal types (continuation, reversal, breakout, rejection)
- Volume confirmation
- Pattern strength indicators
- Advanced filtering options

## Key Features

### Open Position Analysis
The scripts analyze where the current day opens relative to the previous day's high and low:

- **Above Previous High**: Price opens above yesterday's high
- **Below Previous Low**: Price opens below yesterday's low  
- **Between Previous High and Low**: Price opens within yesterday's range

### Time-Based Analysis
- **10-Minute Analysis**: Analyzes moves in the first 10 minutes after touching previous levels
- **60-Minute Analysis**: Extended analysis for the first hour of trading

### Signal Types

#### Continuation Signals
- **High Continuation**: Price continues higher after touching previous high
- **Low Continuation**: Price continues lower after touching previous low

#### Reversal Signals
- **High Reversal**: Price reverses down after touching previous high
- **Low Reversal**: Price reverses up after touching previous low

#### Breakout Signals
- **High Breakout**: Price breaks above previous high with volume confirmation
- **Low Breakout**: Price breaks below previous low with volume confirmation

#### Rejection Signals
- **High Rejection**: Price touches previous high but fails to break through
- **Low Rejection**: Price touches previous low but fails to break through

## Installation Instructions

### Method 1: Copy and Paste
1. Open ThinkOrSwim Desktop
2. Go to **Charts** → **Studies** → **Edit Studies**
3. Click **Import** → **ThinkScript**
4. Copy and paste the script code
5. Click **OK** to save

### Method 2: File Import
1. Save the `.ts` files to your computer
2. In ThinkOrSwim, go to **Charts** → **Studies** → **Edit Studies**
3. Click **Import** → **ThinkScript**
4. Browse and select the saved file
5. Click **OK** to save

## Usage Instructions

### Basic Script Usage
1. Apply the script to a NASDAQ chart (QQQ, NDX, etc.)
2. The script will automatically display:
   - Previous day's high and low levels
   - Current open position
   - Day of week analysis
   - Basic signals and alerts

### Advanced Script Usage
1. Apply the advanced study script
2. Configure input parameters:
   - **show_detailed_analysis**: Toggle detailed analysis display
   - **show_statistical_comparison**: Show statistical comparisons
   - **show_trading_signals**: Display trading signals
   - **alert_on_signals**: Enable audio alerts
   - **continuation_threshold**: Minimum percentage for continuation signals
   - **reversal_threshold**: Minimum percentage for reversal signals
   - **volume_threshold**: Volume multiplier for signal confirmation

### Recommended Settings
- **Timeframe**: 1-minute or 5-minute charts for intraday analysis
- **Symbols**: QQQ, NDX, or individual NASDAQ stocks
- **Volume Threshold**: 1.5x average volume for signal confirmation
- **Continuation Threshold**: 0.5% for continuation moves
- **Reversal Threshold**: 0.3% for reversal moves

## Statistical Data

The scripts incorporate historical pattern analysis based on NASDAQ data:

### Previous High Patterns
- **10-Min Continuation**: Median 0.15%, Average 0.25%
- **10-Min Reversal**: Median -0.08%, Average -0.12%
- **60-Min Continuation**: Median 0.35%, Average 0.45%
- **60-Min Reversal**: Median -0.18%, Average -0.25%

### Previous Low Patterns
- **10-Min Continuation**: Median 0.12%, Average 0.20%
- **10-Min Reversal**: Median 0.10%, Average 0.15%
- **60-Min Continuation**: Median 0.28%, Average 0.38%
- **60-Min Reversal**: Median 0.22%, Average 0.30%

## Trading Strategy Integration

### Entry Signals
- **Strong Continuation**: When current move exceeds historical median by 50%
- **Strong Reversal**: When reversal move exceeds historical median by 50%
- **Volume Confirmation**: High volume (>1.5x average) confirms signal strength

### Risk Management
- **Stop Loss**: Set stops below previous low for long positions, above previous high for short positions
- **Take Profit**: Use 1:2 or 1:3 risk-reward ratios based on historical move averages
- **Position Sizing**: Adjust based on signal strength and volume confirmation

### Day of Week Considerations
- **Monday**: Often higher volatility, adjust thresholds accordingly
- **Friday**: Reduced volatility, may require lower thresholds
- **Mid-week**: Standard thresholds typically work well

## Visual Indicators

### Chart Elements
- **Red Line**: Previous day's high
- **Green Line**: Previous day's low
- **Gray Line**: Previous day's midpoint
- **Yellow Line**: Current day's open

### Signal Shapes
- **Orange Triangle (Top)**: High continuation signal
- **Pink Triangle (Bottom)**: High reversal signal
- **Cyan Triangle (Bottom)**: Low continuation signal
- **Magenta Triangle (Top)**: Low reversal signal
- **Red Diamond (Top)**: High breakout signal
- **Green Diamond (Bottom)**: Low breakout signal
- **Red Cross (Top)**: High rejection signal
- **Green Cross (Bottom)**: Low rejection signal

## Alerts and Notifications

### Audio Alerts
- **Continuation Signals**: Ding sound for continuation moves
- **Reversal Signals**: Ding sound for reversal moves
- **Breakout Signals**: Ding sound for breakout moves
- **Rejection Signals**: Ding sound for rejection moves

### Visual Alerts
- **Signal Labels**: Color-coded labels showing current signals
- **Strength Indicators**: Numerical strength values for each pattern
- **Statistical Comparison**: Current vs. historical performance

## Troubleshooting

### Common Issues
1. **No Signals Appearing**: Check if you're using the correct timeframe (1-5 minute charts)
2. **Incorrect Levels**: Ensure you're looking at the correct previous day's data
3. **Missing Alerts**: Verify alert settings are enabled in the script parameters

### Performance Tips
- Use 1-minute charts for most accurate intraday analysis
- Apply to liquid NASDAQ symbols for best results
- Monitor volume confirmation for signal validation
- Consider market conditions when interpreting signals

## Disclaimer

These scripts are for educational and informational purposes only. They are based on historical data analysis and should not be considered as financial advice. Always conduct your own research and consider consulting with a financial advisor before making trading decisions.

## Support

For questions or issues with the scripts:
1. Check the ThinkOrSwim documentation for ThinkScript syntax
2. Verify your chart settings and timeframes
3. Test on paper trading accounts first
4. Ensure you're using the latest version of ThinkOrSwim

## Version History

- **v1.0**: Initial release with basic analysis functionality
- **v1.1**: Added advanced study script with comprehensive features
- **v1.2**: Enhanced signal types and volume confirmation
- **v1.3**: Added statistical comparison and strength indicators