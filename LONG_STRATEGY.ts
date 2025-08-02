# Bullish Order Block LONG Strategy for QQQ Shares on Thinkorswim
# Designed for 1-minute chart
# Strategy: Scale position size based on green dots, exit when price closes below green dot level

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

# --- Position State Tracking (using recursive definitions) ---
def currentPosition = if currentPosition[1] == 0 and isBullishOrderBlock and bullishUnmitigated then 1
                      else if currentPosition[1] == 1 and closeBelowBullish and !redDotPlotted[1] then 0
                      else currentPosition[1];

def entryPrice = if currentPosition[1] == 0 and isBullishOrderBlock and bullishUnmitigated then close1
                 else entryPrice[1];

# Count green dots and scale position size
def greenDotCount = if isBullishOrderBlock and bullishUnmitigated then greenDotCount[1] + 1 else if closeBelowBullish and !redDotPlotted[1] then 0 else greenDotCount[1];

# Calculate position size: 100 shares per green dot
def positionSize = greenDotCount * 100;

# --- Strategy Logic ---
# Enter with scaled position size on green dot
def shouldEnterLong = currentPosition[1] == 0 and isBullishOrderBlock and bullishUnmitigated;

# Exit all shares when price closes below green dot level
def shouldExitLong = currentPosition[1] == 1 and closeBelowBullish and !redDotPlotted[1];

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
# Enter with scaled position size on green dot
AddOrder(OrderType.BUY_TO_OPEN, shouldEnterLong, close1, positionSize, Color.GREEN, Color.GREEN, "Enter Long - Scaled Position");

# Exit all shares when price closes below green dot level
AddOrder(OrderType.SELL_TO_CLOSE, shouldExitLong, close1, positionSize, Color.RED, Color.RED, "Exit Long - All Shares");

# --- Performance Labels ---
AddLabel(yes, "LONG Strategy - Scaled Position", Color.WHITE);
AddLabel(yes, "Position: " + (if currentPosition == 1 then "LONG" else "FLAT"), 
         if currentPosition == 1 then Color.GREEN else Color.GRAY);
AddLabel(yes, "Green Dots: " + greenDotCount, Color.WHITE);
AddLabel(yes, "Position Size: " + positionSize + " shares", Color.WHITE);
AddLabel(yes, "Stop Level: $" + Round(lastBullishLevel, 2), Color.RED);

# --- Alerts ---
Alert(shouldEnterLong, "Green Dot - Enter Long with " + positionSize + " shares", Alert.BAR, Sound.Bell);
Alert(shouldExitLong, "Red Dot - Exit Long " + positionSize + " shares", Alert.BAR, Sound.Ding);