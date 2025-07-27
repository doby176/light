import csv
from collections import defaultdict, Counter
from datetime import datetime
import re

def analyze_premarket_levels():
    data = []
    with open('data/event_analysis_metrics.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['touched_premarket_level'] and row['returned_to_opposite_level']:
                data.append({
                    'date': row['date'],
                    'event_type': row['event_type'],
                    'touched_level': row['touched_premarket_level'],
                    'returned_to_opposite': row['returned_to_opposite_level'],
                    'data': row['data'],
                    'bin': row['bin']
                })
    
    print(f"Total events with premarket level data: {len(data)}")
    
    # Date range
    dates = [datetime.strptime(row['date'], '%Y-%m-%d') for row in data]
    min_date = min(dates)
    max_date = max(dates)
    print(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    
    # Basic statistics
    touched_levels = [row['touched_level'] for row in data]
    returned_to_opposite = [row['returned_to_opposite'] for row in data]
    
    touched_counter = Counter(touched_levels)
    returned_counter = Counter(returned_to_opposite)
    
    print(f"\n=== PREMARKET LEVEL TOUCH ANALYSIS ===")
    print(f"High level touches: {touched_counter.get('High', 0)} ({touched_counter.get('High', 0)/len(data)*100:.1f}%)")
    print(f"Low level touches: {touched_counter.get('Low', 0)} ({touched_counter.get('Low', 0)/len(data)*100:.1f}%)")
    
    print(f"\n=== RETURN TO OPPOSITE LEVEL ANALYSIS ===")
    print(f"Returned to opposite: {returned_counter.get('Yes', 0)} ({returned_counter.get('Yes', 0)/len(data)*100:.1f}%)")
    print(f"Did not return: {returned_counter.get('No', 0)} ({returned_counter.get('No', 0)/len(data)*100:.1f}%)")
    
    # Event type analysis
    print(f"\n=== EVENT TYPE ANALYSIS ===")
    event_type_stats = defaultdict(lambda: {'total': 0, 'high_touches': 0, 'low_touches': 0, 'returned': 0, 'not_returned': 0})
    
    for row in data:
        event_type = row['event_type']
        event_type_stats[event_type]['total'] += 1
        
        if row['touched_level'] == 'High':
            event_type_stats[event_type]['high_touches'] += 1
        elif row['touched_level'] == 'Low':
            event_type_stats[event_type]['low_touches'] += 1
            
        if row['returned_to_opposite'] == 'Yes':
            event_type_stats[event_type]['returned'] += 1
        elif row['returned_to_opposite'] == 'No':
            event_type_stats[event_type]['not_returned'] += 1
    
    for event_type, stats in event_type_stats.items():
        print(f"\n{event_type} Events ({stats['total']} total):")
        print(f"  High touches: {stats['high_touches']} ({stats['high_touches']/stats['total']*100:.1f}%)")
        print(f"  Low touches: {stats['low_touches']} ({stats['low_touches']/stats['total']*100:.1f}%)")
        print(f"  Returned to opposite: {stats['returned']} ({stats['returned']/stats['total']*100:.1f}%)")
        print(f"  Did not return: {stats['not_returned']} ({stats['not_returned']/stats['total']*100:.1f}%)")
    
    # Bin analysis
    print(f"\n=== MARKET CONDITION (BIN) ANALYSIS ===")
    bin_stats = defaultdict(lambda: {'total': 0, 'high_touches': 0, 'low_touches': 0, 'returned': 0, 'not_returned': 0})
    
    for row in data:
        bin_category = row['bin']
        if bin_category:  # Only include if bin is not empty
            bin_stats[bin_category]['total'] += 1
            
            if row['touched_level'] == 'High':
                bin_stats[bin_category]['high_touches'] += 1
            elif row['touched_level'] == 'Low':
                bin_stats[bin_category]['low_touches'] += 1
                
            if row['returned_to_opposite'] == 'Yes':
                bin_stats[bin_category]['returned'] += 1
            elif row['returned_to_opposite'] == 'No':
                bin_stats[bin_category]['not_returned'] += 1
    
    for bin_category, stats in bin_stats.items():
        if stats['total'] > 0:
            print(f"\n{bin_category} Market Conditions ({stats['total']} events):")
            print(f"  High touches: {stats['high_touches']} ({stats['high_touches']/stats['total']*100:.1f}%)")
            print(f"  Low touches: {stats['low_touches']} ({stats['low_touches']/stats['total']*100:.1f}%)")
            print(f"  Returned to opposite: {stats['returned']} ({stats['returned']/stats['total']*100:.1f}%)")
            print(f"  Did not return: {stats['not_returned']} ({stats['not_returned']/stats['total']*100:.1f}%)")
    
    # Combined analysis: Event type vs Bin
    print(f"\n=== EVENT TYPE vs MARKET CONDITION ANALYSIS ===")
    combined_stats = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'high_touches': 0, 'low_touches': 0, 'returned': 0, 'not_returned': 0}))
    
    for row in data:
        event_type = row['event_type']
        bin_category = row['bin']
        if bin_category:  # Only include if bin is not empty
            combined_stats[event_type][bin_category]['total'] += 1
            
            if row['touched_level'] == 'High':
                combined_stats[event_type][bin_category]['high_touches'] += 1
            elif row['touched_level'] == 'Low':
                combined_stats[event_type][bin_category]['low_touches'] += 1
                
            if row['returned_to_opposite'] == 'Yes':
                combined_stats[event_type][bin_category]['returned'] += 1
            elif row['returned_to_opposite'] == 'No':
                combined_stats[event_type][bin_category]['not_returned'] += 1
    
    for event_type, bins in combined_stats.items():
        print(f"\n{event_type} by Market Condition:")
        for bin_category, stats in bins.items():
            if stats['total'] > 0:
                print(f"  {bin_category}: {stats['total']} events")
                print(f"    High touches: {stats['high_touches']} ({stats['high_touches']/stats['total']*100:.1f}%)")
                print(f"    Low touches: {stats['low_touches']} ({stats['low_touches']/stats['total']*100:.1f}%)")
                print(f"    Returned to opposite: {stats['returned']} ({stats['returned']/stats['total']*100:.1f}%)")
                print(f"    Did not return: {stats['not_returned']} ({stats['not_returned']/stats['total']*100:.1f}%)")
    
    # Data content analysis
    print(f"\n=== DATA CONTENT ANALYSIS ===")
    data_content_stats = defaultdict(lambda: {'total': 0, 'high_touches': 0, 'low_touches': 0, 'returned': 0, 'not_returned': 0})
    
    for row in data:
        data_content = row['data']
        if data_content:  # Only include if data is not empty
            data_content_stats[data_content]['total'] += 1
            
            if row['touched_level'] == 'High':
                data_content_stats[data_content]['high_touches'] += 1
            elif row['touched_level'] == 'Low':
                data_content_stats[data_content]['low_touches'] += 1
                
            if row['returned_to_opposite'] == 'Yes':
                data_content_stats[data_content]['returned'] += 1
            elif row['returned_to_opposite'] == 'No':
                data_content_stats[data_content]['not_returned'] += 1
    
    # Show top data contents by frequency
    sorted_data_contents = sorted(data_content_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    print(f"Top 10 most frequent data contents:")
    for i, (content, stats) in enumerate(sorted_data_contents[:10]):
        print(f"  {i+1}. {content[:50]}... ({stats['total']} events)")
        print(f"     High touches: {stats['high_touches']} ({stats['high_touches']/stats['total']*100:.1f}%)")
        print(f"     Low touches: {stats['low_touches']} ({stats['low_touches']/stats['total']*100:.1f}%)")
        print(f"     Returned to opposite: {stats['returned']} ({stats['returned']/stats['total']*100:.1f}%)")
        print(f"     Did not return: {stats['not_returned']} ({stats['not_returned']/stats['total']*100:.1f}%)")
    
    # Yearly analysis
    print(f"\n=== YEARLY ANALYSIS ===")
    yearly_stats = defaultdict(lambda: {'total': 0, 'high_touches': 0, 'low_touches': 0, 'returned': 0, 'not_returned': 0})
    
    for row in data:
        year = datetime.strptime(row['date'], '%Y-%m-%d').year
        yearly_stats[year]['total'] += 1
        
        if row['touched_level'] == 'High':
            yearly_stats[year]['high_touches'] += 1
        elif row['touched_level'] == 'Low':
            yearly_stats[year]['low_touches'] += 1
            
        if row['returned_to_opposite'] == 'Yes':
            yearly_stats[year]['returned'] += 1
        elif row['returned_to_opposite'] == 'No':
            yearly_stats[year]['not_returned'] += 1
    
    for year in sorted(yearly_stats.keys()):
        stats = yearly_stats[year]
        print(f"\n{year} ({stats['total']} events):")
        print(f"  High touches: {stats['high_touches']} ({stats['high_touches']/stats['total']*100:.1f}%)")
        print(f"  Low touches: {stats['low_touches']} ({stats['low_touches']/stats['total']*100:.1f}%)")
        print(f"  Returned to opposite: {stats['returned']} ({stats['returned']/stats['total']*100:.1f}%)")
        print(f"  Did not return: {stats['not_returned']} ({stats['not_returned']/stats['total']*100:.1f}%)")
    
    # Write summary to file
    with open('premarket_level_insights.txt', 'w') as f:
        f.write("PREMARKET LEVEL ANALYSIS INSIGHTS\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total events analyzed: {len(data)}\n")
        f.write(f"Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n\n")
        
        f.write("OVERALL STATISTICS:\n")
        f.write(f"High level touches: {touched_counter.get('High', 0)} ({touched_counter.get('High', 0)/len(data)*100:.1f}%)\n")
        f.write(f"Low level touches: {touched_counter.get('Low', 0)} ({touched_counter.get('Low', 0)/len(data)*100:.1f}%)\n")
        f.write(f"Returned to opposite level: {returned_counter.get('Yes', 0)} ({returned_counter.get('Yes', 0)/len(data)*100:.1f}%)\n")
        f.write(f"Did not return: {returned_counter.get('No', 0)} ({returned_counter.get('No', 0)/len(data)*100:.1f}%)\n\n")
        
        f.write("KEY FINDINGS:\n")
        f.write("1. Market behavior around premarket levels\n")
        f.write("2. Frequency of touching high vs low premarket levels\n")
        f.write("3. Probability of returning to opposite levels\n")
        f.write("4. Event type performance patterns\n")
        f.write("5. Market condition impact on premarket level behavior\n")
        f.write("6. Yearly trends in premarket level interactions\n")

if __name__ == "__main__":
    analyze_premarket_levels()