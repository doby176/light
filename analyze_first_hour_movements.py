import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Read the CSV file
df = pd.read_csv('data/event_analysis_metrics.csv')

# Focus on the columns of interest
columns_of_interest = ['date', 'event_type', 'percent_move_930_1030_x', 'direction_930_1030_x']
analysis_df = df[columns_of_interest].copy()

# Convert date to datetime
analysis_df['date'] = pd.to_datetime(analysis_df['date'])

# Remove rows with missing values in our target columns
analysis_df = analysis_df.dropna(subset=['percent_move_930_1030_x', 'direction_930_1030_x'])

print("=== FIRST HOUR MOVEMENT ANALYSIS ===")
print(f"Total events analyzed: {len(analysis_df)}")
print(f"Date range: {analysis_df['date'].min().strftime('%Y-%m-%d')} to {analysis_df['date'].max().strftime('%Y-%m-%d')}")
print()

# 1. Event Type Distribution
print("1. EVENT TYPE DISTRIBUTION:")
event_counts = analysis_df['event_type'].value_counts()
print(event_counts)
print()

# 2. Direction Analysis
print("2. FIRST HOUR DIRECTION ANALYSIS:")
direction_counts = analysis_df['direction_930_1030_x'].value_counts()
print(direction_counts)
print(f"Up movements: {direction_counts.get('Up', 0)} ({direction_counts.get('Up', 0)/len(analysis_df)*100:.1f}%)")
print(f"Down movements: {direction_counts.get('Down', 0)} ({direction_counts.get('Down', 0)/len(analysis_df)*100:.1f}%)")
print()

# 3. Magnitude Analysis
print("3. FIRST HOUR MAGNITUDE ANALYSIS:")
print(f"Average movement: {analysis_df['percent_move_930_1030_x'].mean():.4f}%")
print(f"Median movement: {analysis_df['percent_move_930_1030_x'].median():.4f}%")
print(f"Standard deviation: {analysis_df['percent_move_930_1030_x'].std():.4f}%")
print(f"Min movement: {analysis_df['percent_move_930_1030_x'].min():.4f}%")
print(f"Max movement: {analysis_df['percent_move_930_1030_x'].max():.4f}%")
print()

# 4. Direction vs Magnitude
print("4. DIRECTION vs MAGNITUDE:")
up_movements = analysis_df[analysis_df['direction_930_1030_x'] == 'Up']['percent_move_930_1030_x']
down_movements = analysis_df[analysis_df['direction_930_1030_x'] == 'Down']['percent_move_930_1030_x']

print("UP movements:")
print(f"  Average: {up_movements.mean():.4f}%")
print(f"  Median: {up_movements.median():.4f}%")
print(f"  Max: {up_movements.max():.4f}%")
print()

print("DOWN movements:")
print(f"  Average: {down_movements.mean():.4f}%")
print(f"  Median: {down_movements.median():.4f}%")
print(f"  Min: {down_movements.min():.4f}%")
print()

# 5. Extreme Movements Analysis
print("5. EXTREME MOVEMENTS (>1% or <-1%):")
extreme_up = analysis_df[(analysis_df['direction_930_1030_x'] == 'Up') & (analysis_df['percent_move_930_1030_x'] > 1)]
extreme_down = analysis_df[(analysis_df['direction_930_1030_x'] == 'Down') & (analysis_df['percent_move_930_1030_x'] < -1)]

print(f"Extreme up movements (>1%): {len(extreme_up)} events")
print(f"Extreme down movements (<-1%): {len(extreme_down)} events")
print(f"Total extreme movements: {len(extreme_up) + len(extreme_down)} ({((len(extreme_up) + len(extreme_down))/len(analysis_df)*100):.1f}% of all events)")
print()

# 6. Top 10 Largest Movements
print("6. TOP 10 LARGEST FIRST HOUR MOVEMENTS:")
top_movements = analysis_df.nlargest(10, 'percent_move_930_1030_x')[['date', 'event_type', 'percent_move_930_1030_x', 'direction_930_1030_x']]
print(top_movements.to_string(index=False))
print()

print("7. TOP 10 LARGEST DOWNWARD FIRST HOUR MOVEMENTS:")
top_down_movements = analysis_df.nsmallest(10, 'percent_move_930_1030_x')[['date', 'event_type', 'percent_move_930_1030_x', 'direction_930_1030_x']]
print(top_down_movements.to_string(index=False))
print()

# 8. Event Type Performance
print("8. EVENT TYPE PERFORMANCE (First Hour):")
event_performance = analysis_df.groupby('event_type').agg({
    'percent_move_930_1030_x': ['count', 'mean', 'median', 'std'],
    'direction_930_1030_x': lambda x: (x == 'Up').sum()
}).round(4)

event_performance.columns = ['Count', 'Mean_Move', 'Median_Move', 'Std_Move', 'Up_Count']
event_performance['Up_Rate'] = (event_performance['Up_Count'] / event_performance['Count'] * 100).round(1)
print(event_performance)
print()

# 9. Time Period Analysis
print("9. TIME PERIOD ANALYSIS:")
analysis_df['year'] = analysis_df['date'].dt.year
yearly_stats = analysis_df.groupby('year').agg({
    'percent_move_930_1030_x': ['count', 'mean', 'std'],
    'direction_930_1030_x': lambda x: (x == 'Up').sum()
}).round(4)

yearly_stats.columns = ['Count', 'Mean_Move', 'Std_Move', 'Up_Count']
yearly_stats['Up_Rate'] = (yearly_stats['Up_Count'] / yearly_stats['Count'] * 100).round(1)
print(yearly_stats)
print()

# 10. Volatility Analysis
print("10. VOLATILITY ANALYSIS:")
# Calculate rolling volatility (standard deviation of movements)
analysis_df_sorted = analysis_df.sort_values('date')
analysis_df_sorted['rolling_volatility'] = analysis_df_sorted['percent_move_930_1030_x'].rolling(window=12).std()

print(f"Overall volatility (std): {analysis_df['percent_move_930_1030_x'].std():.4f}%")
print(f"Recent volatility (last 12 events): {analysis_df_sorted['rolling_volatility'].tail(1).iloc[0]:.4f}%")
print()

# Save insights to a file
with open('first_hour_insights.txt', 'w') as f:
    f.write("FIRST HOUR MOVEMENT INSIGHTS\n")
    f.write("=" * 50 + "\n\n")
    
    f.write(f"Total events analyzed: {len(analysis_df)}\n")
    f.write(f"Date range: {analysis_df['date'].min().strftime('%Y-%m-%d')} to {analysis_df['date'].max().strftime('%Y-%m-%d')}\n\n")
    
    f.write("KEY FINDINGS:\n")
    f.write(f"1. Average first hour movement: {analysis_df['percent_move_930_1030_x'].mean():.4f}%\n")
    f.write(f"2. Up movements: {direction_counts.get('Up', 0)} ({direction_counts.get('Up', 0)/len(analysis_df)*100:.1f}%)\n")
    f.write(f"3. Down movements: {direction_counts.get('Down', 0)} ({direction_counts.get('Down', 0)/len(analysis_df)*100:.1f}%)\n")
    f.write(f"4. Extreme movements (>1% or <-1%): {len(extreme_up) + len(extreme_down)} events\n")
    f.write(f"5. Overall volatility: {analysis_df['percent_move_930_1030_x'].std():.4f}%\n\n")
    
    f.write("TOP MOVEMENTS:\n")
    f.write("Largest up: " + str(top_movements.iloc[0].to_dict()) + "\n")
    f.write("Largest down: " + str(top_down_movements.iloc[0].to_dict()) + "\n")

print("Analysis complete! Check 'first_hour_insights.txt' for a summary of key findings.")