#!/usr/bin/env python3
import csv
import statistics
from collections import defaultdict

def analyze_csv_data():
    # Data storage
    data = {
        'overall': {'high_continuation_10min': [], 'high_reversal_10min': [], 
                   'low_continuation_10min': [], 'low_reversal_10min': [],
                   'high_continuation_60min': [], 'high_reversal_60min': [], 
                   'low_continuation_60min': [], 'low_reversal_60min': []},
        'position': defaultdict(lambda: {'high_continuation_10min': [], 'high_reversal_10min': [], 
                                        'low_continuation_10min': [], 'low_reversal_10min': [],
                                        'high_continuation_60min': [], 'high_reversal_60min': [], 
                                        'low_continuation_60min': [], 'low_reversal_60min': []}),
        'day': defaultdict(lambda: {'high_continuation_10min': [], 'high_reversal_10min': [], 
                                   'low_continuation_10min': [], 'low_reversal_10min': [],
                                   'high_continuation_60min': [], 'high_reversal_60min': [], 
                                   'low_continuation_60min': [], 'low_reversal_60min': []})
    }
    
    # Read CSV file
    with open('data/previuos_high_low.csv', 'r') as file:
        reader = csv.DictReader(file)
        count = 0
        
        for row in reader:
            count += 1
            
            # Extract values
            touch_type = row['touch_type']
            open_position = row['open_position']
            day_of_week = row['day_of_week']
            
            # 10-minute moves
            continuation_10min = float(row['continuation_move_pct'])
            reversal_10min = float(row['reversal_move_pct'])
            
            # 60-minute moves
            continuation_60min = float(row['continuation_move_pct_60min'])
            reversal_60min = float(row['reversal_move_pct_60min'])
            
            # Store data based on touch type
            if touch_type == 'Previous High':
                # Overall data
                data['overall']['high_continuation_10min'].append(continuation_10min)
                data['overall']['high_reversal_10min'].append(reversal_10min)
                data['overall']['high_continuation_60min'].append(continuation_60min)
                data['overall']['high_reversal_60min'].append(reversal_60min)
                
                # Position-specific data
                data['position'][open_position]['high_continuation_10min'].append(continuation_10min)
                data['position'][open_position]['high_reversal_10min'].append(reversal_10min)
                data['position'][open_position]['high_continuation_60min'].append(continuation_60min)
                data['position'][open_position]['high_reversal_60min'].append(reversal_60min)
                
                # Day-specific data
                data['day'][day_of_week]['high_continuation_10min'].append(continuation_10min)
                data['day'][day_of_week]['high_reversal_10min'].append(reversal_10min)
                data['day'][day_of_week]['high_continuation_60min'].append(continuation_60min)
                data['day'][day_of_week]['high_reversal_60min'].append(reversal_60min)
                
            elif touch_type == 'Previous Low':
                # Overall data
                data['overall']['low_continuation_10min'].append(continuation_10min)
                data['overall']['low_reversal_10min'].append(reversal_10min)
                data['overall']['low_continuation_60min'].append(continuation_60min)
                data['overall']['low_reversal_60min'].append(reversal_60min)
                
                # Position-specific data
                data['position'][open_position]['low_continuation_10min'].append(continuation_10min)
                data['position'][open_position]['low_reversal_10min'].append(reversal_10min)
                data['position'][open_position]['low_continuation_60min'].append(continuation_60min)
                data['position'][open_position]['low_reversal_60min'].append(reversal_60min)
                
                # Day-specific data
                data['day'][day_of_week]['low_continuation_10min'].append(continuation_10min)
                data['day'][day_of_week]['low_reversal_10min'].append(reversal_10min)
                data['day'][day_of_week]['low_continuation_60min'].append(continuation_60min)
                data['day'][day_of_week]['low_reversal_60min'].append(reversal_60min)
    
    print(f"Total data points: {count}")
    print("=" * 50)
    
    # Calculate statistics
    def calculate_stats(values):
        if not values:
            return 0, 0, 0
        return len(values), statistics.mean(values), statistics.median(values)
    
    # Overall statistics
    print("OVERALL STATISTICS (10-MINUTE MOVES)")
    print("=" * 50)
    for move_type in ['high_continuation_10min', 'high_reversal_10min', 'low_continuation_10min', 'low_reversal_10min']:
        count, mean, median = calculate_stats(data['overall'][move_type])
        print(f"{move_type}: count={count}, mean={mean:.4f}, median={median:.4f}")
    
    print("\nOVERALL STATISTICS (60-MINUTE MOVES)")
    print("=" * 50)
    for move_type in ['high_continuation_60min', 'high_reversal_60min', 'low_continuation_60min', 'low_reversal_60min']:
        count, mean, median = calculate_stats(data['overall'][move_type])
        print(f"{move_type}: count={count}, mean={mean:.4f}, median={median:.4f}")
    
    # Position-specific statistics
    print("\nANALYSIS BY OPEN POSITION (10-MINUTE MOVES)")
    print("=" * 50)
    for position in sorted(data['position'].keys()):
        print(f"\n{position}:")
        for move_type in ['high_continuation_10min', 'high_reversal_10min', 'low_continuation_10min', 'low_reversal_10min']:
            count, mean, median = calculate_stats(data['position'][position][move_type])
            if count > 0:
                print(f"  {move_type}: count={count}, mean={mean:.4f}, median={median:.4f}")
    
    print("\nANALYSIS BY OPEN POSITION (60-MINUTE MOVES)")
    print("=" * 50)
    for position in sorted(data['position'].keys()):
        print(f"\n{position}:")
        for move_type in ['high_continuation_60min', 'high_reversal_60min', 'low_continuation_60min', 'low_reversal_60min']:
            count, mean, median = calculate_stats(data['position'][position][move_type])
            if count > 0:
                print(f"  {move_type}: count={count}, mean={mean:.4f}, median={median:.4f}")
    
    # Day-specific statistics
    print("\nANALYSIS BY DAY OF WEEK (10-MINUTE MOVES)")
    print("=" * 50)
    for day in sorted(data['day'].keys()):
        print(f"\n{day}:")
        for move_type in ['high_continuation_10min', 'high_reversal_10min', 'low_continuation_10min', 'low_reversal_10min']:
            count, mean, median = calculate_stats(data['day'][day][move_type])
            if count > 0:
                print(f"  {move_type}: count={count}, mean={mean:.4f}, median={median:.4f}")
    
    print("\nANALYSIS BY DAY OF WEEK (60-MINUTE MOVES)")
    print("=" * 50)
    for day in sorted(data['day'].keys()):
        print(f"\n{day}:")
        for move_type in ['high_continuation_60min', 'high_reversal_60min', 'low_continuation_60min', 'low_reversal_60min']:
            count, mean, median = calculate_stats(data['day'][day][move_type])
            if count > 0:
                print(f"  {move_type}: count={count}, mean={mean:.4f}, median={median:.4f}")
    
    # Generate HTML statistics for the article
    print("\n" + "=" * 50)
    print("GENERATING HTML STATISTICS FOR ARTICLE")
    print("=" * 50)
    
    # Overall 60-minute statistics
    print("\n<!-- 60-MINUTE OVERALL STATISTICS -->")
    for move_type in ['high_continuation_60min', 'high_reversal_60min', 'low_continuation_60min', 'low_reversal_60min']:
        count, mean, median = calculate_stats(data['overall'][move_type])
        print(f"<!-- {move_type}: count={count}, mean={mean:.4f}, median={median:.4f} -->")
    
    # Position-specific 60-minute statistics
    print("\n<!-- 60-MINUTE POSITION-SPECIFIC STATISTICS -->")
    for position in sorted(data['position'].keys()):
        print(f"\n<!-- {position} 60-MINUTE STATS -->")
        for move_type in ['high_continuation_60min', 'high_reversal_60min', 'low_continuation_60min', 'low_reversal_60min']:
            count, mean, median = calculate_stats(data['position'][position][move_type])
            if count > 0:
                print(f"<!-- {move_type}: count={count}, mean={mean:.4f}, median={median:.4f} -->")
    
    # Day-specific 60-minute statistics
    print("\n<!-- 60-MINUTE DAY-SPECIFIC STATISTICS -->")
    for day in sorted(data['day'].keys()):
        print(f"\n<!-- {day} 60-MINUTE STATS -->")
        for move_type in ['high_continuation_60min', 'high_reversal_60min', 'low_continuation_60min', 'low_reversal_60min']:
            count, mean, median = calculate_stats(data['day'][day][move_type])
            if count > 0:
                print(f"<!-- {move_type}: count={count}, mean={mean:.4f}, median={median:.4f} -->")

if __name__ == "__main__":
    analyze_csv_data()