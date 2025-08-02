# Bullish Order Block Strategy for ThinkorSwim
# Simple working version with basic ThinkScript syntax

# Input parameters
input enableShorting = yes;
input autoCycle = yes;
input stopLossPercent = 1.0;

# Bullish Order Block Detection
def inefficiency = AbsValue(high[1] - low) > AbsValue(close[1] - open[1]) * 1.5;
def bosUp = high > Highest(high[2], 3);
def chochUp = low < Lowest(low[2], 3) and high > Highest(high[2], 3);
def isBullishOrderBlock = inefficiency[1] and (bosUp or chochUp) and !IsNaN(close[1]);

# Track order block level
def bullishOrderBlockLevel = if isBullishOrderBlock then open[1] else Double.NaN;
def bullishUnmitigated = if isBullishOrderBlock then 1 else if close < GetValue(low, 1) and GetValue(isBullishOrderBlock, 1) then 0 else bullishUnmitigated[1];

# Track the last valid Bullish Order Block level
def lastBullishLevel = if isBullishOrderBlock then open[1] else lastBullishLevel[1];

# Detect when price closes below the last Bullish Order Block level
def closeBelowBullish = close < lastBullishLevel and !IsNaN(lastBullishLevel) and bullishUnmitigated[1];

# Track if a red dot has already been plotted
def redDotPlotted = if isBullishOrderBlock then 0 else if closeBelowBullish and !redDotPlotted[1] then 1 else redDotPlotted[1];

# Plot Bullish Order Block levels
plot BullishOrderBlock = if isBullishOrderBlock and bullishUnmitigated then bullishOrderBlockLevel else Double.NaN;
BullishOrderBlock.SetDefaultColor(Color.LIGHT_GREEN);
BullishOrderBlock.SetStyle(Curve.POINTS);
BullishOrderBlock.SetLineWeight(3);

# Plot Red Dot when Price Closes Below Last Bullish Order Block
plot RedDot = if closeBelowBullish and !redDotPlotted[1] then close else Double.NaN;
RedDot.SetDefaultColor(Color.RED);
RedDot.SetStyle(Curve.POINTS);
RedDot.SetLineWeight(3);

# Add labels for information
AddLabel(yes, "Bullish Order Block Strategy", Color.WHITE);
AddLabel(yes, "Green Dot = Enter LONG", Color.GREEN);
AddLabel(yes, "Red Dot = Exit LONG, Enter SHORT", Color.RED);

# Alerts
Alert(isBullishOrderBlock and bullishUnmitigated, "Bullish Order Block Detected - Enter LONG", Alert.BAR, Sound.Bell);
Alert(closeBelowBullish and !redDotPlotted[1], "Price Closed Below Bullish Order Block - Exit LONG, Enter SHORT", Alert.BAR, Sound.Ding);