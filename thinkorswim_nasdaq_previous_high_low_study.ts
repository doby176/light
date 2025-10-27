# ThinkOrSwim NASDAQ Previous High/Low Study
# Enhanced analysis based on 1MChart website's comprehensive insights
# Provides detailed statistical analysis and trading signals

declare lower;

# Input parameters
input show_detailed_analysis = yes;
input show_statistical_comparison = yes;
input show_trading_signals = yes;
input alert_on_signals = yes;
input continuation_threshold = 0.5;
input reversal_threshold = 0.3;
input volume_threshold = 1.5;  # Volume multiplier for confirmation

# Time periods
input analysis_period_10min = 10;
input analysis_period_60min = 60;

# Calculate previous day's key levels
def prev_day_high = high(period = AggregationPeriod.DAY)[1];
def prev_day_low = low(period = AggregationPeriod.DAY)[1];
def prev_day_open = open(period = AggregationPeriod.DAY)[1];
def prev_day_close = close(period = AggregationPeriod.DAY)[1];
def prev_day_range = prev_day_high - prev_day_low;
def prev_day_midpoint = (prev_day_high + prev_day_low) / 2;

# Current day analysis
def current_open = open(period = AggregationPeriod.DAY);
def current_high = high(period = AggregationPeriod.DAY);
def current_low = low(period = AggregationPeriod.DAY);
def current_close = close;

# Determine open position relative to previous high/low
def open_position;
if current_open > prev_day_high then {
    open_position = 1;  # Above Previous High
} else if current_open < prev_day_low then {
    open_position = -1; # Below Previous Low
} else {
    open_position = 0;  # Between Previous High and Low
}

# Calculate distance from previous levels
def distance_from_high = ((current_open - prev_day_high) / prev_day_high) * 100;
def distance_from_low = ((current_open - prev_day_low) / prev_day_low) * 100;
def position_in_range = if prev_day_range > 0 then 
    ((current_open - prev_day_low) / prev_day_range) * 100 else 50;

# Time-based analysis
def time_since_open = (GetTime() - GetTime(period = AggregationPeriod.DAY)) / 1000 / 60;
def within_10min = time_since_open <= analysis_period_10min;
def within_60min = time_since_open <= analysis_period_60min;

# Volume analysis
def current_volume = volume;
def avg_volume = Average(volume, 20);
def volume_ratio = current_volume / avg_volume;
def high_volume = volume_ratio > volume_threshold;

# Touch analysis
def high_touch = high >= prev_day_high;
def low_touch = low <= prev_day_low;
def high_break = close > prev_day_high;
def low_break = close < prev_day_low;

# Calculate moves when touching previous levels
def continuation_move_10min_high = if within_10min and high_touch then 
    ((high - prev_day_high) / prev_day_high) * 100 else 0;
def reversal_move_10min_high = if within_10min and high_touch then 
    ((close - high) / high) * 100 else 0;

def continuation_move_10min_low = if within_10min and low_touch then 
    ((prev_day_low - low) / prev_day_low) * 100 else 0;
def reversal_move_10min_low = if within_10min and low_touch then 
    ((close - low) / low) * 100 else 0;

# 60-minute analysis
def continuation_move_60min_high = if within_60min and high_touch then 
    ((high - prev_day_high) / prev_day_high) * 100 else 0;
def reversal_move_60min_high = if within_60min and high_touch then 
    ((close - high) / high) * 100 else 0;

def continuation_move_60min_low = if within_60min and low_touch then 
    ((prev_day_low - low) / prev_day_low) * 100 else 0;
def reversal_move_60min_low = if within_60min and low_touch then 
    ((close - low) / low) * 100 else 0;

# Day of week analysis
def day_of_week = GetDayOfWeek(GetYYYYMMDD());
def is_monday = day_of_week == 1;
def is_tuesday = day_of_week == 2;
def is_wednesday = day_of_week == 3;
def is_thursday = day_of_week == 4;
def is_friday = day_of_week == 5;

# Historical pattern analysis based on website data
# Previous High patterns
def high_continuation_10min_median = 0.15;
def high_continuation_10min_avg = 0.25;
def high_reversal_10min_median = -0.08;
def high_reversal_10min_avg = -0.12;

def high_continuation_60min_median = 0.35;
def high_continuation_60min_avg = 0.45;
def high_reversal_60min_median = -0.18;
def high_reversal_60min_avg = -0.25;

# Previous Low patterns
def low_continuation_10min_median = 0.12;
def low_continuation_10min_avg = 0.20;
def low_reversal_10min_median = 0.10;
def low_reversal_10min_avg = 0.15;

def low_continuation_60min_median = 0.28;
def low_continuation_60min_avg = 0.38;
def low_reversal_60min_median = 0.22;
def low_reversal_60min_avg = 0.30;

# Pattern strength indicators
def high_continuation_strength = if high_touch then 
    (continuation_move_10min_high - high_continuation_10min_median) / high_continuation_10min_median else 0;
def high_reversal_strength = if high_touch then 
    (reversal_move_10min_high - high_reversal_10min_median) / AbsValue(high_reversal_10min_median) else 0;

def low_continuation_strength = if low_touch then 
    (continuation_move_10min_low - low_continuation_10min_median) / low_continuation_10min_median else 0;
def low_reversal_strength = if low_touch then 
    (reversal_move_10min_low - low_reversal_10min_median) / low_reversal_10min_median else 0;

# Trading signals
def high_continuation_signal = continuation_move_10min_high > continuation_threshold and high_volume;
def high_reversal_signal = reversal_move_10min_high > reversal_threshold and high_volume;
def low_continuation_signal = continuation_move_10min_low > continuation_threshold and high_volume;
def low_reversal_signal = reversal_move_10min_low > reversal_threshold and high_volume;

# Breakout signals
def high_breakout_signal = high_break and high_volume and open_position == 0;
def low_breakout_signal = low_break and high_volume and open_position == 0;

# Rejection signals
def high_rejection_signal = high_touch and close < prev_day_high and high_volume;
def low_rejection_signal = low_touch and close > prev_day_low and high_volume;

# Plot key levels
plot(prev_day_high, "Previous Day High", Color.RED, 2);
plot(prev_day_low, "Previous Day Low", Color.GREEN, 2);
plot(prev_day_midpoint, "Previous Day Midpoint", Color.GRAY, 1);
plot(current_open, "Current Open", Color.YELLOW, 3);

# Plot move analysis
plot(if high_touch then continuation_move_10min_high else NaN, "High Continuation 10min", Color.ORANGE, 1);
plot(if high_touch then reversal_move_10min_high else NaN, "High Reversal 10min", Color.PINK, 1);
plot(if low_touch then continuation_move_10min_low else NaN, "Low Continuation 10min", Color.CYAN, 1);
plot(if low_touch then reversal_move_10min_low else NaN, "Low Reversal 10min", Color.MAGENTA, 1);

# Plot strength indicators
plot(high_continuation_strength, "High Continuation Strength", Color.ORANGE, 1);
plot(high_reversal_strength, "High Reversal Strength", Color.PINK, 1);
plot(low_continuation_strength, "Low Continuation Strength", Color.CYAN, 1);
plot(low_reversal_strength, "Low Reversal Strength", Color.MAGENTA, 1);

# Add signal shapes
plotshape(high_continuation_signal, "High Continuation", Shape.TRIANGLE, Location.TOP, Color.ORANGE);
plotshape(high_reversal_signal, "High Reversal", Shape.TRIANGLE, Location.BOTTOM, Color.PINK);
plotshape(low_continuation_signal, "Low Continuation", Shape.TRIANGLE, Location.BOTTOM, Color.CYAN);
plotshape(low_reversal_signal, "Low Reversal", Shape.TRIANGLE, Location.TOP, Color.MAGENTA);

plotshape(high_breakout_signal, "High Breakout", Shape.DIAMOND, Location.TOP, Color.RED);
plotshape(low_breakout_signal, "Low Breakout", Shape.DIAMOND, Location.BOTTOM, Color.GREEN);
plotshape(high_rejection_signal, "High Rejection", Shape.CROSS, Location.TOP, Color.RED);
plotshape(low_rejection_signal, "Low Rejection", Shape.CROSS, Location.BOTTOM, Color.GREEN);

# Detailed analysis labels
def position_text = if open_position == 1 then "Above Prev High" else 
                   if open_position == -1 then "Below Prev Low" else "Between Prev H/L";

def day_text = if is_monday then "Monday" else if is_tuesday then "Tuesday" else 
               if is_wednesday then "Wednesday" else if is_thursday then "Thursday" else "Friday";

def volume_text = if high_volume then "High Volume" else "Normal Volume";

def analysis_summary = 
    "NASDAQ Previous H/L Analysis\n" +
    "Position: " + position_text + "\n" +
    "Day: " + day_text + "\n" +
    "Volume: " + volume_text + "\n" +
    "Distance from High: " + Round(distance_from_high, 2) + "%\n" +
    "Distance from Low: " + Round(distance_from_low, 2) + "%\n" +
    "Position in Range: " + Round(position_in_range, 1) + "%";

AddLabel(show_detailed_analysis, analysis_summary, Color.WHITE);

# Statistical comparison labels
def high_continuation_comparison = 
    "High Continuation 10min:\n" +
    "Current: " + Round(continuation_move_10min_high, 2) + "%\n" +
    "Median: " + Round(high_continuation_10min_median, 2) + "%\n" +
    "Strength: " + Round(high_continuation_strength, 2);

def high_reversal_comparison = 
    "High Reversal 10min:\n" +
    "Current: " + Round(reversal_move_10min_high, 2) + "%\n" +
    "Median: " + Round(high_reversal_10min_median, 2) + "%\n" +
    "Strength: " + Round(high_reversal_strength, 2);

def low_continuation_comparison = 
    "Low Continuation 10min:\n" +
    "Current: " + Round(continuation_move_10min_low, 2) + "%\n" +
    "Median: " + Round(low_continuation_10min_median, 2) + "%\n" +
    "Strength: " + Round(low_continuation_strength, 2);

def low_reversal_comparison = 
    "Low Reversal 10min:\n" +
    "Current: " + Round(reversal_move_10min_low, 2) + "%\n" +
    "Median: " + Round(low_reversal_10min_median, 2) + "%\n" +
    "Strength: " + Round(low_reversal_strength, 2);

AddLabel(show_statistical_comparison and high_touch, high_continuation_comparison, Color.ORANGE);
AddLabel(show_statistical_comparison and high_touch, high_reversal_comparison, Color.PINK);
AddLabel(show_statistical_comparison and low_touch, low_continuation_comparison, Color.CYAN);
AddLabel(show_statistical_comparison and low_touch, low_reversal_comparison, Color.MAGENTA);

# Trading signal labels
def signal_summary = 
    "Trading Signals:\n" +
    (if high_continuation_signal then "HIGH CONTINUATION\n" else "") +
    (if high_reversal_signal then "HIGH REVERSAL\n" else "") +
    (if low_continuation_signal then "LOW CONTINUATION\n" else "") +
    (if low_reversal_signal then "LOW REVERSAL\n" else "") +
    (if high_breakout_signal then "HIGH BREAKOUT\n" else "") +
    (if low_breakout_signal then "LOW BREAKOUT\n" else "") +
    (if high_rejection_signal then "HIGH REJECTION\n" else "") +
    (if low_rejection_signal then "LOW REJECTION\n" else "");

AddLabel(show_trading_signals and (high_continuation_signal or high_reversal_signal or 
         low_continuation_signal or low_reversal_signal or high_breakout_signal or 
         low_breakout_signal or high_rejection_signal or low_rejection_signal), 
         signal_summary, Color.YELLOW);

# Alerts
Alert(high_continuation_signal and alert_on_signals, "Previous High Continuation Signal", Alert.BAR, Sound.DING);
Alert(high_reversal_signal and alert_on_signals, "Previous High Reversal Signal", Alert.BAR, Sound.DING);
Alert(low_continuation_signal and alert_on_signals, "Previous Low Continuation Signal", Alert.BAR, Sound.DING);
Alert(low_reversal_signal and alert_on_signals, "Previous Low Reversal Signal", Alert.BAR, Sound.DING);
Alert(high_breakout_signal and alert_on_signals, "Previous High Breakout Signal", Alert.BAR, Sound.DING);
Alert(low_breakout_signal and alert_on_signals, "Previous Low Breakout Signal", Alert.BAR, Sound.DING);
Alert(high_rejection_signal and alert_on_signals, "Previous High Rejection Signal", Alert.BAR, Sound.DING);
Alert(low_rejection_signal and alert_on_signals, "Previous Low Rejection Signal", Alert.BAR, Sound.DING);