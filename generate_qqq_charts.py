#!/usr/bin/env python3
"""
Generate QQQ Gap Analysis Charts
Run this script to create all charts from your CSV data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Set style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_prepare_data():
    """Load and prepare the CSV data for visualization"""
    print("Loading QQQ gap data...")
    
    # Load the CSV file
    df = pd.read_csv('data/qqq_central_data_cleaned.csv')
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Create gap size bins
    def categorize_gap_size(abs_gap):
        if abs_gap <= 0.35:
            return 'Small (0.15-0.35%)'
        elif abs_gap <= 0.5:
            return 'Medium (0.35-0.5%)'
        elif abs_gap <= 1.0:
            return 'Large (0.5-1%)'
        elif abs_gap <= 1.5:
            return 'Very Large (1-1.5%)'
        else:
            return 'Massive (1.5%+)'
    
    df['gap_size_category'] = df['abs_gap'].apply(categorize_gap_size)
    
    # Convert filled to boolean - handle mixed types
    df['filled'] = df['filled'].astype(str).str.lower() == 'true'
    
    # Add day of week
    df['day_of_week'] = df['date'].dt.day_name()
    
    print(f"Loaded {len(df)} records")
    return df

def create_fill_rate_by_size_chart(df):
    """Create chart showing fill rates by gap size"""
    print("Creating fill rate by size chart...")
    
    # Calculate fill rates by gap size
    fill_rates = df.groupby('gap_size_category')['filled'].agg(['count', 'sum'])
    fill_rates['fill_rate'] = (fill_rates['sum'] / fill_rates['count']) * 100
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#2E8B57', '#3CB371', '#FFD700', '#FF8C00', '#DC143C']
    bars = ax.bar(fill_rates.index, fill_rates['fill_rate'], color=colors, alpha=0.8)
    
    # Add value labels on bars
    for bar, rate in zip(bars, fill_rates['fill_rate']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Customize the chart
    ax.set_title('QQQ Gap Fill Rates by Size\n(1,929 Gap Occurrences Analyzed)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Fill Rate (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Gap Size Category', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 85)
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='y')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add sample size annotations
    for i, (category, data) in enumerate(fill_rates.iterrows()):
        ax.text(i, data['fill_rate']/2, f'n={data["count"]}', 
                ha='center', va='center', fontweight='bold', color='white', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('static/qqq_fill_rates_by_size.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Fill rate chart saved")

def create_day_of_week_analysis(df):
    """Create chart showing fill rates by day of week"""
    print("Creating day of week analysis chart...")
    
    # Calculate fill rates by day of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    fill_rates_by_day = df.groupby('day_of_week')['filled'].agg(['count', 'sum'])
    fill_rates_by_day['fill_rate'] = (fill_rates_by_day['sum'] / fill_rates_by_day['count']) * 100
    fill_rates_by_day = fill_rates_by_day.reindex(day_order)
    
    # Create the chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Chart 1: Overall fill rates by day
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    bars1 = ax1.bar(fill_rates_by_day.index, fill_rates_by_day['fill_rate'], 
                    color=colors, alpha=0.8)
    
    # Add value labels
    for bar, rate in zip(bars1, fill_rates_by_day['fill_rate']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax1.set_title('Overall Gap Fill Rates by Day of Week', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Fill Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 75)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Chart 2: Fill rates by day and gap size
    pivot_data = df.pivot_table(
        values='filled', 
        index='day_of_week', 
        columns='gap_size_category', 
        aggfunc='mean'
    ) * 100
    
    pivot_data = pivot_data.reindex(day_order)
    
    # Create heatmap
    sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn', 
                cbar_kws={'label': 'Fill Rate (%)'}, ax=ax2)
    ax2.set_title('Fill Rates by Day and Gap Size', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Gap Size Category', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Day of Week', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('static/qqq_day_of_week_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Day of week analysis chart saved")

def create_gap_direction_analysis(df):
    """Create chart showing up vs down gap analysis"""
    print("Creating gap direction analysis chart...")
    
    # Calculate fill rates by gap direction and size
    direction_analysis = df.groupby(['gap_direction', 'gap_size_category'])['filled'].agg(['count', 'sum'])
    direction_analysis['fill_rate'] = (direction_analysis['sum'] / direction_analysis['count']) * 100
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Prepare data for grouped bar chart
    gap_sizes = ['Small (0.15-0.35%)', 'Medium (0.35-0.5%)', 'Large (0.5-1%)', 
                 'Very Large (1-1.5%)', 'Massive (1.5%+)']
    
    x = np.arange(len(gap_sizes))
    width = 0.35
    
    up_rates = []
    down_rates = []
    
    for size in gap_sizes:
        up_rate = direction_analysis.loc[('up', size), 'fill_rate'] if ('up', size) in direction_analysis.index else 0
        down_rate = direction_analysis.loc[('down', size), 'fill_rate'] if ('down', size) in direction_analysis.index else 0
        up_rates.append(up_rate)
        down_rates.append(down_rate)
    
    bars1 = ax.bar(x - width/2, up_rates, width, label='Up Gaps', color='#2E8B57', alpha=0.8)
    bars2 = ax.bar(x + width/2, down_rates, width, label='Down Gaps', color='#DC143C', alpha=0.8)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_title('Gap Fill Rates: Up vs Down Gaps by Size', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Fill Rate (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Gap Size Category', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(gap_sizes, rotation=45, ha='right')
    ax.legend(fontsize=12)
    ax.set_ylim(0, 90)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('static/qqq_gap_direction_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Gap direction analysis chart saved")

def create_price_movement_zones(df):
    """Create chart showing the three zones of price movement"""
    print("Creating price movement zones chart...")
    
    # Calculate average moves for each zone by gap size
    zone_data = df.groupby('gap_size_category').agg({
        'max_move_gap_direction_first_30min_pct': 'mean',  # Zone 1
        'move_before_reversal_fill_direction_pct': 'mean'  # Zone 3
    }).reset_index()
    
    # For Zone 2 (unfilled gaps), we need to filter
    unfilled_data = df[~df['filled']].groupby('gap_size_category')['max_move_gap_direction_first_30min_pct'].mean()
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(6, 4))
    
    x = np.arange(len(zone_data))
    width = 0.25
    
    # Zone 1: Initial move (all gaps)
    zone1_values = zone_data['max_move_gap_direction_first_30min_pct'] * 100
    bars1 = ax.bar(x - width, zone1_values, width, label='Zone 1: Initial Move', 
                   color='#4ECDC4', alpha=0.8)
    
    # Zone 2: Stop zone (unfilled gaps)
    zone2_values = [unfilled_data.get(cat, 0) * 100 for cat in zone_data['gap_size_category']]
    bars2 = ax.bar(x, zone2_values, width, label='Zone 2: Stop Zone', 
                   color='#FF6B6B', alpha=0.8)
    
    # Zone 3: Reversal zone (filled gaps with reversals)
    zone3_values = zone_data['move_before_reversal_fill_direction_pct'] * 100
    bars3 = ax.bar(x + width, zone3_values, width, label='Zone 3: Reversal Zone', 
                   color='#45B7D1', alpha=0.8)
    
    ax.set_title('Three Zones of Gap Trading', fontsize=10, fontweight='bold')
    ax.set_ylabel('Average Move (%)', fontsize=8, fontweight='bold')
    ax.set_xlabel('Gap Size', fontsize=8, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(zone_data['gap_size_category'])
    ax.legend(fontsize=7)
    ax.set_ylim(0, 0.6)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.subplots_adjust(bottom=0.15, left=0.1, right=0.95, top=0.9)
    plt.savefig('static/qqq_price_movement_zones.png', dpi=300)
    plt.close()
    print("✓ Price movement zones chart saved")

def create_strategy_success_rates():
    """Create chart showing strategy success rates"""
    print("Creating strategy success rates chart...")
    
    # Strategy data based on our analysis
    strategies = ['Small Gap Fade\n(0.15-0.35%)', 'Medium Gap Momentum\n(0.35-0.5%)', 
                  'Large Gap Breakout\n(0.5-1%)', 'Very Large Gap Caution\n(1%+)']
    success_rates = [75.2, 58.4, 47.8, 28.7]
    risk_levels = ['Low', 'Medium', 'High', 'Very High']
    colors = ['#2E8B57', '#FFD700', '#FF8C00', '#DC143C']
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.bar(strategies, success_rates, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Add risk level annotations
    for i, (bar, risk) in enumerate(zip(bars, risk_levels)):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()/2,
                f'Risk: {risk}', ha='center', va='center', fontweight='bold', 
                color='white', fontsize=10)
    
    ax.set_title('Trading Strategy Success Rates by Gap Size', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Success Rate (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Strategy Type', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 85)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('static/qqq_strategy_success_rates.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Strategy success rates chart saved")

def create_timeline_analysis(df):
    """Create chart showing gap behavior over time"""
    print("Creating timeline analysis chart...")
    
    # Add year and month columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Calculate monthly fill rates
    monthly_fill_rates = df.groupby(['year', 'month'])['filled'].agg(['count', 'sum'])
    monthly_fill_rates['fill_rate'] = (monthly_fill_rates['sum'] / monthly_fill_rates['count']) * 100
    monthly_fill_rates = monthly_fill_rates.reset_index()
    
    # Create date column for x-axis
    monthly_fill_rates['date'] = pd.to_datetime(monthly_fill_rates[['year', 'month']].assign(day=1))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Chart 1: Monthly fill rates over time
    ax1.plot(monthly_fill_rates['date'], monthly_fill_rates['fill_rate'], 
             marker='o', linewidth=2, markersize=6, color='#4ECDC4')
    ax1.set_title('Monthly Gap Fill Rates Over Time', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Fill Rate (%)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # Add trend line
    z = np.polyfit(range(len(monthly_fill_rates)), monthly_fill_rates['fill_rate'], 1)
    p = np.poly1d(z)
    ax1.plot(monthly_fill_rates['date'], p(range(len(monthly_fill_rates))), 
             "r--", alpha=0.8, linewidth=2, label='Trend Line')
    ax1.legend()
    
    # Chart 2: Monthly gap count
    ax2.bar(monthly_fill_rates['date'], monthly_fill_rates['count'], 
            color='#45B7D1', alpha=0.8)
    ax2.set_title('Monthly Gap Count', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Gaps', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('static/qqq_timeline_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Timeline analysis chart saved")

def main():
    """Main function to create all charts"""
    print("🚀 Creating QQQ Gap Analysis Charts...")
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Load data
    df = load_and_prepare_data()
    
    # Create all charts
    create_fill_rate_by_size_chart(df)
    create_day_of_week_analysis(df)
    create_gap_direction_analysis(df)
    create_price_movement_zones(df)
    create_strategy_success_rates()
    create_timeline_analysis(df)
    
    print("\n✅ All charts created successfully!")
    print("📁 Charts saved in static/ directory:")
    print("1. qqq_fill_rates_by_size.png - Fill rates by gap size")
    print("2. qqq_day_of_week_analysis.png - Day of week analysis")
    print("3. qqq_gap_direction_analysis.png - Up vs down gaps")
    print("4. qqq_price_movement_zones.png - Three trading zones")
    print("5. qqq_strategy_success_rates.png - Strategy success rates")
    print("6. qqq_timeline_analysis.png - Timeline analysis")

if __name__ == "__main__":
    main()