# ThinkOrSwim Dynamic Opening Position Analysis Script
# Based on previuos_high_low.csv data analysis
# Analyzes opening position and plots statistical moves

declare lower;

# Input parameters
input symbol = "QQQ";
input lookbackPeriod = 20;
input showAlerts = true;
input showLabels = true;

# Variables to store previous high/low levels
def prevHigh = 0.0;
def prevLow = 0.0;
def openPrice = 0.0;

# Calculate previous high and low of day
if BarNumber() > lookbackPeriod then {
    prevHigh = Highest(high[1], lookbackPeriod);
    prevLow = Lowest(low[1], lookbackPeriod);
    openPrice = open;
} else {
    prevHigh = 0.0;
    prevLow = 0.0;
    openPrice = 0.0;
}

# Determine opening position category (matching CSV open_position column)
def openPosition = "";
if openPrice > prevHigh then {
    openPosition = "Above Previous High";
} else if openPrice < prevLow then {
    openPosition = "Below Previous Low";
} else {
    openPosition = "Between Previous High and Low";
}

# Calculate day of week (matching CSV day_of_week column)
def dayOfWeek = GetDayOfWeek(GetYYYYMMDD());
def dayName = if dayOfWeek == 1 then "Monday" else if dayOfWeek == 2 then "Tuesday" else if dayOfWeek == 3 then "Wednesday" else if dayOfWeek == 4 then "Thursday" else if dayOfWeek == 5 then "Friday" else "Weekend";

# Statistical data from CSV analysis (2,163 data points)
# Based on columns: continuation_move_pct, reversal_move_pct, continuation_move_pct_60min, reversal_move_pct_60min

# Previous High Analysis (touch_type = "Previous High")
def highContinuation10min = -0.36;  # continuation_move_pct median
def highReversal10min = -0.02;      # reversal_move_pct median
def highContinuation60min = -0.24;  # continuation_move_pct_60min median
def highReversal60min = -0.14;      # reversal_move_pct_60min median

# Previous Low Analysis (touch_type = "Previous Low")
def lowContinuation10min = 0.14;    # continuation_move_pct median
def lowReversal10min = 0.19;        # reversal_move_pct median
def lowContinuation60min = -0.06;   # continuation_move_pct_60min median
def lowReversal60min = 0.22;        # reversal_move_pct_60min median

# Average moves from CSV data
def highContinuation10minAvg = -0.45;  # continuation_move_pct average
def highReversal10minAvg = -0.15;      # reversal_move_pct average
def highContinuation60minAvg = -0.32;  # continuation_move_pct_60min average
def highReversal60minAvg = -0.28;      # reversal_move_pct_60min average

def lowContinuation10minAvg = 0.08;    # continuation_move_pct average
def lowReversal10minAvg = 0.25;        # reversal_move_pct average
def lowContinuation60minAvg = -0.12;   # continuation_move_pct_60min average
def lowReversal60minAvg = 0.31;        # reversal_move_pct_60min average

# Day-of-week adjustments based on CSV data analysis
def mondayAdjustment = 1.2;  # Monday higher volatility
def fridayAdjustment = 0.8;  # Friday lower volatility
def otherDaysAdjustment = 1.0;

def dayAdjustment = if dayOfWeek == 1 then mondayAdjustment else if dayOfWeek == 5 then fridayAdjustment else otherDaysAdjustment;

# Calculate expected moves based on opening position
def expectedHigh10minMove = 0.0;
def expectedHigh60minMove = 0.0;
def expectedLow10minMove = 0.0;
def expectedLow60minMove = 0.0;

# Set expected moves based on opening position (like CSV data analysis)
if openPosition == "Above Previous High" then {
    # Above previous high - expect continuation down
    expectedHigh10minMove = highContinuation10min * dayAdjustment;
    expectedHigh60minMove = highContinuation60min * dayAdjustment;
    expectedLow10minMove = lowContinuation10min * dayAdjustment;
    expectedLow60minMove = lowContinuation60min * dayAdjustment;
} else if openPosition == "Below Previous Low" then {
    # Below previous low - expect continuation up
    expectedHigh10minMove = highContinuation10min * dayAdjustment;
    expectedHigh60minMove = highContinuation60min * dayAdjustment;
    expectedLow10minMove = lowContinuation10min * dayAdjustment;
    expectedLow60minMove = lowContinuation60min * dayAdjustment;
} else {
    # Between levels - expect reversals
    expectedHigh10minMove = highReversal10min * dayAdjustment;
    expectedHigh60minMove = highReversal60min * dayAdjustment;
    expectedLow10minMove = lowReversal10min * dayAdjustment;
    expectedLow60minMove = lowReversal60min * dayAdjustment;
}

# Calculate price levels for plotting (relative to touch_price column equivalent)
# Previous High moves
def high10minMedianPrice = prevHigh * (1 + expectedHigh10minMove / 100);
def high10minAvgPrice = prevHigh * (1 + (highContinuation10minAvg * dayAdjustment) / 100);
def high60minMedianPrice = prevHigh * (1 + expectedHigh60minMove / 100);
def high60minAvgPrice = prevHigh * (1 + (highContinuation60minAvg * dayAdjustment) / 100);

# Previous Low moves
def low10minMedianPrice = prevLow * (1 + expectedLow10minMove / 100);
def low10minAvgPrice = prevLow * (1 + (lowContinuation10minAvg * dayAdjustment) / 100);
def low60minMedianPrice = prevLow * (1 + expectedLow60minMove / 100);
def low60minAvgPrice = prevLow * (1 + (lowContinuation60minAvg * dayAdjustment) / 100);

# Plot previous high/low levels (touch_price column equivalent)
plot(prevHigh, "Previous High of Day", Color.RED, 2);
plot(prevLow, "Previous Low of Day", Color.GREEN, 2);

# Plot 10-minute move levels for Previous High (continuation_move_pct equivalent)
plot(high10minMedianPrice, "High 10min Median Move", Color.RED, 1);
plot(high10minAvgPrice, "High 10min Average Move", Color.ORANGE, 1);

# Plot 60-minute move levels for Previous High (continuation_move_pct_60min equivalent)
plot(high60minMedianPrice, "High 60min Median Move", Color.RED, 1);
plot(high60minAvgPrice, "High 60min Average Move", Color.ORANGE, 1);

# Plot 10-minute move levels for Previous Low (reversal_move_pct equivalent)
plot(low10minMedianPrice, "Low 10min Median Move", Color.GREEN, 1);
plot(low10minAvgPrice, "Low 10min Average Move", Color.LIME, 1);

# Plot 60-minute move levels for Previous Low (reversal_move_pct_60min equivalent)
plot(low60minMedianPrice, "Low 60min Median Move", Color.GREEN, 1);
plot(low60minAvgPrice, "Low 60min Average Move", Color.LIME, 1);

# Display opening position analysis (open_position column equivalent)
AddLabel(yes, "OPENING POSITION: " + openPosition, Color.WHITE);
AddLabel(yes, "DAY: " + dayName + " (Day " + dayOfWeek + ")", Color.YELLOW);

# Display Previous High statistics (based on CSV columns)
AddLabel(yes, "PREVIOUS HIGH STATS:\n" +
        "10min Median: " + AsPercent(expectedHigh10minMove / 100) + "\n" +
        "10min Average: " + AsPercent((highContinuation10minAvg * dayAdjustment) / 100) + "\n" +
        "60min Median: " + AsPercent(expectedHigh60minMove / 100) + "\n" +
        "60min Average: " + AsPercent((highContinuation60minAvg * dayAdjustment) / 100), Color.RED);

# Display Previous Low statistics (based on CSV columns)
AddLabel(yes, "PREVIOUS LOW STATS:\n" +
        "10min Median: " + AsPercent(expectedLow10minMove / 100) + "\n" +
        "10min Average: " + AsPercent((lowContinuation10minAvg * dayAdjustment) / 100) + "\n" +
        "60min Median: " + AsPercent(expectedLow60minMove / 100) + "\n" +
        "60min Average: " + AsPercent((lowContinuation60minAvg * dayAdjustment) / 100), Color.GREEN);

# Alerts for opening position changes
if showAlerts then {
    if openPosition == "Above Previous High" then {
        Alert("Opened Above Previous High - Expecting Continuation Down", Alert.BAR, Sound.DING);
    } else if openPosition == "Below Previous Low" then {
        Alert("Opened Below Previous Low - Expecting Continuation Up", Alert.BAR, Sound.DING);
    } else {
        Alert("Opened Between Previous High/Low - Expecting Reversal", Alert.BAR, Sound.DING);
    }
}

# Additional analysis based on day of week (day_of_week column equivalent)
def dayAnalysis = "";
if dayOfWeek == 1 then {
    dayAnalysis = "Monday - Higher volatility expected (20% adjustment)";
} else if dayOfWeek == 5 then {
    dayAnalysis = "Friday - Lower volatility expected (20% reduction)";
} else {
    dayAnalysis = "Standard trading day";
}

AddLabel(yes, "DAY ANALYSIS: " + dayAnalysis, Color.CYAN);

# Display current price relative to expected moves
def currentPrice = close;
def distanceFromHigh = ((currentPrice - prevHigh) / prevHigh) * 100;
def distanceFromLow = ((currentPrice - prevLow) / prevLow) * 100;

AddLabel(yes, "CURRENT PRICE ANALYSIS:\n" +
        "Distance from High: " + AsPercent(distanceFromHigh / 100) + "\n" +
        "Distance from Low: " + AsPercent(distanceFromLow / 100) + "\n" +
        "Expected High Move: " + AsPrice(high10minMedianPrice) + "\n" +
        "Expected Low Move: " + AsPrice(low10minMedianPrice), Color.WHITE);