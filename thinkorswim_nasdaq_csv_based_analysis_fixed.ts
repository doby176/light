# ThinkOrSwim NASDAQ Previous High/Low Analysis - CSV Data Based
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

# Position-specific statistics
# Between Previous High and Low statistics
def between_previous_high_and_low_high_continuation_10min_median = 0.0963;
def between_previous_high_and_low_high_continuation_10min_avg = 0.1399;
def between_previous_high_and_low_high_reversal_10min_median = -0.0826;
def between_previous_high_and_low_high_reversal_10min_avg = -0.1383;
def between_previous_high_and_low_low_continuation_10min_median = -0.1556;
def between_previous_high_and_low_low_continuation_10min_avg = -0.2043;
def between_previous_high_and_low_low_reversal_10min_median = 0.1087;
def between_previous_high_and_low_low_reversal_10min_avg = 0.1563;

# Above Previous High statistics
def above_previous_high_high_continuation_10min_median = -0.1305;
def above_previous_high_high_continuation_10min_avg = -0.1468;
def above_previous_high_high_reversal_10min_median = 0.1085;
def above_previous_high_high_reversal_10min_avg = 0.1766;

# Below Previous Low statistics
def below_previous_low_high_continuation_10min_median = 0.1126;
def below_previous_low_high_continuation_10min_avg = 0.1560;
def below_previous_low_high_reversal_10min_median = -0.0576;
def below_previous_low_high_reversal_10min_avg = -0.2362;
def below_previous_low_low_continuation_10min_median = 0.1744;
def below_previous_low_low_continuation_10min_avg = 0.2001;
def below_previous_low_low_reversal_10min_median = -0.1270;
def below_previous_low_low_reversal_10min_avg = -0.2293;

# Day-specific statistics
# Monday statistics
def monday_high_continuation_10min_median = 0.0562;
def monday_high_continuation_10min_avg = 0.0531;
def monday_high_reversal_10min_median = -0.0345;
def monday_high_reversal_10min_avg = -0.0396;
def monday_low_continuation_10min_median = -0.0880;
def monday_low_continuation_10min_avg = -0.0620;
def monday_low_reversal_10min_median = 0.0239;
def monday_low_reversal_10min_avg = 0.0022;

# Tuesday statistics
def tuesday_high_continuation_10min_median = 0.0309;
def tuesday_high_continuation_10min_avg = 0.0270;
def tuesday_high_reversal_10min_median = -0.0181;
def tuesday_high_reversal_10min_avg = -0.0155;
def tuesday_low_continuation_10min_median = -0.1000;
def tuesday_low_continuation_10min_avg = -0.1030;
def tuesday_low_reversal_10min_median = 0.0648;
def tuesday_low_reversal_10min_avg = 0.0498;

# Wednesday statistics
def wednesday_high_continuation_10min_median = 0.0428;
def wednesday_high_continuation_10min_avg = 0.0532;
def wednesday_high_reversal_10min_median = -0.0504;
def wednesday_high_reversal_10min_avg = -0.0381;
def wednesday_low_continuation_10min_median = -0.1230;
def wednesday_low_continuation_10min_avg = -0.1235;
def wednesday_low_reversal_10min_median = 0.0599;
def wednesday_low_reversal_10min_avg = 0.0811;

# Thursday statistics
def thursday_high_continuation_10min_median = 0.0457;
def thursday_high_continuation_10min_avg = 0.0294;
def thursday_high_reversal_10min_median = -0.0335;
def thursday_high_reversal_10min_avg = -0.0392;
def thursday_low_continuation_10min_median = -0.0522;
def thursday_low_continuation_10min_avg = -0.0631;
def thursday_low_reversal_10min_median = 0.0509;
def thursday_low_reversal_10min_avg = 0.0334;

# Friday statistics
def friday_high_continuation_10min_median = 0.0386;
def friday_high_continuation_10min_avg = 0.0318;
def friday_high_reversal_10min_median = -0.0111;
def friday_high_reversal_10min_avg = -0.0164;
def friday_low_continuation_10min_median = -0.0753;
def friday_low_continuation_10min_avg = -0.0856;
def friday_low_reversal_10min_median = 0.0616;
def friday_low_reversal_10min_avg = 0.0533;

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

# Get appropriate statistics based on current conditions (simplified)
def current_high_continuation_median = 
    if open_position == 0 then {
        if is_monday then monday_high_continuation_10min_median
        else if is_tuesday then tuesday_high_continuation_10min_median
        else if is_wednesday then wednesday_high_continuation_10min_median
        else if is_thursday then thursday_high_continuation_10min_median
        else if is_friday then friday_high_continuation_10min_median
        else between_previous_high_and_low_high_continuation_10min_median
    } else if open_position == 1 then {
        above_previous_high_high_continuation_10min_median
    } else {
        below_previous_low_high_continuation_10min_median
    };

def current_high_reversal_median = 
    if open_position == 0 then {
        if is_monday then monday_high_reversal_10min_median
        else if is_tuesday then tuesday_high_reversal_10min_median
        else if is_wednesday then wednesday_high_reversal_10min_median
        else if is_thursday then thursday_high_reversal_10min_median
        else if is_friday then friday_high_reversal_10min_median
        else between_previous_high_and_low_high_reversal_10min_median
    } else if open_position == 1 then {
        above_previous_high_high_reversal_10min_median
    } else {
        below_previous_low_high_reversal_10min_median
    };

def current_low_continuation_median = 
    if open_position == 0 then {
        if is_monday then monday_low_continuation_10min_median
        else if is_tuesday then tuesday_low_continuation_10min_median
        else if is_wednesday then wednesday_low_continuation_10min_median
        else if is_thursday then thursday_low_continuation_10min_median
        else if is_friday then friday_low_continuation_10min_median
        else between_previous_high_and_low_low_continuation_10min_median
    } else if open_position == -1 then {
        below_previous_low_low_continuation_10min_median
    } else {
        low_continuation_10min_median
    };

def current_low_reversal_median = 
    if open_position == 0 then {
        if is_monday then monday_low_reversal_10min_median
        else if is_tuesday then tuesday_low_reversal_10min_median
        else if is_wednesday then wednesday_low_reversal_10min_median
        else if is_thursday then thursday_low_reversal_10min_median
        else if is_friday then friday_low_reversal_10min_median
        else between_previous_high_and_low_low_reversal_10min_median
    } else if open_position == -1 then {
        below_previous_low_low_reversal_10min_median
    } else {
        low_reversal_10min_median
    };

# Trading signals
def high_continuation_signal = continuation_move_10min_high > continuation_threshold and high_volume;
def high_reversal_signal = reversal_move_10min_high > reversal_threshold and high_volume;
def low_continuation_signal = continuation_move_10min_low > continuation_threshold and high_volume;
def low_reversal_signal = reversal_move_10min_low > reversal_threshold and high_volume;

# Breakout signals
def high_breakout = close > prev_day_high and high_volume and open_position == 0;
def low_breakout = close < prev_day_low and high_volume and open_position == 0;

# Plot key levels
plot(prev_day_high, "Previous Day High", Color.RED, 2);
plot(prev_day_low, "Previous Day Low", Color.GREEN, 2);
plot(current_open, "Current Open", Color.YELLOW, 3);

# Plot move values
plot(continuation_move_10min_high, "High Continuation 10min", Color.ORANGE, 1);
plot(reversal_move_10min_high, "High Reversal 10min", Color.PINK, 1);
plot(continuation_move_10min_low, "Low Continuation 10min", Color.CYAN, 1);
plot(reversal_move_10min_low, "Low Reversal 10min", Color.MAGENTA, 1);

# Plot historical medians
plot(current_high_continuation_median, "High Continuation Median", Color.ORANGE, 1);
plot(current_high_reversal_median, "High Reversal Median", Color.PINK, 1);
plot(current_low_continuation_median, "Low Continuation Median", Color.CYAN, 1);
plot(current_low_reversal_median, "Low Reversal Median", Color.MAGENTA, 1);

# Add signal shapes
plotshape(high_continuation_signal, "High Continuation", Shape.TRIANGLE, Location.TOP, Color.ORANGE);
plotshape(high_reversal_signal, "High Reversal", Shape.TRIANGLE, Location.BOTTOM, Color.PINK);
plotshape(low_continuation_signal, "Low Continuation", Shape.TRIANGLE, Location.BOTTOM, Color.CYAN);
plotshape(low_reversal_signal, "Low Reversal", Shape.TRIANGLE, Location.TOP, Color.MAGENTA);
plotshape(high_breakout, "High Breakout", Shape.DIAMOND, Location.TOP, Color.RED);
plotshape(low_breakout, "Low Breakout", Shape.DIAMOND, Location.BOTTOM, Color.GREEN);

# Position text
def position_text = if open_position == 1 then "Above Prev High" else 
                   if open_position == -1 then "Below Prev Low" else "Between Prev H/L";

def day_text = if is_monday then "Monday" else if is_tuesday then "Tuesday" else 
               if is_wednesday then "Wednesday" else if is_thursday then "Thursday" else "Friday";

# Analysis summary
def analysis_summary = 
    "NASDAQ Previous H/L Analysis\n" +
    "Data Source: 2100+ days CSV\n" +
    "Position: " + position_text + "\n" +
    "Day: " + day_text + "\n" +
    "Volume: " + (if high_volume then "High" else "Normal") + "\n" +
    "High Continuation: " + Round(continuation_move_10min_high, 2) + "%\n" +
    "High Reversal: " + Round(reversal_move_10min_high, 2) + "%\n" +
    "Low Continuation: " + Round(continuation_move_10min_low, 2) + "%\n" +
    "Low Reversal: " + Round(reversal_move_10min_low, 2) + "%";

AddLabel(show_analysis, analysis_summary, Color.WHITE);

# Statistical comparison
def high_continuation_comparison = 
    "High Continuation:\n" +
    "Current: " + Round(continuation_move_10min_high, 2) + "%\n" +
    "Historical Median: " + Round(current_high_continuation_median, 2) + "%\n" +
    "Strength: " + Round((continuation_move_10min_high - current_high_continuation_median) / AbsValue(current_high_continuation_median), 2);

def high_reversal_comparison = 
    "High Reversal:\n" +
    "Current: " + Round(reversal_move_10min_high, 2) + "%\n" +
    "Historical Median: " + Round(current_high_reversal_median, 2) + "%\n" +
    "Strength: " + Round((reversal_move_10min_high - current_high_reversal_median) / AbsValue(current_high_reversal_median), 2);

def low_continuation_comparison = 
    "Low Continuation:\n" +
    "Current: " + Round(continuation_move_10min_low, 2) + "%\n" +
    "Historical Median: " + Round(current_low_continuation_median, 2) + "%\n" +
    "Strength: " + Round((continuation_move_10min_low - current_low_continuation_median) / AbsValue(current_low_continuation_median), 2);

def low_reversal_comparison = 
    "Low Reversal:\n" +
    "Current: " + Round(reversal_move_10min_low, 2) + "%\n" +
    "Historical Median: " + Round(current_low_reversal_median, 2) + "%\n" +
    "Strength: " + Round((reversal_move_10min_low - current_low_reversal_median) / AbsValue(current_low_reversal_median), 2);

AddLabel(show_analysis and high_touch, high_continuation_comparison, Color.ORANGE);
AddLabel(show_analysis and high_touch, high_reversal_comparison, Color.PINK);
AddLabel(show_analysis and low_touch, low_continuation_comparison, Color.CYAN);
AddLabel(show_analysis and low_touch, low_reversal_comparison, Color.MAGENTA);

# Signal summary
def signal_summary = 
    "Trading Signals:\n" +
    (if high_continuation_signal then "HIGH CONTINUATION\n" else "") +
    (if high_reversal_signal then "HIGH REVERSAL\n" else "") +
    (if low_continuation_signal then "LOW CONTINUATION\n" else "") +
    (if low_reversal_signal then "LOW REVERSAL\n" else "") +
    (if high_breakout then "HIGH BREAKOUT\n" else "") +
    (if low_breakout then "LOW BREAKOUT\n" else "");

AddLabel(show_analysis and (high_continuation_signal or high_reversal_signal or 
         low_continuation_signal or low_reversal_signal or high_breakout or low_breakout), 
         signal_summary, Color.YELLOW);

# Alerts
Alert(high_continuation_signal and show_alerts, "High Continuation", Alert.BAR, Sound.DING);
Alert(high_reversal_signal and show_alerts, "High Reversal", Alert.BAR, Sound.DING);
Alert(low_continuation_signal and show_alerts, "Low Continuation", Alert.BAR, Sound.DING);
Alert(low_reversal_signal and show_alerts, "Low Reversal", Alert.BAR, Sound.DING);
Alert(high_breakout and show_alerts, "High Breakout", Alert.BAR, Sound.DING);
Alert(low_breakout and show_alerts, "Low Breakout", Alert.BAR, Sound.DING);