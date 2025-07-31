# QQQ Gap Analysis Indicator
# Based on 1MChart historical gap analysis data (1929 records from 2015-2024)
# Provides gap fill probability and price targets

# Input parameters
input showLabels = yes;
input showPriceTargets = yes;
input showProbability = yes;
input showAverageTargets = yes;

# Get daily open and close for gap calculations (regardless of current chart timeframe)
def dailyOpen = GetValue(open, 0, 1);  # Daily open
def dailyClose = GetValue(close, 0, 1);  # Daily close
def prevDailyClose = GetValue(close, 1, 1);  # Previous day's close

# Calculate gap based on daily open vs previous close
def gapValue = dailyOpen - prevDailyClose;
def gapPercentage = (gapValue / prevDailyClose) * 100;
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

# Gap Fill Rates by bin, day, direction - Using conditional logic
def currentGapFillRate = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 58.1 else 82.5
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 69.1 else 76.1
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 73.9 else 77.1
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 80.0 else 78.6
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 70.1 else 81.2
        else 65.0
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 48.8 else 51.5
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 70.5 else 59.3
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 69.2 else 60.0
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 60.0 else 63.9
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 47.9 else 59.5
        else 55.0
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 40.3 else 44.0
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 52.5 else 38.9
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 44.4 else 55.8
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 43.7 else 65.2
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 45.7 else 48.0
        else 45.0
    else if gapSizeBin == 4 then # Bin 4 (1-1.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 18.2 else 27.8
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 33.3 else 40.0
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 28.6 else 60.0
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 28.6 else 14.3
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 35.0 else 25.0
        else 30.0
    else if gapSizeBin == 5 then # Bin 5 (1.5%+)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 16.7 else 25.0
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 31.8 else 25.0
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 11.1 else 31.8
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 16.7 else 22.7
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 30.8 else 10.0
        else 20.0
    else 50.0; # Default

# Median moves before fill (percentage) - Real data from filled gaps
def currentMedianMove = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.11 else 0.12
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.16 else 0.15
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.17 else 0.19
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.17 else 0.37
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.21 else 0.11
        else 0.15
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.14 else 0.28
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.26 else 0.14
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.18 else 0.18
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.26 else 0.32
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.02 else 0.26
        else 0.20
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.25 else 0.27
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.32 else 0.32
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.04 else 0.19
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.15 else 0.18
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.24 else 0.13
        else 0.20
    else if gapSizeBin == 4 then # Bin 4 (1-1.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.01 else 0.00
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 1.01 else 0.00
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 2.17 else 0.00
        else 0.50
    else if gapSizeBin == 5 then # Bin 5 (1.5%+)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.00 else 0.03
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.00 else 1.34
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.11 else 0.00
        else 0.50
    else 0.25; # Default

# Average moves before fill (percentage) - Real data from filled gaps
def currentAverageMove = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.15 else 0.18
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.22 else 0.21
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.24 else 0.25
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.23 else 0.42
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.28 else 0.16
        else 0.20
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.19 else 0.32
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.31 else 0.18
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.23 else 0.22
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.31 else 0.37
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.05 else 0.31
        else 0.25
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.30 else 0.32
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.38 else 0.37
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.08 else 0.24
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.20 else 0.23
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.29 else 0.18
        else 0.25
    else if gapSizeBin == 4 then # Bin 4 (1-1.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.02 else 0.00
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 1.15 else 0.00
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 2.45 else 0.00
        else 0.60
    else if gapSizeBin == 5 then # Bin 5 (1.5%+)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.00 else 0.05
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.00 else 0.00
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.00 else 1.52
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.15 else 0.00
        else 0.60
    else 0.30; # Default

# Median max moves for unfilled gaps - Real data from unfilled gaps
def currentMaxMoveUnfilled = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.37 else 0.31
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.33 else 0.29
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.28 else 0.41
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.27 else 0.36
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.42 else 0.40
        else 0.35
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.49 else 0.41
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.46 else 0.32
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.29 else 0.40
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.31 else 0.33
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.34 else 0.37
        else 0.40
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.35 else 0.45
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.39 else 0.39
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.22 else 0.37
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.26 else 0.48
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.29 else 0.42
        else 0.40
    else if gapSizeBin == 4 then # Bin 4 (1-1.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.41 else 0.40
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.52 else 0.32
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.44 else 0.29
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.24 else 0.52
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.51 else 0.37
        else 0.45
    else if gapSizeBin == 5 then # Bin 5 (1.5%+)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.18 else 0.39
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.41 else 0.36
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.44 else 0.40
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.48 else 0.26
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.48 else 0.26
        else 0.40
    else 0.30; # Default

# Average max moves for unfilled gaps - Real data from unfilled gaps
def currentAverageMaxUnfilled = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.42 else 0.36
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.38 else 0.34
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.33 else 0.46
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.32 else 0.41
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.47 else 0.45
        else 0.40
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.54 else 0.46
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.51 else 0.37
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.34 else 0.45
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.36 else 0.38
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.39 else 0.42
        else 0.45
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.40 else 0.50
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.44 else 0.44
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.27 else 0.42
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.31 else 0.53
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.34 else 0.47
        else 0.45
    else if gapSizeBin == 4 then # Bin 4 (1-1.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.46 else 0.45
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.57 else 0.37
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.49 else 0.34
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.29 else 0.57
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.56 else 0.42
        else 0.50
    else if gapSizeBin == 5 then # Bin 5 (1.5%+)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.23 else 0.44
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.46 else 0.41
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.49 else 0.45
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.53 else 0.31
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.53 else 0.31
        else 0.45
    else 0.35; # Default

# Calculate price targets based on historical patterns
def entryPrice = dailyOpen;

# Median target prices
def medianExitPrice = if gapDirection == 1 then 
                         dailyOpen * (1 + currentMedianMove / 100)
                      else 
                         dailyOpen * (1 - currentMedianMove / 100);

# Average target prices
def averageExitPrice = if gapDirection == 1 then 
                         dailyOpen * (1 + currentAverageMove / 100)
                      else 
                         dailyOpen * (1 - currentAverageMove / 100);

# Stop loss prices (median and average)
def medianStopLossPrice = if gapDirection == 1 then 
                            dailyOpen * (1 - currentMaxMoveUnfilled / 100)
                         else 
                            dailyOpen * (1 + currentMaxMoveUnfilled / 100);

def averageStopLossPrice = if gapDirection == 1 then 
                             dailyOpen * (1 - currentAverageMaxUnfilled / 100)
                          else 
                             dailyOpen * (1 + currentAverageMaxUnfilled / 100);

# Risk/Reward calculations
def medianRiskRewardRatio = AbsValue((medianExitPrice - entryPrice) / (entryPrice - medianStopLossPrice));
def averageRiskRewardRatio = AbsValue((averageExitPrice - entryPrice) / (entryPrice - averageStopLossPrice));

# Plot price targets as horizontal lines on main chart
# Entry line (white)
plot entryLine = if showPriceTargets then entryPrice else Double.NaN;
entryLine.SetPaintingStrategy(PaintingStrategy.LINE);
entryLine.SetLineWeight(2);
entryLine.AssignValueColor(Color.WHITE);

# Median target line (green for long, red for short)
plot medianTargetLine = if showPriceTargets then medianExitPrice else Double.NaN;
medianTargetLine.SetPaintingStrategy(PaintingStrategy.LINE);
medianTargetLine.SetLineWeight(3);
medianTargetLine.AssignValueColor(if gapDirection == 1 then Color.RED else Color.GREEN);

# Average target line (lighter green for long, lighter red for short)
plot averageTargetLine = if showPriceTargets and showAverageTargets then averageExitPrice else Double.NaN;
averageTargetLine.SetPaintingStrategy(PaintingStrategy.LINE);
averageTargetLine.SetLineWeight(2);
averageTargetLine.AssignValueColor(if gapDirection == 1 then Color.DARK_RED else Color.DARK_GREEN);

# Median stop loss line (orange)
plot medianStopLine = if showPriceTargets then medianStopLossPrice else Double.NaN;
medianStopLine.SetPaintingStrategy(PaintingStrategy.LINE);
medianStopLine.SetLineWeight(3);
medianStopLine.AssignValueColor(Color.ORANGE);

# Average stop loss line (lighter orange)
plot averageStopLine = if showPriceTargets and showAverageTargets then averageStopLossPrice else Double.NaN;
averageStopLine.SetPaintingStrategy(PaintingStrategy.LINE);
averageStopLine.SetLineWeight(2);
averageStopLine.AssignValueColor(Color.DARK_ORANGE);

# Add informative labels
AddLabel(showLabels, "Gap: " + Round(gapPercentage, 2) + "% " + (if gapDirection == 1 then "UP" else "DOWN"), if gapDirection == 1 then Color.RED else Color.GREEN);
AddLabel(showProbability, "Fill Prob: " + Round(currentGapFillRate, 1) + "%", if currentGapFillRate > 60 then Color.GREEN else if currentGapFillRate > 50 then Color.YELLOW else Color.RED);

# Price target labels
AddLabel(showPriceTargets, "Entry: $" + Round(entryPrice, 2), Color.WHITE);
AddLabel(showPriceTargets, "Median Target: $" + Round(medianExitPrice, 2), if gapDirection == 1 then Color.RED else Color.GREEN);
AddLabel(showPriceTargets and showAverageTargets, "Avg Target: $" + Round(averageExitPrice, 2), if gapDirection == 1 then Color.DARK_RED else Color.DARK_GREEN);
AddLabel(showPriceTargets, "Median Stop: $" + Round(medianStopLossPrice, 2), Color.ORANGE);
AddLabel(showPriceTargets and showAverageTargets, "Avg Stop: $" + Round(averageStopLossPrice, 2), Color.DARK_ORANGE);

# Risk/Reward labels
AddLabel(showPriceTargets, "Median R/R: " + Round(medianRiskRewardRatio, 2), if medianRiskRewardRatio > 2 then Color.GREEN else Color.YELLOW);
AddLabel(showPriceTargets and showAverageTargets, "Avg R/R: " + Round(averageRiskRewardRatio, 2), if averageRiskRewardRatio > 2 then Color.GREEN else Color.YELLOW);

# Add data source label
AddLabel(yes, "1MChart Data (1929 records)", Color.CYAN);

# Alert conditions for high probability setups
Alert(currentGapFillRate > 70 and gapDirection == 1, "High Probability Gap Up Fill (>70%)", Alert.BAR, Sound.DING);
Alert(currentGapFillRate > 70 and gapDirection == -1, "High Probability Gap Down Fill (>70%)", Alert.BAR, Sound.DING);
Alert(currentGapFillRate < 30 and gapDirection == 1, "Low Probability Gap Up (<30%) - Consider Short", Alert.BAR, Sound.DING);
Alert(currentGapFillRate < 30 and gapDirection == -1, "Low Probability Gap Down (<30%) - Consider Long", Alert.BAR, Sound.DING);