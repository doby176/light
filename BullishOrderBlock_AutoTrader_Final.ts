# Bullish Order Block Auto-Trading Strategy for QQQ Shares on Thinkorswim
# Designed for 1-minute chart
# Strategy: Go long ONLY when NEW green dot appears, flip to short on red dot, flip back to long on next NEW green dot

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
def currentPosition = if isBullishOrderBlock and bullishUnmitigated then 1
                      else if closeBelowBullish and !redDotPlotted[1] and currentPosition[1] == 1 then -1
                      else if high1 >= lastGreenDotLevel[1] and currentPosition[1] == -1 then 1
                      else currentPosition[1];

def lastGreenDotLevel = if isBullishOrderBlock and bullishUnmitigated then bullishOrderBlockLevel else lastGreenDotLevel[1];
def lastRedDotLevel = if closeBelowBullish and !redDotPlotted[1] and currentPosition[1] == 1 then close1 else lastRedDotLevel[1];

def waitingForRedDot = if isBullishOrderBlock and bullishUnmitigated then 1
                       else if closeBelowBullish and !redDotPlotted[1] and currentPosition[1] == 1 then 0
                       else waitingForRedDot[1];

def waitingForGreenDot = if closeBelowBullish and !redDotPlotted[1] and currentPosition[1] == 1 then 1
                         else if high1 >= lastGreenDotLevel[1] and currentPosition[1] == -1 then 0
                         else waitingForGreenDot[1];

# --- Strategy Logic ---
# Rule 1: Go long ONLY when NEW green dot appears and we're flat or waiting for green dot
def shouldGoLong = isBullishOrderBlock and bullishUnmitigated and (currentPosition[1] == 0 or waitingForGreenDot[1] == 1);

# Rule 2: Exit long and go short when red dot appears (close below Bullish Order Block)
def shouldExitLongGoShort = closeBelowBullish and !redDotPlotted[1] and currentPosition[1] == 1;

# Rule 3: Exit short and go long when price hits the green dot level (but only if we're waiting for it)
def shouldExitShortGoLong = currentPosition[1] == -1 and high1 >= lastGreenDotLevel[1] and waitingForGreenDot[1] == 1;

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

# --- Plot Waiting States ---
plot WaitingForRed = if waitingForRedDot == 1 then high1 + 0.5 else Double.NaN;
WaitingForRed.SetDefaultColor(Color.ORANGE);
WaitingForRed.SetStyle(Curve.POINTS);
WaitingForRed.SetLineWeight(2);

plot WaitingForGreen = if waitingForGreenDot == 1 then low1 - 0.5 else Double.NaN;
WaitingForGreen.SetDefaultColor(Color.CYAN);
WaitingForGreen.SetStyle(Curve.POINTS);
WaitingForGreen.SetLineWeight(2);

# --- Strategy Orders ---
# Go long ONLY when NEW green dot appears
AddOrder(OrderType.BUY_TO_OPEN, shouldGoLong, close1, 100, Color.GREEN, Color.GREEN, "Long on NEW Green Dot");

# Exit long and go short when red dot appears
AddOrder(OrderType.SELL_TO_CLOSE, shouldExitLongGoShort, close1, 100, Color.RED, Color.RED, "Exit Long");
AddOrder(OrderType.SELL_TO_OPEN, shouldExitLongGoShort, close1, 100, Color.RED, Color.RED, "Short on Red Dot");

# Exit short and go long when price hits green dot level
AddOrder(OrderType.BUY_TO_CLOSE, shouldExitShortGoLong, lastGreenDotLevel, 100, Color.GREEN, Color.GREEN, "Exit Short");
AddOrder(OrderType.BUY_TO_OPEN, shouldExitShortGoLong, lastGreenDotLevel, 100, Color.GREEN, Color.GREEN, "Long on Green Level");

# --- Performance Labels ---
AddLabel(yes, "Position: " + (if currentPosition == 1 then "LONG" else if currentPosition == -1 then "SHORT" else "FLAT"), 
         if currentPosition == 1 then Color.GREEN else if currentPosition == -1 then Color.RED else Color.GRAY);
AddLabel(yes, "Green Level: $" + Round(lastGreenDotLevel, 2), Color.GREEN);
AddLabel(yes, "Red Level: $" + Round(lastRedDotLevel, 2), Color.RED);
AddLabel(yes, "Waiting: " + (if waitingForRedDot == 1 then "RED DOT" else if waitingForGreenDot == 1 then "GREEN LEVEL" else "NONE"), 
         if waitingForRedDot == 1 then Color.ORANGE else if waitingForGreenDot == 1 then Color.CYAN else Color.GRAY);

# --- Alerts ---
Alert(shouldGoLong, "NEW Green Dot - Enter LONG", Alert.BAR, Sound.Bell);
Alert(shouldExitLongGoShort, "Red Dot - Exit LONG, Enter SHORT", Alert.BAR, Sound.Ding);
Alert(shouldExitShortGoLong, "Hit Green Level - Exit SHORT, Enter LONG", Alert.BAR, Sound.Chimes);