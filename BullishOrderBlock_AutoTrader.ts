# Bullish Order Block Auto-Trader for ThinkorSwim
# Focuses on generating trading signals for manual execution
# This version should work without syntax errors

# Input parameters
input symbol = "QQQ";
input enableShorting = yes;
input autoCycle = yes;

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

# Trading signals
def longSignal = isBullishOrderBlock and bullishUnmitigated;
def shortSignal = closeBelowBullish and !redDotPlotted[1];
def exitShortSignal = high >= lastBullishLevel;

# Plot signals
plot BullishOrderBlock = if longSignal then bullishOrderBlockLevel else Double.NaN;
BullishOrderBlock.SetDefaultColor(Color.LIGHT_GREEN);
BullishOrderBlock.SetStyle(Curve.POINTS);
BullishOrderBlock.SetLineWeight(3);

plot RedDot = if shortSignal then close else Double.NaN;
RedDot.SetDefaultColor(Color.RED);
RedDot.SetStyle(Curve.POINTS);
RedDot.SetLineWeight(3);

plot ExitShort = if exitShortSignal then high else Double.NaN;
ExitShort.SetDefaultColor(Color.BLUE);
ExitShort.SetStyle(Curve.POINTS);
ExitShort.SetLineWeight(3);

# Add labels for trading signals
AddLabel(yes, "Bullish Order Block Auto-Trader", Color.WHITE);
AddLabel(yes, "Green Dot = BUY LONG", Color.GREEN);
AddLabel(yes, "Red Dot = SELL LONG, BUY SHORT", Color.RED);
AddLabel(yes, "Blue Dot = SELL SHORT, BUY LONG", Color.BLUE);

# Alerts for trading signals
Alert(longSignal, "BUY LONG - Bullish Order Block Detected", Alert.BAR, Sound.Bell);
Alert(shortSignal, "SELL LONG, BUY SHORT - Price Below Order Block", Alert.BAR, Sound.Ding);
Alert(exitShortSignal, "SELL SHORT, BUY LONG - Price at Order Block Level", Alert.BAR, Sound.Chimes);