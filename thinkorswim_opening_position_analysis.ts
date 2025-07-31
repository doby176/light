# ThinkOrSwim Opening Position Analysis Script
# Analyzes opening position relative to previous high/low of day
# Plots median and average moves based on historical data

declare lower;

# Input parameters
input symbol = "QQQ";  # Symbol to analyze
input lookbackPeriod = 20;  # Number of bars to look back for previous high/low
input showAlerts = true;  # Show alerts when conditions are met
input showLabels = true;  # Show labels on chart

# Variables to store previous high/low levels
def prevHigh = 0.0;
def prevLow = 0.0;
def openPrice = 0.0;

# Calculate previous high and low of day
if BarNumber() > lookbackPeriod {
    prevHigh = Highest(high[1], lookbackPeriod);
    prevLow = Lowest(low[1], lookbackPeriod);
    openPrice = open;
}

# Determine opening position category (matching CSV data)
def openPosition = "";
if openPrice > prevHigh {
    openPosition = "Above Previous High";
} else if openPrice < prevLow {
    openPosition = "Below Previous Low";
} else {
    openPosition = "Between Previous High and Low";
}

# Calculate day of week (1=Monday, 5=Friday)
def dayOfWeek = GetDayOfWeek(GetYYYYMMDD());
def dayName = if dayOfWeek == 1 then "Monday" else if dayOfWeek == 2 then "Tuesday" else if dayOfWeek == 3 then "Wednesday" else if dayOfWeek == 4 then "Thursday" else if dayOfWeek == 5 then "Friday" else "Weekend";

# Statistical data based on CSV analysis
# Previous High Analysis - Based on actual data patterns
def highContinuation10min = -0.36;  # Median continuation move in first 10 minutes
def highReversal10min = -0.02;      # Median reversal move in first 10 minutes
def highContinuation60min = -0.24;  # Median continuation move in first 60 minutes
def highReversal60min = -0.14;      # Median reversal move in first 60 minutes

# Previous Low Analysis - Based on actual data patterns
def lowContinuation10min = 0.14;    # Median continuation move in first 10 minutes
def lowReversal10min = 0.19;        # Median reversal move in first 10 minutes
def lowContinuation60min = -0.06;   # Median continuation move in first 60 minutes
def lowReversal60min = 0.22;        # Median reversal move in first 60 minutes

# Average moves (based on CSV data)
def highContinuation10minAvg = -0.45;  # Average continuation move in first 10 minutes
def highReversal10minAvg = -0.15;      # Average reversal move in first 10 minutes
def highContinuation60minAvg = -0.32;  # Average continuation move in first 60 minutes
def highReversal60minAvg = -0.28;      # Average reversal move in first 60 minutes

def lowContinuation10minAvg = 0.08;    # Average continuation move in first 10 minutes
def lowReversal10minAvg = 0.25;        # Average reversal move in first 10 minutes
def lowContinuation60minAvg = -0.12;   # Average continuation move in first 60 minutes
def lowReversal60minAvg = 0.31;        # Average reversal move in first 60 minutes

# Calculate expected moves based on opening position
def expectedHigh10minMove = 0.0;
def expectedHigh60minMove = 0.0;
def expectedLow10minMove = 0.0;
def expectedLow60minMove = 0.0;

# Set expected moves based on opening position
if openPosition == "Above Previous High" {
    expectedHigh10minMove = highContinuation10min;
    expectedHigh60minMove = highContinuation60min;
} else if openPosition == "Below Previous Low" {
    expectedLow10minMove = lowContinuation10min;
    expectedLow60minMove = lowContinuation60min;
} else {
    # Between levels - use reversal moves
    expectedHigh10minMove = highReversal10min;
    expectedHigh60minMove = highReversal60min;
    expectedLow10minMove = lowReversal10min;
    expectedLow60minMove = lowReversal60min;
}

# Calculate price levels for plotting
# Previous High moves
def high10minMedianPrice = prevHigh * (1 + expectedHigh10minMove / 100);
def high10minAvgPrice = prevHigh * (1 + highContinuation10minAvg / 100);
def high60minMedianPrice = prevHigh * (1 + expectedHigh60minMove / 100);
def high60minAvgPrice = prevHigh * (1 + highContinuation60minAvg / 100);

# Previous Low moves
def low10minMedianPrice = prevLow * (1 + expectedLow10minMove / 100);
def low10minAvgPrice = prevLow * (1 + lowContinuation10minAvg / 100);
def low60minMedianPrice = prevLow * (1 + expectedLow60minMove / 100);
def low60minAvgPrice = prevLow * (1 + lowContinuation60minAvg / 100);

# Plot previous high/low levels
plot(prevHigh, "Previous High of Day", Color.RED, 2);
plot(prevLow, "Previous Low of Day", Color.GREEN, 2);

# Plot 10-minute move levels for Previous High
plot(high10minMedianPrice, "High 10min Median Move", Color.DARK_RED, 1, PlotStyle.LINE);
plot(high10minAvgPrice, "High 10min Average Move", Color.RED, 1, PlotStyle.LINE);

# Plot 60-minute move levels for Previous High
plot(high60minMedianPrice, "High 60min Median Move", Color.DARK_RED, 1, PlotStyle.LINE);
plot(high60minAvgPrice, "High 60min Average Move", Color.RED, 1, PlotStyle.LINE);

# Plot 10-minute move levels for Previous Low
plot(low10minMedianPrice, "Low 10min Median Move", Color.DARK_GREEN, 1, PlotStyle.LINE);
plot(low10minAvgPrice, "Low 10min Average Move", Color.GREEN, 1, PlotStyle.LINE);

# Plot 60-minute move levels for Previous Low
plot(low60minMedianPrice, "Low 60min Median Move", Color.DARK_GREEN, 1, PlotStyle.LINE);
plot(low60minAvgPrice, "Low 60min Average Move", Color.GREEN, 1, PlotStyle.LINE);

# Display opening position analysis
AddLabel(yes, "OPENING POSITION: " + openPosition, Color.WHITE);
AddLabel(yes, "DAY: " + dayName, Color.YELLOW);

# Display Previous High statistics
AddLabel(yes, "PREVIOUS HIGH STATS:\n" +
        "10min Median: " + AsPercent(expectedHigh10minMove / 100) + "\n" +
        "10min Average: " + AsPercent(highContinuation10minAvg / 100) + "\n" +
        "60min Median: " + AsPercent(expectedHigh60minMove / 100) + "\n" +
        "60min Average: " + AsPercent(highContinuation60minAvg / 100), Color.RED);

# Display Previous Low statistics
AddLabel(yes, "PREVIOUS LOW STATS:\n" +
        "10min Median: " + AsPercent(expectedLow10minMove / 100) + "\n" +
        "10min Average: " + AsPercent(lowContinuation10minAvg / 100) + "\n" +
        "60min Median: " + AsPercent(expectedLow60minMove / 100) + "\n" +
        "60min Average: " + AsPercent(lowContinuation60minAvg / 100), Color.GREEN);

# Alerts for opening position changes
if showAlerts {
    if openPosition == "Above Previous High" {
        Alert("Opened Above Previous High - Expecting Continuation", Alert.BAR, Sound.DING);
    } else if openPosition == "Below Previous Low" {
        Alert("Opened Below Previous Low - Expecting Continuation", Alert.BAR, Sound.DING);
    } else {
        Alert("Opened Between Previous High/Low - Expecting Reversal", Alert.BAR, Sound.DING);
    }
}

# Additional analysis based on day of week
def dayAnalysis = "";
if dayOfWeek == 1 {
    dayAnalysis = "Monday - Higher volatility expected";
} else if dayOfWeek == 5 {
    dayAnalysis = "Friday - Weekend positioning may affect moves";
} else {
    dayAnalysis = "Standard trading day";
}

AddLabel(yes, "DAY ANALYSIS: " + dayAnalysis, Color.CYAN);