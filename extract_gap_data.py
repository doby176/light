#!/usr/bin/env python3
"""
Extract gap analysis data from CSV without pandas dependency
Generate ThinkScript data arrays with real historical values
"""

import csv
from datetime import datetime
from collections import defaultdict

def load_gap_data(csv_file_path):
    """Load gap data from CSV file"""
    print(f"Loading gap data from {csv_file_path}...")

    data = []
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Parse date and get day of week
                date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                day_of_week = date_obj.strftime('%A')  # Monday, Tuesday, etc.

                # Map day to number (0=Monday, 1=Tuesday, etc.)
                day_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4}
                day_num = day_mapping.get(day_of_week, 0)

                # Map gap direction to number (1=up, -1=down)
                gap_dir_num = 1 if row['gap_direction'] == 'up' else -1

                # Parse numeric values
                filled = row['filled'].lower() == 'true'
                reversal_after_fill = row['reversal_after_fill'] == '1.0' if row['reversal_after_fill'] else False
                
                # CORRECTED MAPPING to match ThinkOrSwim indicator:
                # ZONE 1: Move before gap fill (from max_move_gap_direction_first_30min_pct) - ONLY FILLED GAPS
                move_before_fill = float(row['max_move_gap_direction_first_30min_pct']) if row['max_move_gap_direction_first_30min_pct'] else 0
                
                # ZONE 2: Stop out for unfilled gaps (from max_move_gap_direction_first_30min_pct for unfilled only)
                max_move_unfilled = float(row['max_move_gap_direction_first_30min_pct']) if row['max_move_gap_direction_first_30min_pct'] else 0
                
                # ZONE 3: Move after gap fill (from move_before_reversal_fill_direction_pct) - ONLY GAPS WITH REVERSALS
                move_after_fill = float(row['move_before_reversal_fill_direction_pct']) if row['move_before_reversal_fill_direction_pct'] else 0

                data.append({
                    'gap_size_bin': row['gap_size_bin'],
                    'day_num': day_num,
                    'gap_dir_num': gap_dir_num,
                    'filled': filled,
                    'reversal_after_fill': reversal_after_fill,
                    'move_before_fill': move_before_fill,
                    'max_move_unfilled': max_move_unfilled,
                    'move_after_fill': move_after_fill
                })
            except (ValueError, KeyError) as e:
                continue  # Skip rows with parsing errors

    print(f"Loaded {len(data)} valid records")
    return data

def calculate_metrics(data):
    """Calculate gap fill rates and move statistics"""

    # Group data by bin, day, and direction
    grouped = defaultdict(list)
    for record in data:
        key = (record['gap_size_bin'], record['day_num'], record['gap_dir_num'])
        grouped[key].append(record)

    results = {}

    # Define gap size bins for mapping
    bin_mapping = {
        '0.15-0.35%': 1,
        '0.35-0.5%': 2,
        '0.5-1%': 3,
        '1-1.5%': 4,
        '1.5%+': 5
    }

    for (bin_name, day_num, gap_dir), records in grouped.items():
        if len(records) < 5:  # Skip if too few samples
            continue

        bin_num = bin_mapping.get(bin_name, 1)

        # Calculate fill rate
        filled_count = sum(1 for r in records if r['filled'])
        fill_rate = (filled_count / len(records)) * 100

        # ZONE 1: Calculate median/average move before fill (for FILLED gaps only)
        filled_records = [r for r in records if r['filled']]
        if filled_records:
            moves_before_fill = [r['move_before_fill'] for r in filled_records if r['move_before_fill'] > 0]
            median_move_before_fill = sorted(moves_before_fill)[len(moves_before_fill)//2] if moves_before_fill else 0
            avg_move_before_fill = sum(moves_before_fill) / len(moves_before_fill) if moves_before_fill else 0
        else:
            median_move_before_fill = 0
            avg_move_before_fill = 0

        # ZONE 2: Calculate median/average max move for unfilled gaps (stop levels)
        unfilled_records = [r for r in records if not r['filled']]
        if unfilled_records:
            moves = [r['max_move_unfilled'] for r in unfilled_records if r['max_move_unfilled'] > 0]
            median_max_unfilled = sorted(moves)[len(moves)//2] if moves else 0
            avg_max_unfilled = sum(moves) / len(moves) if moves else 0
        else:
            median_max_unfilled = 0
            avg_max_unfilled = 0

        # ZONE 3: Calculate median/average move after fill (for filled gaps with reversals only)
        filled_with_reversal_records = [r for r in records if r['filled'] and r['reversal_after_fill']]
        if filled_with_reversal_records:
            moves = [r['move_after_fill'] for r in filled_with_reversal_records if r['move_after_fill'] > 0]
            median_move_after_fill = sorted(moves)[len(moves)//2] if moves else 0
            avg_move_after_fill = sum(moves) / len(moves) if moves else 0
        else:
            median_move_after_fill = 0
            avg_move_after_fill = 0

        key = (bin_num, day_num, gap_dir)
        results[key] = {
            'fill_rate': fill_rate,
            'median_move_before_fill': median_move_before_fill,
            'avg_move_before_fill': avg_move_before_fill,
            'median_max_unfilled': median_max_unfilled,
            'avg_max_unfilled': avg_max_unfilled,
            'median_move_after_fill': median_move_after_fill,
            'avg_move_after_fill': avg_move_after_fill,
            'sample_size': len(records)
        }

        print(f"Bin {bin_num} ({bin_name}), Day {day_num}, Dir {gap_dir}: "
              f"Fill Rate {fill_rate:.1f}%, Sample Size {len(records)}")

    return results

def generate_thinkorswim_arrays(results):
    """Generate ThinkScript data arrays"""

    print("\n"+"="*60)
    print("GENERATING THINKORSWIM DATA ARRAYS")
    print("="*60)

    # Generate gap fill rates array
    print("\n# Gap Fill Rates by bin, day, direction")
    print("def gapFillRates = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    fill_rate = results[key]['fill_rate']
                    day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][day_num]
                    print(f"    {{{day_num}, {gap_dir}}}: {fill_rate:.1f},  # {day_name}")
                else:
                    day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][day_num]
                    print(f"    {{{day_num}, {gap_dir}}}: 50.0,  # {day_name} (no data)")
        print()

    print("};")

    # Generate median moves before fill array
    print("\n# Median moves before fill (percentage)")
    print("def medianMovesBeforeFill = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    median_move = results[key]['median_move_before_fill']
                    print(f"    {{{day_num}, {gap_dir}}}: {median_move:.2f},")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 0.25,")
        print()

    print("};")

    # Generate average moves before fill array
    print("\n# Average moves before fill (percentage)")
    print("def averageMovesBeforeFill = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    avg_move = results[key]['avg_move_before_fill']
                    print(f"    {{{day_num}, {gap_dir}}}: {avg_move:.2f},")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 0.30,")
        print()

    print("};")

    # Generate median max moves unfilled array
    print("\n# Median max moves for unfilled gaps")
    print("def medianMaxMovesUnfilled = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    median_max = results[key]['median_max_unfilled']
                    print(f"    {{{day_num}, {gap_dir}}}: {median_max:.2f},")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 0.20,")
        print()

    print("};")

    # Generate average max moves unfilled array
    print("\n# Average max moves for unfilled gaps")
    print("def averageMaxMovesUnfilled = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    avg_max = results[key]['avg_max_unfilled']
                    print(f"    {{{day_num}, {gap_dir}}}: {avg_max:.2f},")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 0.25,")
        print()

    print("};")

    # Generate median moves after fill array
    print("\n# Median moves after fill (percentage)")
    print("def medianMovesAfterFill = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    median_after = results[key]['median_move_after_fill']
                    print(f"    {{{day_num}, {gap_dir}}}: {median_after:.2f},")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 0.25,")
        print()

    print("};")

    # Generate average moves after fill array
    print("\n# Average moves after fill (percentage)")
    print("def averageMovesAfterFill = {")

    for bin_num in range(1, 6):
        print(f"    # Bin {bin_num}")
        for day_num in range(5):
            for gap_dir in [1, -1]:
                key = (bin_num, day_num, gap_dir)
                if key in results:
                    avg_after = results[key]['avg_move_after_fill']
                    print(f"    {{{day_num}, {gap_dir}}}: {avg_after:.2f},")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 0.30,")
        print()

    print("};")

def main():
    """Main function"""
    csv_file = "data/qqq_central_data_cleaned.csv"

    try:
        data = load_gap_data(csv_file)
        results = calculate_metrics(data)
        generate_thinkorswim_arrays(results)

        print("\n"+"="*60)
        print("DATA PROCESSING COMPLETE")
        print("="*60)
        print(f"Total records processed: {len(data)}")
        print(f"Unique combinations found: {len(results)}")

    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()