# QQQ Gap Analysis Indicator
# Based on 1MChart historical gap analysis data (1929 records from 2015-2024)
# Provides gap fill probability and price targets

declare lower;

# Input parameters
input showLabels = yes;
input showPriceTargets = yes;
input showProbability = yes;

# Get current QQQ data
def currentOpen = close;
def prevClose = close[1];
def gapValue = currentOpen - prevClose;
def gapPercentage = (gapValue / prevClose) * 100;
def gapDirection = if gapValue > 0 then 1 else -1; # 1 for up, -1 for down

# Determine gap size bin
def absGap = AbsValue(gapPercentage);
def gapSizeBin = if absGap >= 0.15 and absGap < 0.35 then 1
                 else if absGap >= 0.35 and absGap < 0.5 then 2
                 else if absGap >= 0.5 and absGap < 1.0 then 3
                 else if absGap >= 1.0 and absGap < 1.5 then 4
                 else if absGap >= 1.5 then 5
                 else 1; # Default for small gaps

# Get day of week (0=Monday, 1=Tuesday, etc.)
def dayOfWeek = GetDayOfWeek(GetYYYYMMDD());

# Historical gap analysis data (extracted from 1MChart database - 1929 records)
# Real data from 2015-2024 QQQ gap analysis

# Gap Fill Rates by bin, day, direction
def gapFillRates = {
    # Bin 1 (0.15-0.35%)
    {0, 1}: 58.1, {0, -1}: 82.5,  # Monday
    {1, 1}: 69.1, {1, -1}: 76.1,  # Tuesday  
    {2, 1}: 73.9, {2, -1}: 77.1,  # Wednesday
    {3, 1}: 80.0, {3, -1}: 78.6,  # Thursday
    {4, 1}: 70.1, {4, -1}: 81.2,  # Friday
    
    # Bin 2 (0.35-0.5%)
    {0, 1}: 48.8, {0, -1}: 51.5,
    {1, 1}: 70.5, {1, -1}: 59.3,
    {2, 1}: 69.2, {2, -1}: 60.0,
    {3, 1}: 60.0, {3, -1}: 63.9,
    {4, 1}: 47.9, {4, -1}: 59.5,
    
    # Bin 3 (0.5-1%)
    {0, 1}: 40.3, {0, -1}: 44.0,
    {1, 1}: 52.5, {1, -1}: 38.9,
    {2, 1}: 44.4, {2, -1}: 55.8,
    {3, 1}: 43.7, {3, -1}: 65.2,
    {4, 1}: 45.7, {4, -1}: 48.0,
    
    # Bin 4 (1-1.5%)
    {0, 1}: 18.2, {0, -1}: 27.8,
    {1, 1}: 33.3, {1, -1}: 40.0,
    {2, 1}: 28.6, {2, -1}: 60.0,
    {3, 1}: 28.6, {3, -1}: 14.3,
    {4, 1}: 35.0, {4, -1}: 25.0,
    
    # Bin 5 (1.5%+)
    {0, 1}: 16.7, {0, -1}: 25.0,
    {1, 1}: 31.8, {1, -1}: 25.0,
    {2, 1}: 11.1, {2, -1}: 31.8,
    {3, 1}: 16.7, {3, -1}: 22.7,
    {4, 1}: 30.8, {4, -1}: 10.0
};

# Median moves before fill (percentage) - Real data from filled gaps
def medianMovesBeforeFill = {
    # Bin 1 (0.15-0.35%)
    {0, 1}: 0.11, {0, -1}: 0.12,
    {1, 1}: 0.16, {1, -1}: 0.15,
    {2, 1}: 0.17, {2, -1}: 0.19,
    {3, 1}: 0.17, {3, -1}: 0.37,
    {4, 1}: 0.21, {4, -1}: 0.11,
    
    # Bin 2 (0.35-0.5%)
    {0, 1}: 0.14, {0, -1}: 0.28,
    {1, 1}: 0.26, {1, -1}: 0.14,
    {2, 1}: 0.18, {2, -1}: 0.18,
    {3, 1}: 0.26, {3, -1}: 0.32,
    {4, 1}: 0.02, {4, -1}: 0.26,
    
    # Bin 3 (0.5-1%)
    {0, 1}: 0.25, {0, -1}: 0.27,
    {1, 1}: 0.32, {1, -1}: 0.32,
    {2, 1}: 0.04, {2, -1}: 0.19,
    {3, 1}: 0.15, {3, -1}: 0.18,
    {4, 1}: 0.24, {4, -1}: 0.13,
    
    # Bin 4 (1-1.5%)
    {0, 1}: 0.00, {0, -1}: 0.00,
    {1, 1}: 0.01, {1, -1}: 0.00,
    {2, 1}: 1.01, {2, -1}: 0.00,
    {3, 1}: 0.00, {3, -1}: 0.00,
    {4, 1}: 2.17, {4, -1}: 0.00,
    
    # Bin 5 (1.5%+)
    {0, 1}: 0.00, {0, -1}: 0.03,
    {1, 1}: 0.00, {1, -1}: 0.00,
    {2, 1}: 0.00, {2, -1}: 0.00,
    {3, 1}: 0.00, {3, -1}: 1.34,
    {4, 1}: 0.11, {4, -1}: 0.00
};

# Median max moves for unfilled gaps - Real data from unfilled gaps
def medianMaxMovesUnfilled = {
    # Bin 1 (0.15-0.35%)
    {0, 1}: 0.37, {0, -1}: 0.31,
    {1, 1}: 0.33, {1, -1}: 0.29,
    {2, 1}: 0.28, {2, -1}: 0.41,
    {3, 1}: 0.27, {3, -1}: 0.36,
    {4, 1}: 0.42, {4, -1}: 0.40,
    
    # Bin 2 (0.35-0.5%)
    {0, 1}: 0.49, {0, -1}: 0.41,
    {1, 1}: 0.46, {1, -1}: 0.32,
    {2, 1}: 0.29, {2, -1}: 0.40,
    {3, 1}: 0.31, {3, -1}: 0.33,
    {4, 1}: 0.34, {4, -1}: 0.37,
    
    # Bin 3 (0.5-1%)
    {0, 1}: 0.35, {0, -1}: 0.45,
    {1, 1}: 0.39, {1, -1}: 0.39,
    {2, 1}: 0.22, {2, -1}: 0.37,
    {3, 1}: 0.26, {3, -1}: 0.48,
    {4, 1}: 0.29, {4, -1}: 0.42,
    
    # Bin 4 (1-1.5%)
    {0, 1}: 0.41, {0, -1}: 0.40,
    {1, 1}: 0.52, {1, -1}: 0.32,
    {2, 1}: 0.44, {2, -1}: 0.29,
    {3, 1}: 0.24, {3, -1}: 0.52,
    {4, 1}: 0.51, {4, -1}: 0.37,
    
    # Bin 5 (1.5%+)
    {0, 1}: 0.18, {0, -1}: 0.39,
    {1, 1}: 0.41, {1, -1}: 0.36,
    {2, 1}: 0.44, {2, -1}: 0.40,
    {3, 1}: 0.48, {3, -1}: 0.26,
    {4, 1}: 0.48, {4, -1}: 0.26
};

# Get current gap analysis based on real historical data
def currentGapFillRate = gapFillRates[{dayOfWeek, gapDirection}];
def currentMedianMove = medianMovesBeforeFill[{dayOfWeek, gapDirection}];
def currentMaxMoveUnfilled = medianMaxMovesUnfilled[{dayOfWeek, gapDirection}];

# Calculate price targets based on historical patterns
def entryPrice = currentOpen;
def exitPrice = if gapDirection == 1 then 
                   currentOpen * (1 + currentMedianMove / 100)
                else 
                   currentOpen * (1 - currentMedianMove / 100);
def stopLossPrice = if gapDirection == 1 then 
                       currentOpen * (1 - currentMaxMoveUnfilled / 100)
                    else 
                       currentOpen * (1 + currentMaxMoveUnfilled / 100);

# Risk/Reward calculation
def riskRewardRatio = AbsValue((exitPrice - entryPrice) / (entryPrice - stopLossPrice));

# Plot gap fill probability (lower panel)
plot gapFillProb = currentGapFillRate;
gapFillProb.SetPaintingStrategy(PaintingStrategy.LINE);
gapFillProb.SetLineWeight(2);
gapFillProb.AssignValueColor(if currentGapFillRate > 60 then Color.GREEN else if currentGapFillRate > 50 then Color.YELLOW else Color.RED);

# Plot price targets as horizontal lines on main chart
plot entryLine = if showPriceTargets then entryPrice else Double.NaN;
entryLine.SetPaintingStrategy(PaintingStrategy.LINE);
entryLine.SetLineWeight(1);
entryLine.AssignValueColor(Color.WHITE);

plot exitLine = if showPriceTargets then exitPrice else Double.NaN;
exitLine.SetPaintingStrategy(PaintingStrategy.LINE);
exitLine.SetLineWeight(2);
exitLine.AssignValueColor(Color.GREEN);

plot stopLossLine = if showPriceTargets then stopLossPrice else Double.NaN;
stopLossLine.SetPaintingStrategy(PaintingStrategy.LINE);
stopLossLine.SetLineWeight(2);
stopLossLine.AssignValueColor(Color.RED);

# Add informative labels
AddLabel(showLabels, "Gap: " + Round(gapPercentage, 2) + "% " + (if gapDirection == 1 then "UP" else "DOWN"), if gapDirection == 1 then Color.GREEN else Color.RED);
AddLabel(showProbability, "Fill Prob: " + Round(currentGapFillRate, 1) + "%", if currentGapFillRate > 60 then Color.GREEN else if currentGapFillRate > 50 then Color.YELLOW else Color.RED);
AddLabel(showPriceTargets, "Entry: $" + Round(entryPrice, 2), Color.WHITE);
AddLabel(showPriceTargets, "Target: $" + Round(exitPrice, 2), Color.GREEN);
AddLabel(showPriceTargets, "Stop: $" + Round(stopLossPrice, 2), Color.RED);
AddLabel(showPriceTargets, "R/R: " + Round(riskRewardRatio, 2), if riskRewardRatio > 2 then Color.GREEN else Color.YELLOW);

# Add data source label
AddLabel(yes, "1MChart Data (1929 records)", Color.CYAN);

# Alert conditions for high probability setups
Alert(gapFillProb > 70 and gapDirection == 1, "High Probability Gap Up Fill (>70%)", Alert.BAR, Sound.DING);
Alert(gapFillProb > 70 and gapDirection == -1, "High Probability Gap Down Fill (>70%)", Alert.BAR, Sound.DING);
Alert(gapFillProb < 30 and gapDirection == 1, "Low Probability Gap Up (<30%) - Consider Short", Alert.BAR, Sound.DING);
Alert(gapFillProb < 30 and gapDirection == -1, "Low Probability Gap Down (<30%) - Consider Long", Alert.BAR, Sound.DING);