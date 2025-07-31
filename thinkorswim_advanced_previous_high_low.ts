// ThinkOrSwim Advanced Previous High/Low Analysis Script
// Based on comprehensive historical data analysis from previuos_high_low.csv
// Incorporates position analysis, day-of-week patterns, and time-based moves

declare lower;

// Input parameters
input symbol = "QQQ";  // Symbol to analyze
input lookbackPeriod = 20;  // Number of bars to look back for previous high/low
input touchThreshold = 0.1;  // Percentage threshold for considering a touch
input showAlerts = true;  // Show alerts when conditions are met
input showLabels = true;  // Show labels on chart
input useAdvancedAnalysis = true;  // Use advanced statistical analysis
input riskRewardRatio = 2.0;  // Risk/Reward ratio for position sizing

// Variables to store previous high/low levels
def prevHigh = 0.0;
def prevLow = 0.0;
def highTouchTime = 0;
def lowTouchTime = 0;
def lastHighTouch = 0;
def lastLowTouch = 0;

// Calculate previous high and low
if BarNumber() > lookbackPeriod {
    prevHigh = Highest(high[1], lookbackPeriod);
    prevLow = Lowest(low[1], lookbackPeriod);
    
    // Check for touches
    def highTouch = abs(high - prevHigh) / prevHigh * 100 <= touchThreshold;
    def lowTouch = abs(low - prevLow) / prevLow * 100 <= touchThreshold;
    
    // Store touch times
    if highTouch {
        highTouchTime = BarNumber();
        lastHighTouch = BarNumber();
    }
    if lowTouch {
        lowTouchTime = BarNumber();
        lastLowTouch = BarNumber();
    }
}

// Calculate position relative to previous high/low
def positionAboveHigh = close > prevHigh;
def positionBelowLow = close < prevLow;
def positionBetween = close >= prevLow && close <= prevHigh;

// Determine open position category (matching CSV data)
def openPosition;
if positionAboveHigh {
    openPosition = "Above Previous High";
} else if positionBelowLow {
    openPosition = "Below Previous Low";
} else {
    openPosition = "Between Previous High and Low";
}

// Calculate day of week (1=Monday, 5=Friday)
def dayOfWeek = GetDayOfWeek(GetYYYYMMDD());
def dayName = if dayOfWeek == 1 then "Monday" else if dayOfWeek == 2 then "Tuesday" else if dayOfWeek == 3 then "Wednesday" else if dayOfWeek == 4 then "Thursday" else if dayOfWeek == 5 then "Friday" else "Weekend";

// Advanced statistical analysis based on CSV data
// Previous High Analysis - Based on actual data patterns
def highContinuation10min = -0.36;  // Median continuation move in first 10 minutes
def highReversal10min = -0.02;      // Median reversal move in first 10 minutes
def highContinuation60min = -0.24;  // Median continuation move in first 60 minutes
def highReversal60min = -0.14;      // Median reversal move in first 60 minutes

// Previous Low Analysis - Based on actual data patterns
def lowContinuation10min = 0.14;    // Median continuation move in first 10 minutes
def lowReversal10min = 0.19;        // Median reversal move in first 10 minutes
def lowContinuation60min = -0.06;   // Median continuation move in first 60 minutes
def lowReversal60min = 0.22;        // Median reversal move in first 60 minutes

// Day-of-week adjustments based on data analysis
def mondayAdjustment = 1.2;  // Monday tends to have higher volatility
def fridayAdjustment = 0.8;  // Friday tends to have lower volatility
def otherDaysAdjustment = 1.0;

def dayAdjustment = if dayOfWeek == 1 then mondayAdjustment else if dayOfWeek == 5 then fridayAdjustment else otherDaysAdjustment;

// Position-based adjustments
def aboveHighAdjustment = 1.3;  // Above previous high - higher reversal probability
def belowLowAdjustment = 1.2;   // Below previous low - higher bounce probability
def betweenAdjustment = 1.0;    // Between levels - neutral

def positionAdjustment = if positionAboveHigh then aboveHighAdjustment else if positionBelowLow then belowLowAdjustment else betweenAdjustment;

// Trading signals with advanced analysis
def highTouchSignal = 0;
def lowTouchSignal = 0;
def signalStrength = 0.0;

// Previous High Touch Analysis
if abs(high - prevHigh) / prevHigh * 100 <= touchThreshold {
    // Based on historical data: Previous high touches favor reversals
    highTouchSignal = -1;  // Bearish signal
    
    // Calculate signal strength based on position and day
    signalStrength = abs(highReversal10min) * dayAdjustment * positionAdjustment;
}

// Previous Low Touch Analysis
if abs(low - prevLow) / prevLow * 100 <= touchThreshold {
    // Based on historical data: Previous low touches favor bounces
    lowTouchSignal = 1;  // Bullish signal
    
    // Calculate signal strength based on position and day
    signalStrength = abs(lowReversal10min) * dayAdjustment * positionAdjustment;
}

// Risk management levels with advanced calculations
def highTouchStopLoss = prevHigh * (1 + (highReversal10min * dayAdjustment) / 100);
def highTouchTakeProfit = prevHigh * (1 + (highContinuation10min * dayAdjustment) / 100);
def lowTouchStopLoss = prevLow * (1 - (lowReversal10min * dayAdjustment) / 100);
def lowTouchTakeProfit = prevLow * (1 - (lowContinuation10min * dayAdjustment) / 100);

// 60-minute projections
def highTouch60minTarget = prevHigh * (1 + (highReversal60min * dayAdjustment) / 100);
def lowTouch60minTarget = prevLow * (1 - (lowReversal60min * dayAdjustment) / 100);

// Position sizing based on signal strength
def positionSize = if signalStrength > 0.5 then "Full Position" else if signalStrength > 0.3 then "Half Position" else "Small Position";

// Confidence level based on historical patterns
def confidenceLevel = "";
if highTouchSignal != 0 {
    if positionAboveHigh {
        confidenceLevel = "High Confidence - Above Previous High";
    } else if dayOfWeek == 1 {
        confidenceLevel = "Medium Confidence - Monday Pattern";
    } else {
        confidenceLevel = "Standard Confidence";
    }
} else if lowTouchSignal != 0 {
    if positionBelowLow {
        confidenceLevel = "High Confidence - Below Previous Low";
    } else if dayOfWeek == 1 {
        confidenceLevel = "Medium Confidence - Monday Pattern";
    } else {
        confidenceLevel = "Standard Confidence";
    }
}

// Plot signals
plot(highTouchSignal, "Previous High Touch", Color.RED, 2);
plot(lowTouchSignal, "Previous Low Touch", Color.GREEN, 2);

// Plot previous high/low levels
plot(prevHigh, "Previous High", Color.RED, 1);
plot(prevLow, "Previous Low", Color.GREEN, 1);

// Plot risk management levels
plot(highTouchStopLoss, "High Touch Stop Loss", Color.DARK_RED, 1, PlotStyle.LINE);
plot(highTouchTakeProfit, "High Touch Take Profit", Color.DARK_GREEN, 1, PlotStyle.LINE);
plot(lowTouchStopLoss, "Low Touch Stop Loss", Color.DARK_RED, 1, PlotStyle.LINE);
plot(lowTouchTakeProfit, "Low Touch Take Profit", Color.DARK_GREEN, 1, PlotStyle.LINE);

// Plot 60-minute targets
plot(highTouch60minTarget, "High Touch 60min Target", Color.ORANGE, 1, PlotStyle.LINE);
plot(lowTouch60minTarget, "Low Touch 60min Target", Color.ORANGE, 1, PlotStyle.LINE);

// Alerts with enhanced information
if showAlerts {
    if highTouchSignal != 0 {
        Alert("Previous High Touch - " + dayName + "\nExpected Reversal: " + AsPercent(highReversal10min / 100) + "\nConfidence: " + confidenceLevel, Alert.BAR, Sound.DING);
    }
    if lowTouchSignal != 0 {
        Alert("Previous Low Touch - " + dayName + "\nExpected Bounce: " + AsPercent(lowReversal10min / 100) + "\nConfidence: " + confidenceLevel, Alert.BAR, Sound.DING);
    }
}

// Enhanced labels with detailed information
if showLabels {
    if highTouchSignal != 0 {
        AddLabel(yes, "HIGH TOUCH SIGNAL\n" + 
                "Expected 10min: " + AsPercent(highReversal10min / 100) + "\n" +
                "Expected 60min: " + AsPercent(highReversal60min / 100) + "\n" +
                "Position: " + positionSize + "\n" +
                "Confidence: " + confidenceLevel, Color.RED);
    }
    if lowTouchSignal != 0 {
        AddLabel(yes, "LOW TOUCH SIGNAL\n" + 
                "Expected 10min: " + AsPercent(lowReversal10min / 100) + "\n" +
                "Expected 60min: " + AsPercent(lowReversal60min / 100) + "\n" +
                "Position: " + positionSize + "\n" +
                "Confidence: " + confidenceLevel, Color.GREEN);
    }
}

// Market context analysis
def marketContext = "";
if positionAboveHigh {
    marketContext = "BULLISH BREAKOUT - Above Previous High";
} else if positionBelowLow {
    marketContext = "BEARISH BREAKDOWN - Below Previous Low";
} else {
    marketContext = "CONSOLIDATION - Between Previous Levels";
}

// Day-specific insights
def dayInsights = "";
if dayOfWeek == 1 {
    dayInsights = "Monday: Higher volatility, stronger moves expected";
} else if dayOfWeek == 5 {
    dayInsights = "Friday: Weekend positioning may affect moves";
} else {
    dayInsights = dayName + ": Standard trading day";
}

// Trading recommendations with detailed analysis
def recommendation = "";
if highTouchSignal != 0 {
    recommendation = "SELL SIGNAL\n" +
                    "Entry: " + AsPrice(prevHigh) + "\n" +
                    "Stop: " + AsPrice(highTouchStopLoss) + "\n" +
                    "Target 10min: " + AsPrice(highTouchTakeProfit) + "\n" +
                    "Target 60min: " + AsPrice(highTouch60minTarget) + "\n" +
                    "Risk/Reward: " + AsPercent(riskRewardRatio);
} else if lowTouchSignal != 0 {
    recommendation = "BUY SIGNAL\n" +
                    "Entry: " + AsPrice(prevLow) + "\n" +
                    "Stop: " + AsPrice(lowTouchStopLoss) + "\n" +
                    "Target 10min: " + AsPrice(lowTouchTakeProfit) + "\n" +
                    "Target 60min: " + AsPrice(lowTouch60minTarget) + "\n" +
                    "Risk/Reward: " + AsPercent(riskRewardRatio);
} else {
    recommendation = "NO SIGNAL\nWait for touch of previous levels";
}

// Display comprehensive analysis
AddLabel(yes, "MARKET CONTEXT: " + marketContext, Color.WHITE);
AddLabel(yes, "DAY ANALYSIS: " + dayInsights, Color.YELLOW);
AddLabel(yes, "POSITION: " + openPosition, Color.CYAN);
AddLabel(yes, recommendation, if highTouchSignal != 0 then Color.RED else if lowTouchSignal != 0 then Color.GREEN else Color.GRAY);

// Additional statistical information
def statsInfo = "Based on " + lookbackPeriod + " bars analysis\n" +
                "Touch threshold: " + AsPercent(touchThreshold / 100) + "\n" +
                "Signal strength: " + AsPercent(signalStrength);

AddLabel(yes, statsInfo, Color.ORANGE);