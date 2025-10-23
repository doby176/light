#!/usr/bin/env python3
"""
Generate ThinkOrSwim data arrays from 1MChart gap analysis data
Extracts real historical data and formats it for ThinkScript
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_and_process_gap_data(csv_file_path):
    """Load and process the gap data from CSV"""
    print(f"Loading gap data from {csv_file_path}...")
    
    # Load the data
    df = pd.read_csv(csv_file_path)
    
    # Convert date to datetime and extract day of week
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Map day names to numbers (0=Monday, 1=Tuesday, etc.)
    day_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4}
    df['day_num'] = df['day_of_week'].map(day_mapping)
    
    # Map gap direction to numbers (1=up, -1=down)
    df['gap_dir_num'] = df['gap_direction'].map({'up': 1, 'down': -1})
    
    print(f"Loaded {len(df)} records")
    return df

def calculate_gap_metrics(df):
    """Calculate gap fill rates and move statistics by bin, day, and direction"""
    
    # Define gap size bins
    gap_bins = {
        1: '0.15-0.35%',
        2: '0.35-0.5%', 
        3: '0.5-1%',
        4: '1-1.5%',
        5: '1.5%+'
    }
    
    results = {}
    
    for bin_num, bin_name in gap_bins.items():
        print(f"\nProcessing bin {bin_num}: {bin_name}")
        
        # Filter data for this bin
        bin_data = df[df['gap_size_bin'] == bin_name].copy()
        
        if len(bin_data) == 0:
            print(f"No data for bin {bin_name}")
            continue
            
        for day_num in range(5):  # Monday to Friday
            for gap_dir in [1, -1]:  # Up and down
                
                # Filter for specific day and direction
                filtered = bin_data[
                    (bin_data['day_num'] == day_num) & 
                    (bin_data['gap_dir_num'] == gap_dir)
                ]
                
                if len(filtered) == 0:
                    continue
                
                # Calculate metrics
                fill_rate = filtered['filled'].mean() * 100
                
                # Median move before fill (for filled gaps only)
                filled_gaps = filtered[filtered['filled'] == True]
                median_move_before_fill = filled_gaps['move_before_reversal_fill_direction_pct'].median() if len(filled_gaps) > 0 else 0
                
                # Median max move for unfilled gaps
                unfilled_gaps = filtered[filtered['filled'] == False]
                median_max_unfilled = unfilled_gaps['max_move_gap_direction_first_30min_pct'].median() if len(unfilled_gaps) > 0 else 0
                
                # Store results
                key = (bin_num, day_num, gap_dir)
                results[key] = {
                    'fill_rate': fill_rate,
                    'median_move_before_fill': median_move_before_fill,
                    'median_max_unfilled': median_max_unfilled,
                    'sample_size': len(filtered)
                }
                
                print(f"  Day {day_num}, Dir {gap_dir}: Fill Rate {fill_rate:.1f}%, Sample Size {len(filtered)}")
    
    return results

def generate_thinkorswim_arrays(results):
    """Generate ThinkScript data arrays from the results"""
    
    print("\n" + "="*60)
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
                    print(f"    {{{day_num}, {gap_dir}}}: {fill_rate:.1f},  # {'Mon' if day_num==0 else 'Tue' if day_num==1 else 'Wed' if day_num==2 else 'Thu' if day_num==3 else 'Fri'}")
                else:
                    print(f"    {{{day_num}, {gap_dir}}}: 50.0,  # {'Mon' if day_num==0 else 'Tue' if day_num==1 else 'Wed' if day_num==2 else 'Thu' if day_num==3 else 'Fri'} (no data)")
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

def main():
    """Main function to process data and generate ThinkScript arrays"""
    
    # Load and process the data
    csv_file = "data/qqq_central_data_cleaned.csv"
    
    try:
        df = load_and_process_gap_data(csv_file)
        results = calculate_gap_metrics(df)
        generate_thinkorswim_arrays(results)
        
        print("\n" + "="*60)
        print("DATA PROCESSING COMPLETE")
        print("="*60)
        print(f"Total records processed: {len(df)}")
        print(f"Unique combinations found: {len(results)}")
        
        # Show some sample statistics
        print("\nSample Statistics:")
        for key, data in list(results.items())[:5]:
            bin_num, day_num, gap_dir = key
            print(f"Bin {bin_num}, Day {day_num}, Dir {gap_dir}: {data}")
            
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
        print("Please make sure the CSV file exists in the data directory.")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()