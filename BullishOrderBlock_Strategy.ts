# Bullish Order Block Auto-Trading Strategy for ThinkorSwim
# Designed for 1-minute chart
# Implements automatic long/short cycling based on order block detection
# Add this to the Strategies tab in ThinkorSwim

declare lower;

# Input parameters
input symbol = "QQQ";
input initialCapital = 10000.0;
input positionSize = 0.1;  # 10% of capital per trade
input enableShorting = yes;
input autoCycle = yes;
input stopLossPercent = 1.0;  # 1% stop loss
input maxDailyLoss = 5.0;     # 5% max daily loss
input maxWeeklyLoss = 15.0;   # 15% max weekly loss

# Strategy variables
def currentPosition = 0;  # 0=flat, 1=long, -1=short
def entryPrice = 0.0;
def stopLossPrice = 0.0;
def lastBullishLevel = 0.0;
def redDotPlotted = no;
def dailyPnL = 0.0;
def weeklyPnL = 0.0;
def totalPnL = 0.0;
def tradeCount = 0;
def winCount = 0;

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

# --- Strategy Logic ---

# Check if we should enter LONG (green dot detected)
def shouldEnterLong = currentPosition == 0 and isBullishOrderBlock and bullishUnmitigated;

# Check if we should exit LONG and enter SHORT (red dot detected)
def shouldExitLongEnterShort = currentPosition == 1 and closeBelowBullish and !redDotPlotted[1];

# Check if we should exit SHORT and enter LONG (stop at green dot level)
def shouldExitShortEnterLong = currentPosition == -1 and high1 >= lastBullishLevel;

# Check daily/weekly loss limits
def dailyLossExceeded = dailyPnL < -maxDailyLoss;
def weeklyLossExceeded = weeklyPnL < -maxWeeklyLoss;

# --- Position Management ---

# Enter LONG position
if shouldEnterLong and !dailyLossExceeded and !weeklyLossExceeded {
    currentPosition = 1;
    entryPrice = close1;
    stopLossPrice = entryPrice * (1 - stopLossPercent / 100);
    lastBullishLevel = bullishOrderBlockLevel;
    redDotPlotted = 0;
    
    # Log trade
    AddOrder(OrderType.BUY_TO_OPEN, symbol, 1, name = "Long Entry");
    print("LONG ENTRY: Price=" + entryPrice + ", Stop=" + stopLossPrice);
}

# Exit LONG and Enter SHORT
if shouldExitLongEnterShort and enableShorting {
    # Calculate P&L for long position
    def longPnL = (close1 - entryPrice) / entryPrice * 100;
    totalPnL += longPnL;
    dailyPnL += longPnL;
    weeklyPnL += longPnL;
    tradeCount += 1;
    if longPnL > 0 then winCount += 1;
    
    # Close long position
    currentPosition = 0;
    AddOrder(OrderType.SELL_TO_CLOSE, symbol, 1, name = "Long Exit");
    print("LONG EXIT: Price=" + close1 + ", P&L=" + longPnL + "%");
    
    # Enter short position
    if autoCycle {
        currentPosition = -1;
        entryPrice = close1;
        stopLossPrice = lastBullishLevel;
        
        AddOrder(OrderType.SELL_TO_OPEN, symbol, 1, name = "Short Entry");
        print("SHORT ENTRY: Price=" + entryPrice + ", Stop=" + stopLossPrice);
    }
}

# Exit SHORT and Enter LONG
if shouldExitShortEnterLong and autoCycle {
    # Calculate P&L for short position
    def shortPnL = (entryPrice - lastBullishLevel) / entryPrice * 100;
    totalPnL += shortPnL;
    dailyPnL += shortPnL;
    weeklyPnL += shortPnL;
    tradeCount += 1;
    if shortPnL > 0 then winCount += 1;
    
    # Close short position
    currentPosition = 0;
    AddOrder(OrderType.BUY_TO_CLOSE, symbol, 1, name = "Short Exit");
    print("SHORT EXIT: Price=" + lastBullishLevel + ", P&L=" + shortPnL + "%");
    
    # Enter long position
    currentPosition = 1;
    entryPrice = lastBullishLevel;
    stopLossPrice = entryPrice * (1 - stopLossPercent / 100);
    
    AddOrder(OrderType.BUY_TO_OPEN, symbol, 1, name = "Long Entry");
    print("LONG ENTRY: Price=" + entryPrice + ", Stop=" + stopLossPrice);
}

# Check stop loss
if currentPosition == 1 and low1 <= stopLossPrice {
    def stopLossPnL = (stopLossPrice - entryPrice) / entryPrice * 100;
    totalPnL += stopLossPnL;
    dailyPnL += stopLossPnL;
    weeklyPnL += stopLossPnL;
    tradeCount += 1;
    
    currentPosition = 0;
    AddOrder(OrderType.SELL_TO_CLOSE, symbol, 1, name = "Stop Loss");
    print("STOP LOSS: Price=" + stopLossPrice + ", P&L=" + stopLossPnL + "%");
}

if currentPosition == -1 and high1 >= stopLossPrice {
    def stopLossPnL = (entryPrice - stopLossPrice) / entryPrice * 100;
    totalPnL += stopLossPnL;
    dailyPnL += stopLossPnL;
    weeklyPnL += stopLossPnL;
    tradeCount += 1;
    
    currentPosition = 0;
    AddOrder(OrderType.BUY_TO_CLOSE, symbol, 1, name = "Stop Loss");
    print("STOP LOSS: Price=" + stopLossPrice + ", P&L=" + stopLossPnL + "%");
}

# Reset daily P&L at market open
def isNewDay = GetDay() != GetDay()[1];
if isNewDay {
    dailyPnL = 0;
}

# Reset weekly P&L at week start
def isNewWeek = GetWeek() != GetWeek()[1];
if isNewWeek {
    weeklyPnL = 0;
}

# --- Plotting ---

# Plot Bullish Order Block levels
plot BullishOrderBlock = if isBullishOrderBlock and bullishUnmitigated then bullishOrderBlockLevel else Double.NaN;
BullishOrderBlock.SetDefaultColor(Color.LIGHT_GREEN);
BullishOrderBlock.SetStyle(Curve.POINTS);
BullishOrderBlock.SetLineWeight(3);

# Plot Red Dot when Price Closes Below Last Bullish Order Block
plot RedDot = if closeBelowBullish and !redDotPlotted[1] then close1 else Double.NaN;
RedDot.SetDefaultColor(Color.RED);
RedDot.SetStyle(Curve.POINTS);
RedDot.SetLineWeight(3);

# Plot current position
plot Position = currentPosition;
Position.SetDefaultColor(Color.YELLOW);
Position.SetStyle(Curve.LINE);
Position.SetLineWeight(2);

# Plot stop loss level
plot StopLoss = if currentPosition != 0 then stopLossPrice else Double.NaN;
StopLoss.SetDefaultColor(Color.RED);
StopLoss.SetStyle(Curve.LINE);
StopLoss.SetLineWeight(1);

# --- Performance Display ---
def winRate = if tradeCount > 0 then winCount / tradeCount * 100 else 0;

# Display performance metrics
AddLabel(yes, "Position: " + (if currentPosition == 1 then "LONG" else if currentPosition == -1 then "SHORT" else "FLAT"), 
         if currentPosition == 1 then Color.GREEN else if currentPosition == -1 then Color.RED else Color.GRAY);
AddLabel(yes, "Total P&L: " + Round(totalPnL, 2) + "%", 
         if totalPnL > 0 then Color.GREEN else if totalPnL < 0 then Color.RED else Color.GRAY);
AddLabel(yes, "Daily P&L: " + Round(dailyPnL, 2) + "%", 
         if dailyPnL > 0 then Color.GREEN else if dailyPnL < 0 then Color.RED else Color.GRAY);
AddLabel(yes, "Trades: " + tradeCount + " | Win Rate: " + Round(winRate, 1) + "%", 
         if winRate > 50 then Color.GREEN else Color.RED);

# --- Alerts ---
Alert(isBullishOrderBlock and bullishUnmitigated, "Bullish Order Block - Enter LONG", Alert.BAR, Sound.Bell);
Alert(closeBelowBullish and !redDotPlotted[1], "Price Below Order Block - Exit LONG, Enter SHORT", Alert.BAR, Sound.Ding);
Alert(shouldExitShortEnterLong, "Price at Order Block Level - Exit SHORT, Enter LONG", Alert.BAR, Sound.Chimes);