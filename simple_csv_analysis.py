import csv
import statistics
from collections import defaultdict

# Read the CSV data
data = []
with open('data/previuos_high_low.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)

print(f"Total data points: {len(data)}")
print(f"Columns: {list(data[0].keys())}")

# Analyze by different scenarios
print("\n" + "="*50)
print("ANALYSIS BY OPEN POSITION")
print("="*50)

# Group by open position
position_data = defaultdict(lambda: {'high_continuation': [], 'high_reversal': [], 'low_continuation': [], 'low_reversal': []})

for row in data:
    position = row['open_position']
    touch_type = row['touch_type']
    
    if touch_type == 'Previous High':
        position_data[position]['high_continuation'].append(float(row['continuation_move_pct']))
        position_data[position]['high_reversal'].append(float(row['reversal_move_pct']))
    elif touch_type == 'Previous Low':
        position_data[position]['low_continuation'].append(float(row['continuation_move_pct']))
        position_data[position]['low_reversal'].append(float(row['reversal_move_pct']))

for position, stats in position_data.items():
    print(f"\n{position}:")
    for metric, values in stats.items():
        if values:
            print(f"  {metric}: count={len(values)}, mean={statistics.mean(values):.4f}, median={statistics.median(values):.4f}")

print("\n" + "="*50)
print("ANALYSIS BY DAY OF WEEK")
print("="*50)

# Group by day of week
day_data = defaultdict(lambda: {'high_continuation': [], 'high_reversal': [], 'low_continuation': [], 'low_reversal': []})

for row in data:
    day = row['day_of_week']
    touch_type = row['touch_type']
    
    if touch_type == 'Previous High':
        day_data[day]['high_continuation'].append(float(row['continuation_move_pct']))
        day_data[day]['high_reversal'].append(float(row['reversal_move_pct']))
    elif touch_type == 'Previous Low':
        day_data[day]['low_continuation'].append(float(row['continuation_move_pct']))
        day_data[day]['low_reversal'].append(float(row['reversal_move_pct']))

for day, stats in day_data.items():
    print(f"\n{day}:")
    for metric, values in stats.items():
        if values:
            print(f"  {metric}: count={len(values)}, mean={statistics.mean(values):.4f}, median={statistics.median(values):.4f}")

print("\n" + "="*50)
print("OVERALL STATISTICS")
print("="*50)

# Overall statistics
overall_stats = {
    'high_continuation': [],
    'high_reversal': [],
    'low_continuation': [],
    'low_reversal': []
}

for row in data:
    touch_type = row['touch_type']
    
    if touch_type == 'Previous High':
        overall_stats['high_continuation'].append(float(row['continuation_move_pct']))
        overall_stats['high_reversal'].append(float(row['reversal_move_pct']))
    elif touch_type == 'Previous Low':
        overall_stats['low_continuation'].append(float(row['continuation_move_pct']))
        overall_stats['low_reversal'].append(float(row['reversal_move_pct']))

print("Overall Statistics:")
for metric, values in overall_stats.items():
    if values:
        print(f"  {metric}: count={len(values)}, mean={statistics.mean(values):.4f}, median={statistics.median(values):.4f}")

print("\n" + "="*50)
print("THINKSCRIPT DATABASE GENERATION")
print("="*50)

# Generate ThinkScript database
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
    for metric, values in overall_stats.items():
        if values:
            median_val = statistics.median(values)
            mean_val = statistics.mean(values)
            code += f"def {metric}_10min_median = {median_val:.4f};\n"
            code += f"def {metric}_10min_avg = {mean_val:.4f};\n"
    code += "\n"
    
    # Position-specific statistics
    code += "# Position-specific statistics\n"
    for position, stats in position_data.items():
        position_name = position.replace(" ", "_").lower()
        code += f"# {position} statistics\n"
        for metric, values in stats.items():
            if values:
                median_val = statistics.median(values)
                mean_val = statistics.mean(values)
                code += f"def {position_name}_{metric}_10min_median = {median_val:.4f};\n"
                code += f"def {position_name}_{metric}_10min_avg = {mean_val:.4f};\n"
        code += "\n"
    
    # Day-specific statistics
    code += "# Day-specific statistics\n"
    for day, stats in day_data.items():
        day_name = day.lower()
        code += f"# {day} statistics\n"
        for metric, values in stats.items():
            if values:
                median_val = statistics.median(values)
                mean_val = statistics.mean(values)
                code += f"def {day_name}_{metric}_10min_median = {median_val:.4f};\n"
                code += f"def {day_name}_{metric}_10min_avg = {mean_val:.4f};\n"
        code += "\n"
    
    return code

print("Generated ThinkScript Database:")
print(generate_think_script_code())

# Save the generated code to a file
with open('generated_think_script_database.txt', 'w') as f:
    f.write(generate_think_script_code())

print("\nDatabase saved to 'generated_think_script_database.txt'")