# Bullish Order Block Auto-Trading Strategy for ThinkorSwim
# Fixed version with proper ThinkScript syntax
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

# Position management - using proper ThinkScript syntax
def newPosition = if shouldEnterLong and !dailyLossExceeded then 1
                  else if shouldExitLongEnterShort and enableShorting then -1
                  else if shouldExitShortEnterLong and autoCycle then 1
                  else currentPosition;

def newEntryPrice = if shouldEnterLong and !dailyLossExceeded then close
                    else if shouldExitLongEnterShort and enableShorting then close
                    else if shouldExitShortEnterLong and autoCycle then lastBullishLevel
                    else entryPrice;

def newStopLossPrice = if shouldEnterLong and !dailyLossExceeded then close * (1 - stopLossPercent / 100)
                       else if shouldExitLongEnterShort and enableShorting then lastBullishLevel
                       else if shouldExitShortEnterLong and autoCycle then lastBullishLevel * (1 - stopLossPercent / 100)
                       else stopLossPrice;

# Update variables
currentPosition = newPosition;
entryPrice = newEntryPrice;
stopLossPrice = newStopLossPrice;

# Calculate P&L for completed trades
def longPnL = if shouldExitLongEnterShort and enableShorting then (close - entryPrice) / entryPrice * 100 else 0;
def shortPnL = if shouldExitShortEnterLong and autoCycle then (entryPrice - lastBullishLevel) / entryPrice * 100 else 0;

# Update performance metrics
def newTotalPnL = totalPnL + longPnL + shortPnL;
def newDailyPnL = dailyPnL + longPnL + shortPnL;
def newTradeCount = tradeCount + (if longPnL != 0 or shortPnL != 0 then 1 else 0);
def newWinCount = winCount + (if longPnL > 0 or shortPnL > 0 then 1 else 0);

totalPnL = newTotalPnL;
dailyPnL = newDailyPnL;
tradeCount = newTradeCount;
winCount = newWinCount;

# Reset daily P&L
def isNewDay = GetDay() != GetDay()[1];
dailyPnL = if isNewDay then 0 else dailyPnL;

# Performance display
def winRate = if tradeCount > 0 then winCount / tradeCount * 100 else 0;

# Add labels for performance display
AddLabel(yes, "Position: " + (if currentPosition == 1 then "LONG" else if currentPosition == -1 then "SHORT" else "FLAT"), 
         if currentPosition == 1 then Color.GREEN else if currentPosition == -1 then Color.RED else Color.GRAY);
AddLabel(yes, "Total P&L: " + Round(totalPnL, 2) + "%", 
         if totalPnL > 0 then Color.GREEN else if totalPnL < 0 then Color.RED else Color.GRAY);
AddLabel(yes, "Daily P&L: " + Round(dailyPnL, 2) + "%", 
         if dailyPnL > 0 then Color.GREEN else if dailyPnL < 0 then Color.RED else Color.GRAY);
AddLabel(yes, "Trades: " + tradeCount + " | Win Rate: " + Round(winRate, 1) + "%", 
         if winRate > 50 then Color.GREEN else Color.RED);

# Plot signals
plot BullishOrderBlock = if isBullishOrderBlock and bullishUnmitigated then bullishOrderBlockLevel else Double.NaN;
BullishOrderBlock.SetDefaultColor(Color.LIGHT_GREEN);
BullishOrderBlock.SetStyle(Curve.POINTS);
BullishOrderBlock.SetLineWeight(3);

plot RedDot = if closeBelowBullish then close else Double.NaN;
RedDot.SetDefaultColor(Color.RED);
RedDot.SetStyle(Curve.POINTS);
RedDot.SetLineWeight(3);

plot Position = currentPosition;
Position.SetDefaultColor(Color.YELLOW);
Position.SetStyle(Curve.LINE);
Position.SetLineWeight(2);

plot StopLoss = if currentPosition != 0 then stopLossPrice else Double.NaN;
StopLoss.SetDefaultColor(Color.RED);
StopLoss.SetStyle(Curve.LINE);
StopLoss.SetLineWeight(1);

# Alerts
Alert(isBullishOrderBlock and bullishUnmitigated, "Bullish Order Block - Enter LONG", Alert.BAR, Sound.Bell);
Alert(closeBelowBullish, "Price Below Order Block - Exit LONG, Enter SHORT", Alert.BAR, Sound.Ding);
Alert(shouldExitShortEnterLong, "Price at Order Block Level - Exit SHORT, Enter LONG", Alert.BAR, Sound.Chimes);