import pandas as pd
import numpy as np

# Read the CSV data
df = pd.read_csv('data/previuos_high_low.csv')

print("Data shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Analyze by different scenarios
print("\n" + "="*50)
print("ANALYSIS BY OPEN POSITION")
print("="*50)

# Group by open position
position_stats = df.groupby('open_position').agg({
    'continuation_move_pct': ['count', 'mean', 'median', 'std'],
    'reversal_move_pct': ['count', 'mean', 'median', 'std'],
    'continuation_move_pct_60min': ['count', 'mean', 'median', 'std'],
    'reversal_move_pct_60min': ['count', 'mean', 'median', 'std']
}).round(4)

print(position_stats)

print("\n" + "="*50)
print("ANALYSIS BY DAY OF WEEK")
print("="*50)

# Group by day of week
day_stats = df.groupby('day_of_week').agg({
    'continuation_move_pct': ['count', 'mean', 'median', 'std'],
    'reversal_move_pct': ['count', 'mean', 'median', 'std'],
    'continuation_move_pct_60min': ['count', 'mean', 'median', 'std'],
    'reversal_move_pct_60min': ['count', 'mean', 'median', 'std']
}).round(4)

print(day_stats)

print("\n" + "="*50)
print("ANALYSIS BY TOUCH TYPE")
print("="*50)

# Group by touch type (Previous High vs Previous Low)
touch_stats = df.groupby('touch_type').agg({
    'continuation_move_pct': ['count', 'mean', 'median', 'std'],
    'reversal_move_pct': ['count', 'mean', 'median', 'std'],
    'continuation_move_pct_60min': ['count', 'mean', 'median', 'std'],
    'reversal_move_pct_60min': ['count', 'mean', 'median', 'std']
}).round(4)

print(touch_stats)

print("\n" + "="*50)
print("COMBINED ANALYSIS")
print("="*50)

# Combined analysis by position and day
combined_stats = df.groupby(['open_position', 'day_of_week']).agg({
    'continuation_move_pct': ['count', 'mean', 'median'],
    'reversal_move_pct': ['count', 'mean', 'median'],
    'continuation_move_pct_60min': ['count', 'mean', 'median'],
    'reversal_move_pct_60min': ['count', 'mean', 'median']
}).round(4)

print(combined_stats)

# Generate ThinkScript database
print("\n" + "="*50)
print("THINKSCRIPT DATABASE GENERATION")
print("="*50)

# Create comprehensive database for ThinkScript
def generate_think_script_database():
    # Overall statistics
    overall_stats = {
        'high_continuation_10min_median': df[df['touch_type'] == 'Previous High']['continuation_move_pct'].median(),
        'high_continuation_10min_avg': df[df['touch_type'] == 'Previous High']['continuation_move_pct'].mean(),
        'high_reversal_10min_median': df[df['touch_type'] == 'Previous High']['reversal_move_pct'].median(),
        'high_reversal_10min_avg': df[df['touch_type'] == 'Previous High']['reversal_move_pct'].mean(),
        'low_continuation_10min_median': df[df['touch_type'] == 'Previous Low']['continuation_move_pct'].median(),
        'low_continuation_10min_avg': df[df['touch_type'] == 'Previous Low']['continuation_move_pct'].mean(),
        'low_reversal_10min_median': df[df['touch_type'] == 'Previous Low']['reversal_move_pct'].median(),
        'low_reversal_10min_avg': df[df['touch_type'] == 'Previous Low']['reversal_move_pct'].mean(),
        
        'high_continuation_60min_median': df[df['touch_type'] == 'Previous High']['continuation_move_pct_60min'].median(),
        'high_continuation_60min_avg': df[df['touch_type'] == 'Previous High']['continuation_move_pct_60min'].mean(),
        'high_reversal_60min_median': df[df['touch_type'] == 'Previous High']['reversal_move_pct_60min'].median(),
        'high_reversal_60min_avg': df[df['touch_type'] == 'Previous High']['reversal_move_pct_60min'].mean(),
        'low_continuation_60min_median': df[df['touch_type'] == 'Previous Low']['continuation_move_pct_60min'].median(),
        'low_continuation_60min_avg': df[df['touch_type'] == 'Previous Low']['continuation_move_pct_60min'].mean(),
        'low_reversal_60min_median': df[df['touch_type'] == 'Previous Low']['reversal_move_pct_60min'].median(),
        'low_reversal_60min_avg': df[df['touch_type'] == 'Previous Low']['reversal_move_pct_60min'].mean(),
    }
    
    # Position-specific statistics
    position_specific = {}
    for position in df['open_position'].unique():
        pos_data = df[df['open_position'] == position]
        position_specific[position] = {
            'high_continuation_10min_median': pos_data[pos_data['touch_type'] == 'Previous High']['continuation_move_pct'].median(),
            'high_continuation_10min_avg': pos_data[pos_data['touch_type'] == 'Previous High']['continuation_move_pct'].mean(),
            'high_reversal_10min_median': pos_data[pos_data['touch_type'] == 'Previous High']['reversal_move_pct'].median(),
            'high_reversal_10min_avg': pos_data[pos_data['touch_type'] == 'Previous High']['reversal_move_pct'].mean(),
            'low_continuation_10min_median': pos_data[pos_data['touch_type'] == 'Previous Low']['continuation_move_pct'].median(),
            'low_continuation_10min_avg': pos_data[pos_data['touch_type'] == 'Previous Low']['continuation_move_pct'].mean(),
            'low_reversal_10min_median': pos_data[pos_data['touch_type'] == 'Previous Low']['reversal_move_pct'].median(),
            'low_reversal_10min_avg': pos_data[pos_data['touch_type'] == 'Previous Low']['reversal_move_pct'].mean(),
        }
    
    # Day-specific statistics
    day_specific = {}
    for day in df['day_of_week'].unique():
        day_data = df[df['day_of_week'] == day]
        day_specific[day] = {
            'high_continuation_10min_median': day_data[day_data['touch_type'] == 'Previous High']['continuation_move_pct'].median(),
            'high_continuation_10min_avg': day_data[day_data['touch_type'] == 'Previous High']['continuation_move_pct'].mean(),
            'high_reversal_10min_median': day_data[day_data['touch_type'] == 'Previous High']['reversal_move_pct'].median(),
            'high_reversal_10min_avg': day_data[day_data['touch_type'] == 'Previous High']['reversal_move_pct'].mean(),
            'low_continuation_10min_median': day_data[day_data['touch_type'] == 'Previous Low']['continuation_move_pct'].median(),
            'low_continuation_10min_avg': day_data[day_data['touch_type'] == 'Previous Low']['continuation_move_pct'].mean(),
            'low_reversal_10min_median': day_data[day_data['touch_type'] == 'Previous Low']['reversal_move_pct'].median(),
            'low_reversal_10min_avg': day_data[day_data['touch_type'] == 'Previous Low']['reversal_move_pct'].mean(),
        }
    
    return overall_stats, position_specific, day_specific

overall_stats, position_specific, day_specific = generate_think_script_database()

print("Overall Statistics:")
for key, value in overall_stats.items():
    print(f"{key}: {value:.4f}")

print("\nPosition-Specific Statistics:")
for position, stats in position_specific.items():
    print(f"\n{position}:")
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}")

print("\nDay-Specific Statistics:")
for day, stats in day_specific.items():
    print(f"\n{day}:")
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}")

# Generate ThinkScript code
print("\n" + "="*50)
print("THINKSCRIPT CODE GENERATION")
print("="*50)

def generate_think_script_code():
    code = "# ThinkOrSwim NASDAQ Previous High/Low Analysis - CSV Data Based\n"
    code += "# Generated from 2100+ days of historical data\n\n"
    
    code += "declare lower;\n\n"
    
    # Input parameters
    code += "# Input parameters\n"
    code += "input show_analysis = yes;\n"
    code += "input show_alerts = yes;\n"
    code += "input continuation_threshold = 0.5;\n"
    code += "input reversal_threshold = 0.3;\n\n"
    
    # Overall statistics
    code += "# Overall statistics from 2100+ days of data\n"
    for key, value in overall_stats.items():
        code += f"def {key} = {value:.4f};\n"
    code += "\n"
    
    # Position-specific statistics
    code += "# Position-specific statistics\n"
    for position, stats in position_specific.items():
        position_name = position.replace(" ", "_").lower()
        code += f"# {position} statistics\n"
        for key, value in stats.items():
            code += f"def {position_name}_{key} = {value:.4f};\n"
        code += "\n"
    
    # Day-specific statistics
    code += "# Day-specific statistics\n"
    for day, stats in day_specific.items():
        day_name = day.lower()
        code += f"# {day} statistics\n"
        for key, value in stats.items():
            code += f"def {day_name}_{key} = {value:.4f};\n"
        code += "\n"
    
    return code

print(generate_think_script_code())