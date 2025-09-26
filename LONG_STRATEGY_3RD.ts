# Bullish Order Block LONG Strategy for QQQ Shares on Thinkorswim
# Designed for 1-minute chart
# Strategy: Enter on 3rd green dot only, exit when price closes below green dot level

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

# Count green dots
def greenDotCount = if isBullishOrderBlock and bullishUnmitigated then greenDotCount[1] + 1 else if closeBelowBullish and !redDotPlotted[1] then 0 else greenDotCount[1];

# --- Strategy Logic ---
# Enter on 3rd green dot only
def shouldEnterLong = currentPosition[1] == 0 and isBullishOrderBlock and bullishUnmitigated and greenDotCount == 3;

# Exit when price closes below green dot level
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
# Enter on 3rd green dot only
AddOrder(OrderType.BUY_TO_OPEN, shouldEnterLong, close1, 100, Color.GREEN, Color.GREEN, "3RD Green Dot - Enter Long");

# Exit when price closes below green dot level
AddOrder(OrderType.SELL_TO_CLOSE, shouldExitLong, close1, 100, Color.RED, Color.RED, "Exit Long");

# --- Performance Labels ---
AddLabel(yes, "3RD Green Dot Strategy", Color.WHITE);
AddLabel(yes, "Position: " + (if currentPosition == 1 then "LONG" else "FLAT"), 
         if currentPosition == 1 then Color.GREEN else Color.GRAY);
AddLabel(yes, "Green Dots: " + greenDotCount, Color.WHITE);
AddLabel(yes, "Entry: $" + Round(entryPrice, 2), Color.WHITE);
AddLabel(yes, "Stop Level: $" + Round(lastBullishLevel, 2), Color.RED);

# --- Alerts ---
Alert(shouldEnterLong, "3RD Green Dot - Enter LONG", Alert.BAR, Sound.Bell);
Alert(shouldExitLong, "Red Dot - Exit LONG", Alert.BAR, Sound.Ding);