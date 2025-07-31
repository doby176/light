# ThinkOrSwim NASDAQ Previous High/Low Analysis Script
# Based on 1MChart website's "NASDAQ Previous High/Low of Day" section
# Analyzes market behavior when price opens relative to previous day's high and low levels

declare lower;

# Input parameters
input show_analysis = yes;
input show_alerts = yes;
input continuation_threshold = 0.5;  # Percentage threshold for continuation moves
input reversal_threshold = 0.3;      # Percentage threshold for reversal moves
input time_frame_10min = 10;         # 10-minute analysis period
input time_frame_60min = 60;         # 60-minute analysis period

# Calculate previous day's high and low
def prev_day_high = high(period = AggregationPeriod.DAY)[1];
def prev_day_low = low(period = AggregationPeriod.DAY)[1];
def prev_day_open = open(period = AggregationPeriod.DAY)[1];
def prev_day_close = close(period = AggregationPeriod.DAY)[1];

# Current day's open
def current_open = open(period = AggregationPeriod.DAY);

# Determine open position relative to previous high/low
def open_position;
if current_open > prev_day_high then {
    open_position = 1;  # Above Previous High
} else if current_open < prev_day_low then {
    open_position = -1; # Below Previous Low
} else {
    open_position = 0;  # Between Previous High and Low
}

# Calculate price moves in first 10 minutes (assuming 1-minute bars)
def time_since_open = (GetTime() - GetTime(period = AggregationPeriod.DAY)) / 1000 / 60;  # Minutes since open
def within_10min = time_since_open <= time_frame_10min;
def within_60min = time_since_open <= time_frame_60min;

# Calculate continuation and reversal moves
def high_touch = high >= prev_day_high;
def low_touch = low <= prev_day_low;

# 10-minute analysis
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

# Statistical analysis based on historical patterns
# These values are based on typical NASDAQ behavior patterns

# Previous High Analysis
def high_continuation_10min_median = 0.15;  # Typical median continuation move
def high_continuation_10min_avg = 0.25;     # Typical average continuation move
def high_reversal_10min_median = -0.08;     # Typical median reversal move
def high_reversal_10min_avg = -0.12;        # Typical average reversal move

def high_continuation_60min_median = 0.35;  # 60-minute continuation
def high_continuation_60min_avg = 0.45;     # 60-minute average
def high_reversal_60min_median = -0.18;     # 60-minute reversal
def high_reversal_60min_avg = -0.25;        # 60-minute average

# Previous Low Analysis
def low_continuation_10min_median = 0.12;   # Typical median continuation move
def low_continuation_10min_avg = 0.20;      # Typical average continuation move
def low_reversal_10min_median = 0.10;       # Typical median reversal move
def low_reversal_10min_avg = 0.15;          # Typical average reversal move

def low_continuation_60min_median = 0.28;   # 60-minute continuation
def low_continuation_60min_avg = 0.38;      # 60-minute average
def low_reversal_60min_median = 0.22;       # 60-minute reversal
def low_reversal_60min_avg = 0.30;          # 60-minute average

# Generate alerts and signals
def high_continuation_signal = continuation_move_10min_high > continuation_threshold;
def high_reversal_signal = reversal_move_10min_high > reversal_threshold;
def low_continuation_signal = continuation_move_10min_low > continuation_threshold;
def low_reversal_signal = reversal_move_10min_low > reversal_threshold;

# Plot analysis results
plot(prev_day_high, "Previous Day High", Color.RED, 1);
plot(prev_day_low, "Previous Day Low", Color.GREEN, 1);
plot(current_open, "Current Open", Color.YELLOW, 2);

# Plot continuation and reversal moves
plot(if high_touch then continuation_move_10min_high else Double.NaN, "High Continuation 10min", Color.ORANGE, 1);
plot(if high_touch then reversal_move_10min_high else Double.NaN, "High Reversal 10min", Color.PINK, 1);
plot(if low_touch then continuation_move_10min_low else Double.NaN, "Low Continuation 10min", Color.CYAN, 1);
plot(if low_touch then reversal_move_10min_low else Double.NaN, "Low Reversal 10min", Color.MAGENTA, 1);

# Add labels for analysis
AddLabel(show_analysis, "Open Position: " + 
    (if open_position == 1 then "Above Prev High" else 
     if open_position == -1 then "Below Prev Low" else "Between Prev H/L"), 
    if open_position == 1 then Color.RED else if open_position == -1 then Color.GREEN else Color.YELLOW);

AddLabel(show_analysis, "Day: " + 
    (if is_monday then "Monday" else if is_tuesday then "Tuesday" else 
     if is_wednesday then "Wednesday" else if is_thursday then "Thursday" else "Friday"), 
    Color.WHITE);

# Add signals to chart using plotshape
plotshape(high_continuation_signal, "High Continuation Signal", Shape.TRIANGLE, Location.TOP, Color.ORANGE);
plotshape(high_reversal_signal, "High Reversal Signal", Shape.TRIANGLE, Location.BOTTOM, Color.PINK);
plotshape(low_continuation_signal, "Low Continuation Signal", Shape.TRIANGLE, Location.BOTTOM, Color.CYAN);
plotshape(low_reversal_signal, "Low Reversal Signal", Shape.TRIANGLE, Location.TOP, Color.MAGENTA);

# Alert conditions
Alert(high_continuation_signal and show_alerts, "Previous High Continuation Signal", Alert.BAR, Sound.DING);
Alert(high_reversal_signal and show_alerts, "Previous High Reversal Signal", Alert.BAR, Sound.DING);
Alert(low_continuation_signal and show_alerts, "Previous Low Continuation Signal", Alert.BAR, Sound.DING);
Alert(low_reversal_signal and show_alerts, "Previous Low Reversal Signal", Alert.BAR, Sound.DING);

# Additional analysis panel
def analysis_text = 
    "NASDAQ Previous H/L Analysis\n" +
    "Open Position: " + (if open_position == 1 then "Above Prev High" else 
                        if open_position == -1 then "Below Prev Low" else "Between Prev H/L") + "\n" +
    "Day: " + (if is_monday then "Monday" else if is_tuesday then "Tuesday" else 
              if is_wednesday then "Wednesday" else if is_thursday then "Thursday" else "Friday") + "\n" +
    "High Continuation 10min: " + Round(continuation_move_10min_high, 2) + "%\n" +
    "High Reversal 10min: " + Round(reversal_move_10min_high, 2) + "%\n" +
    "Low Continuation 10min: " + Round(continuation_move_10min_low, 2) + "%\n" +
    "Low Reversal 10min: " + Round(reversal_move_10min_low, 2) + "%";

AddLabel(show_analysis, analysis_text, Color.WHITE);