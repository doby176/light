import csv
from collections import defaultdict, Counter
from datetime import datetime

def analyze_first_hour_movements():
    # Read the CSV file
    data = []
    with open('data/event_analysis_metrics.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Focus on our columns of interest
            if row['percent_move_930_1030_x'] and row['direction_930_1030_x']:
                data.append({
                    'date': row['date'],
                    'event_type': row['event_type'],
                    'percent_move': float(row['percent_move_930_1030_x']),
                    'direction': row['direction_930_1030_x']
                })
    
    print("=== FIRST HOUR MOVEMENT ANALYSIS ===")
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
    
    # 2. Direction Analysis
    print("2. FIRST HOUR DIRECTION ANALYSIS:")
    direction_counts = Counter(row['direction'] for row in data)
    total_events = len(data)
    
    for direction, count in direction_counts.items():
        percentage = (count / total_events) * 100
        print(f"  {direction}: {count} events ({percentage:.1f}%)")
    print()
    
    # 3. Magnitude Analysis
    print("3. FIRST HOUR MAGNITUDE ANALYSIS:")
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
    
    # 4. Direction vs Magnitude
    print("4. DIRECTION vs MAGNITUDE:")
    up_movements = [row['percent_move'] for row in data if row['direction'] == 'Up']
    down_movements = [row['percent_move'] for row in data if row['direction'] == 'Down']
    
    if up_movements:
        avg_up = sum(up_movements) / len(up_movements)
        median_up = sorted(up_movements)[len(up_movements) // 2]
        max_up = max(up_movements)
        print(f"  UP movements ({len(up_movements)} events):")
        print(f"    Average: {avg_up:.4f}%")
        print(f"    Median: {median_up:.4f}%")
        print(f"    Max: {max_up:.4f}%")
    
    if down_movements:
        avg_down = sum(down_movements) / len(down_movements)
        median_down = sorted(down_movements)[len(down_movements) // 2]
        min_down = min(down_movements)
        print(f"  DOWN movements ({len(down_movements)} events):")
        print(f"    Average: {avg_down:.4f}%")
        print(f"    Median: {median_down:.4f}%")
        print(f"    Min: {min_down:.4f}%")
    print()
    
    # 5. Extreme Movements Analysis
    print("5. EXTREME MOVEMENTS (>1% or <-1%):")
    extreme_up = [row for row in data if row['direction'] == 'Up' and row['percent_move'] > 1]
    extreme_down = [row for row in data if row['direction'] == 'Down' and row['percent_move'] < -1]
    
    print(f"  Extreme up movements (>1%): {len(extreme_up)} events")
    print(f"  Extreme down movements (<-1%): {len(extreme_down)} events")
    print(f"  Total extreme movements: {len(extreme_up) + len(extreme_down)} ({(len(extreme_up) + len(extreme_down))/total_events*100:.1f}% of all events)")
    print()
    
    # 6. Top 10 Largest Movements
    print("6. TOP 10 LARGEST FIRST HOUR MOVEMENTS:")
    sorted_by_magnitude = sorted(data, key=lambda x: x['percent_move'], reverse=True)
    for i, row in enumerate(sorted_by_magnitude[:10], 1):
        print(f"  {i:2d}. {row['date']} | {row['event_type']} | {row['percent_move']:+.4f}% | {row['direction']}")
    print()
    
    print("7. TOP 10 LARGEST DOWNWARD FIRST HOUR MOVEMENTS:")
    sorted_by_magnitude_down = sorted(data, key=lambda x: x['percent_move'])
    for i, row in enumerate(sorted_by_magnitude_down[:10], 1):
        print(f"  {i:2d}. {row['date']} | {row['event_type']} | {row['percent_move']:+.4f}% | {row['direction']}")
    print()
    
    # 8. Event Type Performance
    print("8. EVENT TYPE PERFORMANCE (First Hour):")
    event_stats = defaultdict(lambda: {'count': 0, 'total_move': 0, 'up_count': 0, 'moves': []})
    
    for row in data:
        event_type = row['event_type']
        event_stats[event_type]['count'] += 1
        event_stats[event_type]['total_move'] += row['percent_move']
        event_stats[event_type]['moves'].append(row['percent_move'])
        if row['direction'] == 'Up':
            event_stats[event_type]['up_count'] += 1
    
    print("  Event Type | Count | Avg Move | Up Rate | Min | Max")
    print("  " + "-" * 60)
    for event_type, stats in sorted(event_stats.items()):
        avg_move = stats['total_move'] / stats['count']
        up_rate = (stats['up_count'] / stats['count']) * 100
        min_move = min(stats['moves'])
        max_move = max(stats['moves'])
        print(f"  {event_type:10s} | {stats['count']:5d} | {avg_move:+7.4f}% | {up_rate:6.1f}% | {min_move:+5.2f}% | {max_move:+5.2f}%")
    print()
    
    # 9. Time Period Analysis
    print("9. TIME PERIOD ANALYSIS:")
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
    
    # 10. Key Insights Summary
    print("10. KEY INSIGHTS SUMMARY:")
    print(f"  • Average first hour movement: {avg_movement:.4f}%")
    print(f"  • Market moves up {direction_counts.get('Up', 0)/total_events*100:.1f}% of the time in first hour")
    print(f"  • Market moves down {direction_counts.get('Down', 0)/total_events*100:.1f}% of the time in first hour")
    print(f"  • {len(extreme_up) + len(extreme_down)} extreme movements (>1% or <-1%) out of {total_events} total events")
    print(f"  • Most volatile event type: {max(event_stats.items(), key=lambda x: max(x[1]['moves']) - min(x[1]['moves']))[0]}")
    
    # Find most successful event type (highest up rate)
    most_successful = max(event_stats.items(), key=lambda x: x[1]['up_count'] / x[1]['count'])
    print(f"  • Event type with highest up rate: {most_successful[0]} ({most_successful[1]['up_count']/most_successful[1]['count']*100:.1f}%)")
    
    # Save insights to file
    with open('first_hour_insights.txt', 'w') as f:
        f.write("FIRST HOUR MOVEMENT INSIGHTS\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total events analyzed: {len(data)}\n")
        f.write(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n\n")
        
        f.write("KEY FINDINGS:\n")
        f.write(f"1. Average first hour movement: {avg_movement:.4f}%\n")
        f.write(f"2. Up movements: {direction_counts.get('Up', 0)} ({direction_counts.get('Up', 0)/total_events*100:.1f}%)\n")
        f.write(f"3. Down movements: {direction_counts.get('Down', 0)} ({direction_counts.get('Down', 0)/total_events*100:.1f}%)\n")
        f.write(f"4. Extreme movements (>1% or <-1%): {len(extreme_up) + len(extreme_down)} events\n")
        f.write(f"5. Overall volatility: {std_dev:.4f}%\n\n")
        
        f.write("TOP MOVEMENTS:\n")
        f.write(f"Largest up: {sorted_by_magnitude[0]['date']} | {sorted_by_magnitude[0]['event_type']} | {sorted_by_magnitude[0]['percent_move']:.4f}%\n")
        f.write(f"Largest down: {sorted_by_magnitude_down[0]['date']} | {sorted_by_magnitude_down[0]['event_type']} | {sorted_by_magnitude_down[0]['percent_move']:.4f}%\n")
    
    print("\nAnalysis complete! Check 'first_hour_insights.txt' for a summary of key findings.")

if __name__ == "__main__":
    analyze_first_hour_movements()