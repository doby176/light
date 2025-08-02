# Bullish Order Block SHORT Strategy for QQQ Shares on Thinkorswim
# Designed for 1-minute chart
# Strategy: Go short on first close below green dot level, stop out when first green dot appears

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

# --- Position State Tracking ---
def currentPosition = 0; # 0=flat, -1=short
def entryPrice = 0.0;

# --- Strategy Logic ---
# Go short on first close below green dot level when flat
def shouldGoShort = currentPosition[1] == 0 and closeBelowBullish and !redDotPlotted[1];

# Exit short when first green dot appears
def shouldExitShort = currentPosition[1] == -1 and isBullishOrderBlock and bullishUnmitigated;

# Update position
def newPosition = if shouldGoShort then -1
                  else if shouldExitShort then 0
                  else currentPosition[1];

def newEntryPrice = if shouldGoShort then close1 else entryPrice[1];

# Update variables
currentPosition = newPosition;
entryPrice = newEntryPrice;

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

# --- Plot Current Position ---
plot Position = currentPosition;
Position.SetDefaultColor(Color.YELLOW);
Position.SetStyle(Curve.POINTS);
Position.SetLineWeight(2);

# --- Strategy Orders ---
# Go short on first close below green dot level
AddOrder(OrderType.SELL_TO_OPEN, shouldGoShort, close1, 100, Color.RED, Color.RED, "Short on Red Dot");

# Exit short when first green dot appears
AddOrder(OrderType.BUY_TO_CLOSE, shouldExitShort, close1, 100, Color.GREEN, Color.GREEN, "Exit Short");

# --- Performance Labels ---
AddLabel(yes, "SHORT Strategy", Color.WHITE);
AddLabel(yes, "Position: " + (if currentPosition == -1 then "SHORT" else "FLAT"), 
         if currentPosition == -1 then Color.RED else Color.GRAY);
AddLabel(yes, "Entry: $" + Round(entryPrice, 2), Color.WHITE);
AddLabel(yes, "Stop Level: $" + Round(lastBullishLevel, 2), Color.GREEN);

# --- Alerts ---
Alert(shouldGoShort, "Red Dot - Enter SHORT", Alert.BAR, Sound.Ding);
Alert(shouldExitShort, "Green Dot - Exit SHORT", Alert.BAR, Sound.Bell);