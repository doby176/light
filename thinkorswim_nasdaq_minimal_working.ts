# ThinkOrSwim NASDAQ Previous High/Low Analysis - Minimal Working Version
# Generated from 2100+ days of historical data from your website's CSV file

declare lower;

# Input parameters
input show_analysis = yes;
input show_alerts = yes;
input continuation_threshold = 0.5;
input reversal_threshold = 0.3;

# Overall statistics from 2100+ days of data
def high_continuation_10min_median = 0.0418;
def high_continuation_10min_avg = 0.0386;
def high_reversal_10min_median = -0.0277;
def high_reversal_10min_avg = -0.0295;
def low_continuation_10min_median = -0.0912;
def low_continuation_10min_avg = -0.0881;
def low_reversal_10min_median = 0.0539;
def low_reversal_10min_avg = 0.0455;

# Calculate previous day's levels
def prev_day_high = high(period = AggregationPeriod.DAY)[1];
def prev_day_low = low(period = AggregationPeriod.DAY)[1];
def current_open = open(period = AggregationPeriod.DAY);

# Determine open position
def open_position;
if current_open > prev_day_high then {
    open_position = 1;  # Above Previous High
} else if current_open < prev_day_low then {
    open_position = -1; # Below Previous Low
} else {
    open_position = 0;  # Between Previous High and Low
}

# Calculate time since market open
def time_since_open = (GetTime() - GetTime(period = AggregationPeriod.DAY)) / 1000 / 60;
def within_10min = time_since_open <= 10;

# Touch detection
def high_touch = high >= prev_day_high;
def low_touch = low <= prev_day_low;

# Calculate moves when touching levels
def continuation_move_10min_high = if within_10min and high_touch then 
    ((high - prev_day_high) / prev_day_high) * 100 else 0;
def reversal_move_10min_high = if within_10min and high_touch then 
    ((close - high) / high) * 100 else 0;

def continuation_move_10min_low = if within_10min and low_touch then 
    ((prev_day_low - low) / prev_day_low) * 100 else 0;
def reversal_move_10min_low = if within_10min and low_touch then 
    ((close - low) / low) * 100 else 0;

# Day of week
def day_of_week = GetDayOfWeek(GetYYYYMMDD());
def is_monday = day_of_week == 1;
def is_tuesday = day_of_week == 2;
def is_wednesday = day_of_week == 3;
def is_thursday = day_of_week == 4;
def is_friday = day_of_week == 5;

# Volume analysis
def avg_volume = Average(volume, 20);
def volume_ratio = volume / avg_volume;
def high_volume = volume_ratio > 1.5;

# Trading signals
def high_continuation_signal = continuation_move_10min_high > continuation_threshold and high_volume;
def high_reversal_signal = reversal_move_10min_high > reversal_threshold and high_volume;
def low_continuation_signal = continuation_move_10min_low > continuation_threshold and high_volume;
def low_reversal_signal = reversal_move_10min_low > reversal_threshold and high_volume;

# Breakout signals
def high_breakout = close > prev_day_high and high_volume and open_position == 0;
def low_breakout = close < prev_day_low and high_volume and open_position == 0;

# Plot key levels (only the essential ones)
plot(prev_day_high, "Previous Day High", Color.RED, 2);
plot(prev_day_low, "Previous Day Low", Color.GREEN, 2);
plot(current_open, "Current Open", Color.YELLOW, 3);

# Plot move values (simplified)
plot(continuation_move_10min_high, "High Continuation 10min", Color.ORANGE, 1);
plot(reversal_move_10min_high, "High Reversal 10min", Color.PINK, 1);
plot(continuation_move_10min_low, "Low Continuation 10min", Color.CYAN, 1);
plot(reversal_move_10min_low, "Low Reversal 10min", Color.MAGENTA, 1);

# Position text
def position_text = if open_position == 1 then "Above Prev High" else 
                   if open_position == -1 then "Below Prev Low" else "Between Prev H/L";

def day_text = if is_monday then "Monday" else if is_tuesday then "Tuesday" else 
               if is_wednesday then "Wednesday" else if is_thursday then "Thursday" else "Friday";

# Simple analysis summary
def analysis_summary = 
    "NASDAQ Previous H/L Analysis\n" +
    "Data Source: 2100+ days CSV\n" +
    "Position: " + position_text + "\n" +
    "Day: " + day_text + "\n" +
    "High Continuation: " + Round(continuation_move_10min_high, 2) + "%\n" +
    "High Reversal: " + Round(reversal_move_10min_high, 2) + "%\n" +
    "Low Continuation: " + Round(continuation_move_10min_low, 2) + "%\n" +
    "Low Reversal: " + Round(reversal_move_10min_low, 2) + "%";

AddLabel(show_analysis, analysis_summary, Color.WHITE);

# Simple signal display
def signal_text = 
    "Signals: " +
    (if high_continuation_signal then "HIGH CONT " else "") +
    (if high_reversal_signal then "HIGH REV " else "") +
    (if low_continuation_signal then "LOW CONT " else "") +
    (if low_reversal_signal then "LOW REV " else "") +
    (if high_breakout then "HIGH BRK " else "") +
    (if low_breakout then "LOW BRK " else "");

AddLabel(show_analysis, signal_text, Color.YELLOW);

# Historical comparison
def comparison_text = 
    "Historical Medians:\n" +
    "High Cont: " + Round(high_continuation_10min_median, 2) + "%\n" +
    "High Rev: " + Round(high_reversal_10min_median, 2) + "%\n" +
    "Low Cont: " + Round(low_continuation_10min_median, 2) + "%\n" +
    "Low Rev: " + Round(low_reversal_10min_median, 2) + "%";

AddLabel(show_analysis, comparison_text, Color.CYAN);

# Alerts
Alert(high_continuation_signal and show_alerts, "High Continuation", Alert.BAR, Sound.DING);
Alert(high_reversal_signal and show_alerts, "High Reversal", Alert.BAR, Sound.DING);
Alert(low_continuation_signal and show_alerts, "Low Continuation", Alert.BAR, Sound.DING);
Alert(low_reversal_signal and show_alerts, "Low Reversal", Alert.BAR, Sound.DING);
Alert(high_breakout and show_alerts, "High Breakout", Alert.BAR, Sound.DING);
Alert(low_breakout and show_alerts, "Low Breakout", Alert.BAR, Sound.DING);