# QQQ Gap Analysis Indicator - Manual Input Version
# Based on 1MChart historical gap analysis data (1929 records from 2015-2024)
# Manual input version for use on any timeframe (1min, 5min, etc.)

# Manual input parameters for daily data
input dailyOpenPrice = 0.0;
input previousDailyClose = 0.0;
input showLabels = yes;
input showPriceTargets = yes;
input showProbability = yes;
input showAverageTargets = yes;

# Calculate gap based on manually input daily open vs previous close
def gapValue = dailyOpenPrice - previousDailyClose;
def gapPercentage = (gapValue / previousDailyClose) * 100;
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

# ZONE 1: SHORT/LONG zone - Move before gap fill (median and average)
def moveBeforeFillMedian = 
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

def moveBeforeFillAverage = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.19 else 0.20
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.19 else 0.19
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.29 else 0.28
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.33 else 0.33
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.31 else 0.17
        else 0.20
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.17 else 0.36
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.34 else 0.29
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.19 else 0.20
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.33 else 0.38
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.03 else 0.34
        else 0.25
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.24 else 0.30
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.30 else 0.31
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.18 else 0.29
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.27 else 0.20
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.47 else 0.19
        else 0.25
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
        else 0.60
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
        else 0.60
    else 0.30; # Default

# ZONE 2: STOP out zone - Move on unfilled gaps (median and average)
def moveOnUnfilledGapMedian = 
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

def moveOnUnfilledGapAverage = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.42 else 0.39
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.40 else 0.40
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.31 else 0.46
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.34 else 0.42
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.39 else 0.39
        else 0.40
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.48 else 0.46
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.46 else 0.34
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.26 else 0.41
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.39 else 0.37
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.33 else 0.50
        else 0.45
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.40 else 0.49
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.35 else 0.49
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.32 else 0.47
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.33 else 0.46
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.34 else 0.49
        else 0.45
    else if gapSizeBin == 4 then # Bin 4 (1-1.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.38 else 0.43
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.53 else 0.35
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.48 else 0.34
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.29 else 0.62
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.48 else 0.31
        else 0.50
    else if gapSizeBin == 5 then # Bin 5 (1.5%+)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.31 else 0.47
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.57 else 0.51
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.43 else 0.44
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.44 else 0.42
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.53 else 0.43
        else 0.45
    else 0.35; # Default

# ZONE 3: LONG/SHORT zone - Move after gap fill (median and average)
def moveAfterFillMedian = 
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

def moveAfterFillAverage = 
    if gapSizeBin == 1 then # Bin 1 (0.15-0.35%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.19 else 0.20
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.19 else 0.19
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.29 else 0.28
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.33 else 0.33
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.31 else 0.17
        else 0.20
    else if gapSizeBin == 2 then # Bin 2 (0.35-0.5%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.17 else 0.36
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.34 else 0.29
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.19 else 0.20
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.33 else 0.38
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.03 else 0.34
        else 0.25
    else if gapSizeBin == 3 then # Bin 3 (0.5-1%)
        if dayOfWeek == 0 then # Monday
            if gapDirection == 1 then 0.24 else 0.30
        else if dayOfWeek == 1 then # Tuesday
            if gapDirection == 1 then 0.30 else 0.31
        else if dayOfWeek == 2 then # Wednesday
            if gapDirection == 1 then 0.18 else 0.29
        else if dayOfWeek == 3 then # Thursday
            if gapDirection == 1 then 0.27 else 0.20
        else if dayOfWeek == 4 then # Friday
            if gapDirection == 1 then 0.47 else 0.19
        else 0.25
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
        else 0.60
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
        else 0.60
    else 0.30; # Default

# Calculate price targets based on historical patterns
# ZONE 1: SHORT/LONG zone prices (move before gap fill)
def shortLongZoneMedian = if gapDirection == 1 then 
                            dailyOpenPrice * (1 + moveBeforeFillMedian / 100)
                         else 
                            dailyOpenPrice * (1 - moveBeforeFillMedian / 100);

def shortLongZoneAverage = if gapDirection == 1 then 
                             dailyOpenPrice * (1 + moveBeforeFillAverage / 100)
                          else 
                             dailyOpenPrice * (1 - moveBeforeFillAverage / 100);

# ZONE 2: STOP out zone prices (move on unfilled gaps)
def stopOutZoneMedian = if gapDirection == 1 then 
                          dailyOpenPrice * (1 - moveOnUnfilledGapMedian / 100)
                       else 
                          dailyOpenPrice * (1 + moveOnUnfilledGapMedian / 100);

def stopOutZoneAverage = if gapDirection == 1 then 
                           dailyOpenPrice * (1 - moveOnUnfilledGapAverage / 100)
                        else 
                           dailyOpenPrice * (1 + moveOnUnfilledGapAverage / 100);

# ZONE 3: LONG/SHORT zone prices (move after gap fill)
def longShortZoneMedian = if gapDirection == 1 then 
                            dailyOpenPrice * (1 - moveAfterFillMedian / 100)
                         else 
                            dailyOpenPrice * (1 + moveAfterFillMedian / 100);

def longShortZoneAverage = if gapDirection == 1 then 
                             dailyOpenPrice * (1 - moveAfterFillAverage / 100)
                          else 
                             dailyOpenPrice * (1 + moveAfterFillAverage / 100);

# Only show data if manual inputs are provided
def hasValidInputs = dailyOpenPrice > 0 and previousDailyClose > 0;

# Plot price targets as horizontal lines on main chart
# ZONE 1: SHORT/LONG zone lines (green for long, red for short)
plot shortLongZoneMedianLine = if showPriceTargets and hasValidInputs then shortLongZoneMedian else Double.NaN;
shortLongZoneMedianLine.SetPaintingStrategy(PaintingStrategy.LINE);
shortLongZoneMedianLine.SetLineWeight(3);
shortLongZoneMedianLine.AssignValueColor(if gapDirection == 1 then Color.RED else Color.GREEN);

plot shortLongZoneAverageLine = if showPriceTargets and showAverageTargets and hasValidInputs then shortLongZoneAverage else Double.NaN;
shortLongZoneAverageLine.SetPaintingStrategy(PaintingStrategy.LINE);
shortLongZoneAverageLine.SetLineWeight(2);
shortLongZoneAverageLine.AssignValueColor(if gapDirection == 1 then Color.DARK_RED else Color.DARK_GREEN);

# ZONE 2: STOP out zone lines (orange)
plot stopOutZoneMedianLine = if showPriceTargets and hasValidInputs then stopOutZoneMedian else Double.NaN;
stopOutZoneMedianLine.SetPaintingStrategy(PaintingStrategy.LINE);
stopOutZoneMedianLine.SetLineWeight(3);
stopOutZoneMedianLine.AssignValueColor(Color.ORANGE);

plot stopOutZoneAverageLine = if showPriceTargets and showAverageTargets and hasValidInputs then stopOutZoneAverage else Double.NaN;
stopOutZoneAverageLine.SetPaintingStrategy(PaintingStrategy.LINE);
stopOutZoneAverageLine.SetLineWeight(2);
stopOutZoneAverageLine.AssignValueColor(Color.DARK_ORANGE);

# ZONE 3: LONG/SHORT zone lines (green for long, red for short)
plot longShortZoneMedianLine = if showPriceTargets and hasValidInputs then longShortZoneMedian else Double.NaN;
longShortZoneMedianLine.SetPaintingStrategy(PaintingStrategy.LINE);
longShortZoneMedianLine.SetLineWeight(3);
longShortZoneMedianLine.AssignValueColor(if gapDirection == 1 then Color.GREEN else Color.RED);

plot longShortZoneAverageLine = if showPriceTargets and showAverageTargets and hasValidInputs then longShortZoneAverage else Double.NaN;
longShortZoneAverageLine.SetPaintingStrategy(PaintingStrategy.LINE);
longShortZoneAverageLine.SetLineWeight(2);
longShortZoneAverageLine.AssignValueColor(if gapDirection == 1 then Color.DARK_GREEN else Color.DARK_RED);

# Alert conditions for high probability setups
Alert(hasValidInputs and currentGapFillRate > 70 and gapDirection == 1, "High Probability Gap Up Fill (>70%)", Alert.BAR, Sound.DING);
Alert(hasValidInputs and currentGapFillRate > 70 and gapDirection == -1, "High Probability Gap Down Fill (>70%)", Alert.BAR, Sound.DING);
Alert(hasValidInputs and currentGapFillRate < 30 and gapDirection == 1, "Low Probability Gap Up (<30%) - Consider Short", Alert.BAR, Sound.DING);
Alert(hasValidInputs and currentGapFillRate < 30 and gapDirection == -1, "Low Probability Gap Down (<30%) - Consider Long", Alert.BAR, Sound.DING);