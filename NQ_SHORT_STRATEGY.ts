# Bullish Order Block Short Strategy for NQ/MNQ Futures on ThinkorSwim
# Designed for 1-minute chart
# Strategy: Go short on first close below last green dot, stop out when first green dot appears
# Includes Alerts for Bullish Order Block and Close Below
# **NEW: Closes all positions at market close to avoid overnight positions**

# --- 1-Minute Data ---
def close1 = close;
def open1 = open;
def high1 = high;
def low1 = low;

# --- Daily Close Logic - SIMPLE AND RELIABLE ---
# Check if we're in the last 2 minutes of regular trading session
def isLastMinute = SecondsFromTime(1600) <= 120; # Last 2 minutes before 4:00 PM
def isMarketClosed = SecondsFromTime(1600) > 0; # After 4:00 PM

# Close all positions in last 2 minutes of trading
def shouldCloseDaily = isLastMinute or isMarketClosed;

# --- Bullish Order Block Detection (1-Minute Chart) ---
# Inefficiency: Shadow gap > 1.5x candle body
def inefficiency = AbsValue(high1[1] - low1) > AbsValue(close1[1] - open1[1]) * 1.5;

# Bullish Break of Structure (BOS) and Change of Character (CHOCH)
def bosUp = high1 > Highest(high1[2], 3); # Breaks recent high
def chochUp = low1 < Lowest(low1[2], 3) and high1 > Highest(high1[2], 3); # Higher high, lower low

# Bullish Order Block
def isBullishOrderBlock = (inefficiency[1] and (bosUp or chochUp)) and !IsNaN(close1[1]);

# Track Order Block Level (Single Line at Open)
def bullishOrderBlockLevel = if isBullishOrderBlock then open1[1] else Double.NaN;

# Track Mitigation
def bullishUnmitigated = if isBullishOrderBlock then 1 else if close1 < GetValue(low1, 1) and GetValue(isBullishOrderBlock, 1) then 0 else bullishUnmitigated[1];

# Track the last valid Bullish Order Block level
def lastBullishLevel = if isBullishOrderBlock then open1[1] else lastBullishLevel[1];

# Detect when price closes below the last Bullish Order Block level
def closeBelowBullish = close1 < lastBullishLevel and !IsNaN(lastBullishLevel) and bullishUnmitigated[1];

# Track if a red dot has already been plotted
def redDotPlotted = if isBullishOrderBlock then 0 else if closeBelowBullish and !redDotPlotted[1] then 1 else redDotPlotted[1];

# --- Plot Single Line on Order Block Candle ---
plot BullishOrderBlock = if isBullishOrderBlock and bullishUnmitigated then bullishOrderBlockLevel else Double.NaN;
BullishOrderBlock.SetDefaultColor(Color.LIGHT_GREEN);
BullishOrderBlock.SetStyle(Curve.POINTS);
BullishOrderBlock.SetLineWeight(3);

# --- Plot Single Red Dot when Price Closes Below Last Bullish Order Block ---
plot RedDot = if closeBelowBullish and !redDotPlotted[1] then close1 else Double.NaN;
RedDot.SetDefaultColor(Color.RED);
RedDot.SetStyle(Curve.POINTS);
RedDot.SetLineWeight(3);

# --- Strategy Logic ---
# Position management - FORCE CLOSE at end of day
def currentPosition = if closeBelowBullish and !redDotPlotted[1] then -1 else if isBullishOrderBlock and bullishUnmitigated then 0 else if shouldCloseDaily then 0 else currentPosition[1];
def entryPrice = if closeBelowBullish and !redDotPlotted[1] then close1 else entryPrice[1];

# Go short on first close below last green dot (red dot appears)
AddOrder(OrderType.SELL_TO_OPEN, closeBelowBullish and !redDotPlotted[1], close1, 1, Color.RED, Color.RED, "NQ Short on Red Dot");

# Exit short when first green dot appears
AddOrder(OrderType.BUY_TO_CLOSE, isBullishOrderBlock and bullishUnmitigated, close1, 1, Color.GREEN, Color.GREEN, "NQ Exit Short (Green Dot)");

# **FORCE CLOSE: Exit all positions at end of trading day**
AddOrder(OrderType.BUY_TO_CLOSE, shouldCloseDaily and currentPosition[1] < 0, close1, 1, Color.ORANGE, Color.ORANGE, "NQ FORCE CLOSE - End of Day");

# --- Alerts ---
Alert(closeBelowBullish and !redDotPlotted[1], "NQ Short Entry - Price Closed Below Green Dot", Alert.BAR, Sound.Ding);
Alert(isBullishOrderBlock and bullishUnmitigated, "NQ Exit Short - Green Dot Appeared", Alert.BAR, Sound.Bell);
Alert(shouldCloseDaily and currentPosition[1] < 0, "NQ FORCE CLOSE - End of Trading Day", Alert.BAR, Sound.Chimes);