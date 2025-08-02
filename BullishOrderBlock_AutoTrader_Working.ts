# Bullish Order Block Auto-Trading Strategy for QQQ Shares on Thinkorswim
# Designed for 1-minute chart
# Strategy: Go long on green dot, flip to short on red dot, flip back to long when price hits green dot level

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

# --- Strategy Logic using ThinkScript syntax ---
# Rule 1: Go long on green dot (Bullish Order Block) when flat
def shouldGoLong = isBullishOrderBlock and bullishUnmitigated;

# Rule 2: Exit long and go short on red dot (close below Bullish Order Block)
def shouldExitLongGoShort = closeBelowBullish and !redDotPlotted[1];

# Rule 3: Exit short and go long when price hits green dot level (lastBullishLevel)
def shouldExitShortGoLong = high1 >= lastBullishLevel;

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

# --- Plot Exit Short Signal ---
plot ExitShort = if shouldExitShortGoLong then high1 else Double.NaN;
ExitShort.SetDefaultColor(Color.BLUE);
ExitShort.SetStyle(Curve.POINTS);
ExitShort.SetLineWeight(3);

# --- Strategy Orders ---
# Go long on green dot (Bullish Order Block)
AddOrder(OrderType.BUY_TO_OPEN, shouldGoLong, close1, 100, Color.GREEN, Color.GREEN, "Long on Green Dot");

# Exit long and go short on red dot (close below Bullish Order Block)
AddOrder(OrderType.SELL_TO_CLOSE, shouldExitLongGoShort, close1, 100, Color.RED, Color.RED, "Exit Long");
AddOrder(OrderType.SELL_TO_OPEN, shouldExitLongGoShort, close1, 100, Color.RED, Color.RED, "Short on Red Dot");

# Exit short and go long when price hits green dot level
AddOrder(OrderType.BUY_TO_CLOSE, shouldExitShortGoLong, lastBullishLevel, 100, Color.GREEN, Color.GREEN, "Exit Short");
AddOrder(OrderType.BUY_TO_OPEN, shouldExitShortGoLong, lastBullishLevel, 100, Color.GREEN, Color.GREEN, "Long on Green Level");

# --- Performance Labels ---
AddLabel(yes, "Bullish Order Block Auto-Trader", Color.WHITE);
AddLabel(yes, "Green Dot = BUY LONG", Color.GREEN);
AddLabel(yes, "Red Dot = SELL LONG, BUY SHORT", Color.RED);
AddLabel(yes, "Blue Dot = SELL SHORT, BUY LONG", Color.BLUE);

# --- Alerts ---
Alert(isBullishOrderBlock and bullishUnmitigated, "Bullish Order Block Detected - Enter LONG", Alert.BAR, Sound.Bell);
Alert(closeBelowBullish and !redDotPlotted[1], "Price Closed Below Bullish Order Block - Exit LONG, Enter SHORT", Alert.BAR, Sound.Ding);
Alert(shouldExitShortGoLong, "Price at Green Dot Level - Exit SHORT, Enter LONG", Alert.BAR, Sound.Chimes);