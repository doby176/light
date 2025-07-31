# ThinkOrSwim Previous High/Low Analysis Script
# Based on historical data analysis for trading insights
# This script helps identify potential trading opportunities based on previous high/low touches

declare lower;

# Input parameters
input symbol = "QQQ";  # Symbol to analyze
input lookbackPeriod = 20;  # Number of bars to look back for previous high/low
input touchThreshold = 0.1;  # Percentage threshold for considering a touch
input showAlerts = true;  # Show alerts when conditions are met
input showLabels = true;  # Show labels on chart

# Variables to store previous high/low levels
def prevHigh = 0.0;
def prevLow = 0.0;
def highTouchTime = 0;
def lowTouchTime = 0;

# Calculate previous high and low
if BarNumber() > lookbackPeriod {
    prevHigh = Highest(high[1], lookbackPeriod);
    prevLow = Lowest(low[1], lookbackPeriod);
    
    # Check for touches
    def highTouch = abs(high - prevHigh) / prevHigh * 100 <= touchThreshold;
    def lowTouch = abs(low - prevLow) / prevLow * 100 <= touchThreshold;
    
    # Store touch times
    if highTouch {
        highTouchTime = BarNumber();
    }
    if lowTouch {
        lowTouchTime = BarNumber();
    }
}

# Calculate position relative to previous high/low
def positionAboveHigh = close > prevHigh;
def positionBelowLow = close < prevLow;
def positionBetween = close >= prevLow && close <= prevHigh;

# Determine open position category
def openPosition;
if positionAboveHigh {
    openPosition = "Above Previous High";
} else if positionBelowLow {
    openPosition = "Below Previous Low";
} else {
    openPosition = "Between Previous High and Low";
}

# Calculate day of week
def dayOfWeek = GetDayOfWeek(GetYYYYMMDD());

# Trading signals based on historical analysis
def highTouchSignal = 0;
def lowTouchSignal = 0;

# Previous High Touch Analysis
if abs(high - prevHigh) / prevHigh * 100 <= touchThreshold {
    # Based on historical data analysis:
    # - Previous high touches often lead to reversals
    # - Continuation moves are less common
    # - 60-minute moves tend to be more significant than 10-minute moves
    
    highTouchSignal = -1;  # Bearish signal (expecting reversal)
}

# Previous Low Touch Analysis
if abs(low - prevLow) / prevLow * 100 <= touchThreshold {
    # Based on historical data analysis:
    # - Previous low touches often lead to bounces
    # - Reversal moves are common
    # - Position relative to previous levels matters
    
    lowTouchSignal = 1;  # Bullish signal (expecting bounce)
}

# Calculate expected move percentages based on historical data
def expectedHighReversal = -0.5;  # Based on median reversal move from data
def expectedHighContinuation = 0.1;  # Based on median continuation move from data
def expectedLowReversal = 0.4;  # Based on median reversal move from data
def expectedLowContinuation = -0.2;  # Based on median continuation move from data

# Risk management levels
def highTouchStopLoss = prevHigh * (1 + expectedHighReversal / 100);
def highTouchTakeProfit = prevHigh * (1 + expectedHighContinuation / 100);
def lowTouchStopLoss = prevLow * (1 - expectedLowReversal / 100);
def lowTouchTakeProfit = prevLow * (1 - expectedLowContinuation / 100);

# Plot signals
plot(highTouchSignal, "Previous High Touch", Color.RED, 2);
plot(lowTouchSignal, "Previous Low Touch", Color.GREEN, 2);

# Plot previous high/low levels
plot(prevHigh, "Previous High", Color.RED, 1);
plot(prevLow, "Previous Low", Color.GREEN, 1);

# Plot risk management levels
plot(highTouchStopLoss, "High Touch Stop Loss", Color.DARK_RED, 1, PlotStyle.LINE);
plot(highTouchTakeProfit, "High Touch Take Profit", Color.DARK_GREEN, 1, PlotStyle.LINE);
plot(lowTouchStopLoss, "Low Touch Stop Loss", Color.DARK_RED, 1, PlotStyle.LINE);
plot(lowTouchTakeProfit, "Low Touch Take Profit", Color.DARK_GREEN, 1, PlotStyle.LINE);

# Alerts
if showAlerts {
    if highTouchSignal != 0 {
        Alert("Previous High Touch Detected - Expecting Reversal", Alert.BAR, Sound.DING);
    }
    if lowTouchSignal != 0 {
        Alert("Previous Low Touch Detected - Expecting Bounce", Alert.BAR, Sound.DING);
    }
}

# Labels
if showLabels {
    if highTouchSignal != 0 {
        AddLabel(yes, "HIGH TOUCH\nExpected Reversal: " + AsPercent(expectedHighReversal / 100), Color.RED);
    }
    if lowTouchSignal != 0 {
        AddLabel(yes, "LOW TOUCH\nExpected Bounce: " + AsPercent(expectedLowReversal / 100), Color.GREEN);
    }
}

# Additional analysis based on position
def positionAnalysis = "";
if positionAboveHigh {
    positionAnalysis = "Above Previous High - Higher probability of reversal";
} else if positionBelowLow {
    positionAnalysis = "Below Previous Low - Higher probability of bounce";
} else {
    positionAnalysis = "Between Levels - Mixed signals";
}

# Day of week analysis
def dayAnalysis = "";
if dayOfWeek == 1 {  # Monday
    dayAnalysis = "Monday - Higher volatility expected";
} else if dayOfWeek == 5 {  # Friday
    dayAnalysis = "Friday - Weekend positioning may affect moves";
}

# Output summary
plot(0, "Position: " + openPosition, Color.WHITE);
plot(0, "Day: " + dayAnalysis, Color.YELLOW);

# Trading recommendations
def recommendation = "";
if highTouchSignal != 0 {
    recommendation = "SELL at " + AsPrice(prevHigh) + "\nStop: " + AsPrice(highTouchStopLoss) + "\nTarget: " + AsPrice(highTouchTakeProfit);
} else if lowTouchSignal != 0 {
    recommendation = "BUY at " + AsPrice(prevLow) + "\nStop: " + AsPrice(lowTouchStopLoss) + "\nTarget: " + AsPrice(lowTouchTakeProfit);
} else {
    recommendation = "No signal - Wait for touch";
}

# Display recommendation
AddLabel(yes, recommendation, if highTouchSignal != 0 then Color.RED else if lowTouchSignal != 0 then Color.GREEN else Color.GRAY);