import csv
from collections import defaultdict, Counter
from datetime import datetime
import re

def analyze_extreme_movements():
    # Read the CSV file
    data = []
    with open('data/event_analysis_metrics.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Focus on our columns of interest
            if row['percent_move_930_959_extreme'] and row['direction_930_959_extreme']:
                data.append({
                    'date': row['date'],
                    'event_type': row['event_type'],
                    'percent_move': float(row['percent_move_930_959_extreme']),
                    'direction': row['direction_930_959_extreme'],
                    'data': row['data'],
                    'bin': row['bin']
                })
    
    print("=== EXTREME FIRST 29 MINUTES MOVEMENT ANALYSIS (9:30-9:59 AM) ===")
    print(f"Total events analyzed: {len(data)}")
    
    if not data:
        print("No data found!")
        return
    
    # Date range
    dates = [datetime.strptime(row['date'], '%Y-%m-%d') for row in data]
    min_date = min(dates)
    max_date = max(dates)
    print(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print()
    
    # 1. Event Type Distribution
    print("1. EVENT TYPE DISTRIBUTION:")
    event_counts = Counter(row['event_type'] for row in data)
    for event_type, count in event_counts.most_common():
        print(f"  {event_type}: {count} events")
    print()
    
    # 2. Bin Distribution Analysis
    print("2. BIN DISTRIBUTION ANALYSIS:")
    bin_counts = Counter(row['bin'] for row in data if row['bin'])
    print("Bin categories and their frequencies:")
    for bin_category, count in bin_counts.most_common():
        print(f"  {bin_category}: {count} events")
    print()
    
    # 3. Direction Analysis
    print("3. EXTREME FIRST 29 MINUTES DIRECTION ANALYSIS:")
    direction_counts = Counter(row['direction'] for row in data)
    total_events = len(data)
    
    for direction, count in direction_counts.items():
        percentage = (count / total_events) * 100
        print(f"  {direction}: {count} events ({percentage:.1f}%)")
    print()
    
    # 4. Magnitude Analysis
    print("4. EXTREME FIRST 29 MINUTES MAGNITUDE ANALYSIS:")
    movements = [row['percent_move'] for row in data]
    movements.sort()
    
    avg_movement = sum(movements) / len(movements)
    median_movement = movements[len(movements) // 2]
    min_movement = min(movements)
    max_movement = max(movements)
    
    # Calculate standard deviation
    variance = sum((x - avg_movement) ** 2 for x in movements) / len(movements)
    std_dev = variance ** 0.5
    
    print(f"  Average movement: {avg_movement:.4f}%")
    print(f"  Median movement: {median_movement:.4f}%")
    print(f"  Standard deviation: {std_dev:.4f}%")
    print(f"  Min movement: {min_movement:.4f}%")
    print(f"  Max movement: {max_movement:.4f}%")
    print()
    
    # 5. Event Type vs Bin Analysis
    print("5. EVENT TYPE vs BIN ANALYSIS (Extreme Movements):")
    event_bin_stats = defaultdict(lambda: defaultdict(list))
    
    for row in data:
        if row['bin']:
            event_bin_stats[row['event_type']][row['bin']].append(row['percent_move'])
    
    print("Performance by Event Type and Bin:")
    for event_type in sorted(event_bin_stats.keys()):
        print(f"\n  {event_type}:")
        for bin_category in sorted(event_bin_stats[event_type].keys()):
            moves = event_bin_stats[event_type][bin_category]
            avg_move = sum(moves) / len(moves)
            up_count = sum(1 for row in data if row['event_type'] == event_type and row['bin'] == bin_category and row['direction'] == 'Up')
            total_count = len(moves)
            up_rate = (up_count / total_count * 100) if total_count > 0 else 0
            print(f"    {bin_category}: {total_count} events, avg: {avg_move:+.4f}%, up rate: {up_rate:.1f}%")
    print()
    
    # 6. Data Content Analysis
    print("6. DATA CONTENT ANALYSIS:")
    print("Sample data entries for each event type:")
    event_data_samples = defaultdict(list)
    
    for row in data:
        if row['data'] and len(event_data_samples[row['event_type']]) < 3:
            event_data_samples[row['event_type']].append(row['data'])
    
    for event_type, samples in event_data_samples.items():
        print(f"\n  {event_type} data samples:")
        for i, sample in enumerate(samples, 1):
            print(f"    {i}. {sample[:100]}{'...' if len(sample) > 100 else ''}")
    print()
    
    # 7. Bin Performance Analysis
    print("7. BIN PERFORMANCE ANALYSIS (Extreme Movements):")
    bin_performance = defaultdict(lambda: {'count': 0, 'total_move': 0, 'up_count': 0, 'moves': []})
    
    for row in data:
        if row['bin']:
            bin_category = row['bin']
            bin_performance[bin_category]['count'] += 1
            bin_performance[bin_category]['total_move'] += row['percent_move']
            bin_performance[bin_category]['moves'].append(row['percent_move'])
            if row['direction'] == 'Up':
                bin_performance[bin_category]['up_count'] += 1
    
    print("Performance by Bin Category:")
    print("  Bin Category | Count | Avg Move | Up Rate | Min | Max")
    print("  " + "-" * 70)
    for bin_category, stats in sorted(bin_performance.items()):
        avg_move = stats['total_move'] / stats['count']
        up_rate = (stats['up_count'] / stats['count']) * 100
        min_move = min(stats['moves'])
        max_move = max(stats['moves'])
        print(f"  {bin_category:12s} | {stats['count']:5d} | {avg_move:+8.4f}% | {up_rate:6.1f}% | {min_move:+5.2f}% | {max_move:+5.2f}%")
    print()
    
    # 8. Super Extreme Events Analysis (>2% or <-2%)
    print("8. SUPER EXTREME EVENTS (>2% or <-2%):")
    super_extreme_up = [row for row in data if row['direction'] == 'Up' and row['percent_move'] > 2]
    super_extreme_down = [row for row in data if row['direction'] == 'Down' and row['percent_move'] < -2]
    
    print(f"  Super extreme up movements (>2%): {len(super_extreme_up)} events")
    print(f"  Super extreme down movements (<-2%): {len(super_extreme_down)} events")
    print(f"  Total super extreme movements: {len(super_extreme_up) + len(super_extreme_down)} ({(len(super_extreme_up) + len(super_extreme_down))/total_events*100:.1f}% of all events)")
    print()
    
    # 9. Top 10 Largest Extreme Movements
    print("9. TOP 10 LARGEST EXTREME FIRST 29 MINUTES MOVEMENTS:")
    sorted_by_magnitude = sorted(data, key=lambda x: x['percent_move'], reverse=True)
    for i, row in enumerate(sorted_by_magnitude[:10], 1):
        print(f"  {i:2d}. {row['date']} | {row['event_type']} | {row['percent_move']:+.4f}% | {row['direction']} | {row['bin']}")
    print()
    
    print("10. TOP 10 LARGEST DOWNWARD EXTREME FIRST 29 MINUTES MOVEMENTS:")
    sorted_by_magnitude_down = sorted(data, key=lambda x: x['percent_move'])
    for i, row in enumerate(sorted_by_magnitude_down[:10], 1):
        print(f"  {i:2d}. {row['date']} | {row['event_type']} | {row['percent_move']:+.4f}% | {row['direction']} | {row['bin']}")
    print()
    
    # 10. Event Type Performance
    print("11. EVENT TYPE PERFORMANCE (Extreme First 29 Minutes):")
    event_performance = defaultdict(lambda: {'count': 0, 'total_move': 0, 'up_count': 0, 'moves': []})
    
    for row in data:
        event_type = row['event_type']
        event_performance[event_type]['count'] += 1
        event_performance[event_type]['total_move'] += row['percent_move']
        event_performance[event_type]['moves'].append(row['percent_move'])
        if row['direction'] == 'Up':
            event_performance[event_type]['up_count'] += 1
    
    print("  Event Type | Count | Avg Move | Up Rate | Min | Max")
    print("  " + "-" * 60)
    for event_type, stats in sorted(event_performance.items()):
        avg_move = stats['total_move'] / stats['count']
        up_rate = (stats['up_count'] / stats['count']) * 100
        min_move = min(stats['moves'])
        max_move = max(stats['moves'])
        print(f"  {event_type:10s} | {stats['count']:5d} | {avg_move:+7.4f}% | {up_rate:6.1f}% | {min_move:+5.2f}% | {max_move:+5.2f}%")
    print()
    
    # 11. Time Period Analysis
    print("12. TIME PERIOD ANALYSIS:")
    year_stats = defaultdict(lambda: {'count': 0, 'total_move': 0, 'up_count': 0})
    
    for row in data:
        year = datetime.strptime(row['date'], '%Y-%m-%d').year
        year_stats[year]['count'] += 1
        year_stats[year]['total_move'] += row['percent_move']
        if row['direction'] == 'Up':
            year_stats[year]['up_count'] += 1
    
    print("  Year | Count | Avg Move | Up Rate")
    print("  " + "-" * 35)
    for year in sorted(year_stats.keys()):
        stats = year_stats[year]
        avg_move = stats['total_move'] / stats['count']
        up_rate = (stats['up_count'] / stats['count']) * 100
        print(f"  {year} | {stats['count']:5d} | {avg_move:+8.4f}% | {up_rate:6.1f}%")
    print()
    
    # 12. Data Pattern Analysis
    print("13. DATA PATTERN ANALYSIS:")
    print("Extracting key information from data field:")
    
    # Analyze NFP data patterns
    nfp_data = [row['data'] for row in data if row['event_type'] == 'NFP' and row['data']]
    if nfp_data:
        print("\n  NFP Data Patterns:")
        jobs_patterns = Counter()
        for entry in nfp_data:
            # Extract jobs added number
            jobs_match = re.search(r'Jobs added=([^,]+)', entry)
            if jobs_match:
                jobs_str = jobs_match.group(1)
                jobs_patterns[jobs_str] += 1
        
        print("  Jobs added categories:")
        for jobs, count in jobs_patterns.most_common():
            print(f"    {jobs}: {count} events")
    
    # Analyze CPI/PPI data patterns
    inflation_data = [row['data'] for row in data if row['event_type'] in ['CPI', 'PPI'] and row['data']]
    if inflation_data:
        print("\n  CPI/PPI Data Patterns:")
        print("  Sample entries:")
        for i, entry in enumerate(inflation_data[:5], 1):
            print(f"    {i}. {entry[:80]}{'...' if len(entry) > 80 else ''}")
    print()
    
    # 13. Combined Analysis: Event Type + Bin + Direction
    print("14. COMBINED ANALYSIS (Event Type + Bin + Direction):")
    combined_stats = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'total_move': 0}))
    
    for row in data:
        if row['bin']:
            key = f"{row['event_type']}_{row['bin']}"
            combined_stats[key][row['direction']]['count'] += 1
            combined_stats[key][row['direction']]['total_move'] += row['percent_move']
    
    print("Performance by Event Type + Bin + Direction:")
    for key in sorted(combined_stats.keys()):
        event_type, bin_category = key.split('_', 1)
        print(f"\n  {event_type} - {bin_category}:")
        for direction in ['Up', 'Down']:
            if direction in combined_stats[key]:
                stats = combined_stats[key][direction]
                avg_move = stats['total_move'] / stats['count']
                print(f"    {direction}: {stats['count']} events, avg: {avg_move:+.4f}%")
    print()
    
    # 14. Key Insights Summary
    print("15. KEY INSIGHTS SUMMARY:")
    print(f"  • Total extreme events analyzed: {len(data)}")
    print(f"  • Average extreme movement: {avg_movement:.4f}%")
    print(f"  • Market moves up {direction_counts.get('Up', 0)/total_events*100:.1f}% of the time in extreme first 29 minutes")
    print(f"  • Number of unique bin categories: {len(bin_counts)}")
    
    # Find most successful bin category
    if bin_performance:
        most_successful_bin = max(bin_performance.items(), key=lambda x: x[1]['up_count'] / x[1]['count'])
        print(f"  • Most successful bin category: {most_successful_bin[0]} ({most_successful_bin[1]['up_count']/most_successful_bin[1]['count']*100:.1f}% up rate)")
    
    # Find most volatile bin category
    if bin_performance:
        most_volatile_bin = max(bin_performance.items(), key=lambda x: max(x[1]['moves']) - min(x[1]['moves']))
        print(f"  • Most volatile bin category: {most_volatile_bin[0]} (range: {min(most_volatile_bin[1]['moves']):.2f}% to {max(most_volatile_bin[1]['moves']):.2f}%)")
    
    # Save comprehensive insights to file
    with open('extreme_movements_insights.txt', 'w') as f:
        f.write("EXTREME FIRST 29 MINUTES MOVEMENT INSIGHTS\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Total extreme events analyzed: {len(data)}\n")
        f.write(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n\n")
        
        f.write("KEY FINDINGS:\n")
        f.write(f"1. Average extreme movement: {avg_movement:.4f}%\n")
        f.write(f"2. Up movements: {direction_counts.get('Up', 0)} ({direction_counts.get('Up', 0)/total_events*100:.1f}%)\n")
        f.write(f"3. Down movements: {direction_counts.get('Down', 0)} ({direction_counts.get('Down', 0)/total_events*100:.1f}%)\n")
        f.write(f"4. Number of bin categories: {len(bin_counts)}\n")
        f.write(f"5. Overall volatility: {std_dev:.4f}%\n\n")
        
        f.write("BIN CATEGORIES:\n")
        for bin_category, count in bin_counts.most_common():
            f.write(f"  {bin_category}: {count} events\n")
        
        f.write("\nEVENT TYPE PERFORMANCE:\n")
        for event_type, stats in sorted(event_performance.items()):
            avg_move = stats['total_move'] / stats['count']
            up_rate = (stats['up_count'] / stats['count']) * 100
            f.write(f"  {event_type}: {stats['count']} events, avg: {avg_move:+.4f}%, up rate: {up_rate:.1f}%\n")
    
    print("\nExtreme movements analysis complete! Check 'extreme_movements_insights.txt' for detailed findings.")

if __name__ == "__main__":
    analyze_extreme_movements()