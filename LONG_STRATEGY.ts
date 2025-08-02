# Bullish Order Block Long Strategy for QQQ Shares on ThinkorSwim
# Designed for 1-minute chart
# Strategy: Add 100 shares on each green dot, exit when price closes below green dot
# Includes Alerts for Bullish Order Block and Close Below

# --- 1-Minute Data ---
def close1 = close;
def open1 = open;
def high1 = high;
def low1 = low;

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
# Check if green dot appears AND candle closes above it
def greenDotWithValidClose = isBullishOrderBlock and bullishUnmitigated and close1 > bullishOrderBlockLevel;

# Position management - track total shares
def totalShares = if greenDotWithValidClose then totalShares[1] + 100 else if closeBelowBullish and !redDotPlotted[1] then 0 else totalShares[1];
def entryPrice = if greenDotWithValidClose then close1 else entryPrice[1];

# Add 100 shares on each green dot (valid close)
AddOrder(OrderType.BUY_TO_OPEN, greenDotWithValidClose, close1, 100, Color.GREEN, Color.GREEN, "QQQ Add 100 Shares on Green Dot");

# Exit all positions when price closes below the last green dot (red dot appears)
AddOrder(OrderType.SELL_TO_CLOSE, closeBelowBullish and !redDotPlotted[1] and totalShares[1] > 0, close1, totalShares[1], Color.RED, Color.RED, "QQQ Exit All Positions (Close Below Green Dot)");

# --- Alerts ---
Alert(greenDotWithValidClose, "QQQ Add 100 Shares - Green Dot with Close Above", Alert.BAR, Sound.Bell);
Alert(closeBelowBullish and !redDotPlotted[1] and totalShares[1] > 0, "QQQ Exit All Positions - Price Closed Below Green Dot", Alert.BAR, Sound.Ding);