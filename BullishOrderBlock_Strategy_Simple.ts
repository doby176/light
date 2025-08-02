# Bullish Order Block Auto-Trading Strategy for ThinkorSwim
# Simplified version for Strategies tab
# Implements automatic long/short cycling

# Input parameters
input symbol = "QQQ";
input enableShorting = yes;
input autoCycle = yes;
input stopLossPercent = 1.0;
input maxDailyLoss = 5.0;

# Strategy variables
def currentPosition = 0;  # 0=flat, 1=long, -1=short
def entryPrice = 0.0;
def stopLossPrice = 0.0;
def lastBullishLevel = 0.0;
def dailyPnL = 0.0;
def totalPnL = 0.0;
def tradeCount = 0;
def winCount = 0;

# Bullish Order Block Detection
def inefficiency = AbsValue(high[1] - low) > AbsValue(close[1] - open[1]) * 1.5;
def bosUp = high > Highest(high[2], 3);
def chochUp = low < Lowest(low[2], 3) and high > Highest(high[2], 3);
def isBullishOrderBlock = inefficiency[1] and (bosUp or chochUp) and !IsNaN(close[1]);

# Track order block level
def bullishOrderBlockLevel = if isBullishOrderBlock then open[1] else Double.NaN;
def bullishUnmitigated = if isBullishOrderBlock then 1 else if close < GetValue(low, 1) and GetValue(isBullishOrderBlock, 1) then 0 else bullishUnmitigated[1];

# Update last bullish level
def lastBullishLevel = if isBullishOrderBlock then open[1] else lastBullishLevel[1];

# Detect red dot (price closes below order block)
def closeBelowBullish = close < lastBullishLevel and !IsNaN(lastBullishLevel) and bullishUnmitigated[1];

# Strategy logic
def shouldEnterLong = currentPosition == 0 and isBullishOrderBlock and bullishUnmitigated;
def shouldExitLongEnterShort = currentPosition == 1 and closeBelowBullish;
def shouldExitShortEnterLong = currentPosition == -1 and high >= lastBullishLevel;
def dailyLossExceeded = dailyPnL < -maxDailyLoss;

# Position management
if shouldEnterLong and !dailyLossExceeded {
    currentPosition = 1;
    entryPrice = close;
    stopLossPrice = entryPrice * (1 - stopLossPercent / 100);
    lastBullishLevel = bullishOrderBlockLevel;
    
    AddOrder(OrderType.BUY_TO_OPEN, symbol, 1, name = "Long Entry");
}

if shouldExitLongEnterShort and enableShorting {
    def longPnL = (close - entryPrice) / entryPrice * 100;
    totalPnL += longPnL;
    dailyPnL += longPnL;
    tradeCount += 1;
    if longPnL > 0 then winCount += 1;
    
    currentPosition = 0;
    AddOrder(OrderType.SELL_TO_CLOSE, symbol, 1, name = "Long Exit");
    
    if autoCycle {
        currentPosition = -1;
        entryPrice = close;
        stopLossPrice = lastBullishLevel;
        
        AddOrder(OrderType.SELL_TO_OPEN, symbol, 1, name = "Short Entry");
    }
}

if shouldExitShortEnterLong and autoCycle {
    def shortPnL = (entryPrice - lastBullishLevel) / entryPrice * 100;
    totalPnL += shortPnL;
    dailyPnL += shortPnL;
    tradeCount += 1;
    if shortPnL > 0 then winCount += 1;
    
    currentPosition = 0;
    AddOrder(OrderType.BUY_TO_CLOSE, symbol, 1, name = "Short Exit");
    
    currentPosition = 1;
    entryPrice = lastBullishLevel;
    stopLossPrice = entryPrice * (1 - stopLossPercent / 100);
    
    AddOrder(OrderType.BUY_TO_OPEN, symbol, 1, name = "Long Entry");
}

# Stop loss checks
if currentPosition == 1 and low <= stopLossPrice {
    def stopLossPnL = (stopLossPrice - entryPrice) / entryPrice * 100;
    totalPnL += stopLossPnL;
    dailyPnL += stopLossPnL;
    tradeCount += 1;
    
    currentPosition = 0;
    AddOrder(OrderType.SELL_TO_CLOSE, symbol, 1, name = "Stop Loss");
}

if currentPosition == -1 and high >= stopLossPrice {
    def stopLossPnL = (entryPrice - stopLossPrice) / entryPrice * 100;
    totalPnL += stopLossPnL;
    dailyPnL += stopLossPnL;
    tradeCount += 1;
    
    currentPosition = 0;
    AddOrder(OrderType.BUY_TO_CLOSE, symbol, 1, name = "Stop Loss");
}

# Reset daily P&L
def isNewDay = GetDay() != GetDay()[1];
if isNewDay {
    dailyPnL = 0;
}

# Performance display
def winRate = if tradeCount > 0 then winCount / tradeCount * 100 else 0;

AddLabel(yes, "Position: " + (if currentPosition == 1 then "LONG" else if currentPosition == -1 then "SHORT" else "FLAT"), 
         if currentPosition == 1 then Color.GREEN else if currentPosition == -1 then Color.RED else Color.GRAY);
AddLabel(yes, "Total P&L: " + Round(totalPnL, 2) + "%", 
         if totalPnL > 0 then Color.GREEN else if totalPnL < 0 then Color.RED else Color.GRAY);
AddLabel(yes, "Daily P&L: " + Round(dailyPnL, 2) + "%", 
         if dailyPnL > 0 then Color.GREEN else if dailyPnL < 0 then Color.RED else Color.GRAY);
AddLabel(yes, "Trades: " + tradeCount + " | Win Rate: " + Round(winRate, 1) + "%", 
         if winRate > 50 then Color.GREEN else Color.RED);

# Alerts
Alert(isBullishOrderBlock and bullishUnmitigated, "Bullish Order Block - Enter LONG", Alert.BAR, Sound.Bell);
Alert(closeBelowBullish, "Price Below Order Block - Exit LONG, Enter SHORT", Alert.BAR, Sound.Ding);
Alert(shouldExitShortEnterLong, "Price at Order Block Level - Exit SHORT, Enter LONG", Alert.BAR, Sound.Chimes);