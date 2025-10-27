#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Set style for better looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_clean_data():
    """Load and clean the CSV data"""
    df = pd.read_csv('data/previuos_high_low.csv')
    
    # Convert date columns
    df['date'] = pd.to_datetime(df['date'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract year for analysis
    df['year'] = df['date'].dt.year
    
    return df

def create_overall_statistics_chart(df):
    """Create overall statistics comparison chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('NASDAQ Previous High/Low Analysis: Overall Statistics (2100+ Days)', fontsize=16, fontweight='bold')
    
    # Prepare data
    high_data = df[df['touch_type'] == 'Previous High']
    low_data = df[df['touch_type'] == 'Previous Low']
    
    # 1. 10-minute vs 60-minute comparison
    categories = ['High Continuation', 'High Reversal', 'Low Continuation', 'Low Reversal']
    ten_min_medians = [
        high_data['continuation_move_pct'].median(),
        high_data['reversal_move_pct'].median(),
        low_data['continuation_move_pct'].median(),
        low_data['reversal_move_pct'].median()
    ]
    sixty_min_medians = [
        high_data['continuation_move_pct_60min'].median(),
        high_data['reversal_move_pct_60min'].median(),
        low_data['continuation_move_pct_60min'].median(),
        low_data['reversal_move_pct_60min'].median()
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, ten_min_medians, width, label='10-Minute', color='skyblue', alpha=0.8)
    bars2 = ax1.bar(x + width/2, sixty_min_medians, width, label='60-Minute', color='coral', alpha=0.8)
    
    ax1.set_xlabel('Move Type')
    ax1.set_ylabel('Median Move (%)')
    ax1.set_title('10-Minute vs 60-Minute Median Moves')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # 2. Distribution of moves by touch type
    ax2.hist(high_data['continuation_move_pct'], bins=50, alpha=0.7, label='High Continuation', color='green')
    ax2.hist(high_data['reversal_move_pct'], bins=50, alpha=0.7, label='High Reversal', color='red')
    ax2.set_xlabel('Move Percentage (%)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Previous High Moves')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribution of moves by touch type (Low)
    ax3.hist(low_data['continuation_move_pct'], bins=50, alpha=0.7, label='Low Continuation', color='orange')
    ax3.hist(low_data['reversal_move_pct'], bins=50, alpha=0.7, label='Low Reversal', color='purple')
    ax3.set_xlabel('Move Percentage (%)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Distribution of Previous Low Moves')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Box plot comparison
    data_to_plot = [
        high_data['continuation_move_pct'],
        high_data['reversal_move_pct'],
        low_data['continuation_move_pct'],
        low_data['reversal_move_pct']
    ]
    
    bp = ax4.boxplot(data_to_plot, labels=categories, patch_artist=True)
    colors = ['lightgreen', 'lightcoral', 'lightblue', 'lightyellow']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax4.set_ylabel('Move Percentage (%)')
    ax4.set_title('Box Plot: Move Distributions')
    ax4.grid(True, alpha=0.3)
    plt.setp(ax4.get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig('charts/overall_statistics.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_position_analysis_chart(df):
    """Create analysis by market position at open"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('NASDAQ Analysis by Market Position at Open', fontsize=16, fontweight='bold')
    
    # Filter data by position
    between_data = df[df['open_position'] == 'Between Previous High and Low']
    above_data = df[df['open_position'] == 'Above Previous High']
    below_data = df[df['open_position'] == 'Below Previous Low']
    
    # 1. Position distribution
    position_counts = df['open_position'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    wedges, texts, autotexts = ax1.pie(position_counts.values, labels=position_counts.index, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
    ax1.set_title('Distribution of Market Positions at Open')
    
    # 2. 10-minute moves by position
    positions = ['Between Previous High and Low', 'Above Previous High', 'Below Previous Low']
    high_cont_10min = [
        between_data[between_data['touch_type'] == 'Previous High']['continuation_move_pct'].median(),
        above_data[above_data['touch_type'] == 'Previous High']['continuation_move_pct'].median(),
        below_data[below_data['touch_type'] == 'Previous High']['continuation_move_pct'].median()
    ]
    high_rev_10min = [
        between_data[between_data['touch_type'] == 'Previous High']['reversal_move_pct'].median(),
        above_data[above_data['touch_type'] == 'Previous High']['reversal_move_pct'].median(),
        below_data[below_data['touch_type'] == 'Previous High']['reversal_move_pct'].median()
    ]
    
    x = np.arange(len(positions))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, high_cont_10min, width, label='High Continuation', color='lightgreen', alpha=0.8)
    bars2 = ax2.bar(x + width/2, high_rev_10min, width, label='High Reversal', color='lightcoral', alpha=0.8)
    
    ax2.set_xlabel('Market Position')
    ax2.set_ylabel('Median Move (%)')
    ax2.set_title('10-Minute Moves by Position (Previous High)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Between', 'Above', 'Below'], rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # 3. 60-minute moves by position
    high_cont_60min = [
        between_data[between_data['touch_type'] == 'Previous High']['continuation_move_pct_60min'].median(),
        above_data[above_data['touch_type'] == 'Previous High']['continuation_move_pct_60min'].median(),
        below_data[below_data['touch_type'] == 'Previous High']['continuation_move_pct_60min'].median()
    ]
    high_rev_60min = [
        between_data[between_data['touch_type'] == 'Previous High']['reversal_move_pct_60min'].median(),
        above_data[above_data['touch_type'] == 'Previous High']['reversal_move_pct_60min'].median(),
        below_data[below_data['touch_type'] == 'Previous High']['reversal_move_pct_60min'].median()
    ]
    
    bars3 = ax3.bar(x - width/2, high_cont_60min, width, label='High Continuation', color='darkgreen', alpha=0.8)
    bars4 = ax3.bar(x + width/2, high_rev_60min, width, label='High Reversal', color='darkred', alpha=0.8)
    
    ax3.set_xlabel('Market Position')
    ax3.set_ylabel('Median Move (%)')
    ax3.set_title('60-Minute Moves by Position (Previous High)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(['Between', 'Above', 'Below'], rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    for bar in bars4:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # 4. Heatmap of success rates
    # Calculate success rates (positive moves)
    success_data = []
    for position in positions:
        pos_data = df[df['open_position'] == position]
        high_cont_success = (pos_data[pos_data['touch_type'] == 'Previous High']['continuation_move_pct'] > 0).mean() * 100
        high_rev_success = (pos_data[pos_data['touch_type'] == 'Previous High']['reversal_move_pct'] > 0).mean() * 100
        low_cont_success = (pos_data[pos_data['touch_type'] == 'Previous Low']['continuation_move_pct'] > 0).mean() * 100
        low_rev_success = (pos_data[pos_data['touch_type'] == 'Previous Low']['reversal_move_pct'] > 0).mean() * 100
        success_data.append([high_cont_success, high_rev_success, low_cont_success, low_rev_success])
    
    success_data = np.array(success_data)
    im = ax4.imshow(success_data, cmap='RdYlGn', aspect='auto')
    
    # Add text annotations
    for i in range(len(positions)):
        for j in range(4):
            text = ax4.text(j, i, f'{success_data[i, j]:.1f}%',
                           ha="center", va="center", color="black", fontweight='bold')
    
    ax4.set_xticks(range(4))
    ax4.set_xticklabels(['High Cont', 'High Rev', 'Low Cont', 'Low Rev'], rotation=45)
    ax4.set_yticks(range(len(positions)))
    ax4.set_yticklabels(['Between', 'Above', 'Below'])
    ax4.set_title('Success Rate (%) by Position and Move Type')
    
    plt.colorbar(im, ax=ax4, label='Success Rate (%)')
    plt.tight_layout()
    plt.savefig('charts/position_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_day_of_week_chart(df):
    """Create day of week analysis chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('NASDAQ Analysis by Day of Week', fontsize=16, fontweight='bold')
    
    # 1. Day of week distribution
    day_counts = df['day_of_week'].value_counts()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_counts_ordered = [day_counts.get(day, 0) for day in days_order]
    
    bars = ax1.bar(days_order, day_counts_ordered, color='skyblue', alpha=0.8)
    ax1.set_xlabel('Day of Week')
    ax1.set_ylabel('Number of Instances')
    ax1.set_title('Distribution of Trading Instances by Day')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 2. 10-minute moves by day
    high_cont_10min_by_day = []
    high_rev_10min_by_day = []
    low_cont_10min_by_day = []
    low_rev_10min_by_day = []
    
    for day in days_order:
        day_data = df[df['day_of_week'] == day]
        high_cont_10min_by_day.append(day_data[day_data['touch_type'] == 'Previous High']['continuation_move_pct'].median())
        high_rev_10min_by_day.append(day_data[day_data['touch_type'] == 'Previous High']['reversal_move_pct'].median())
        low_cont_10min_by_day.append(day_data[day_data['touch_type'] == 'Previous Low']['continuation_move_pct'].median())
        low_rev_10min_by_day.append(day_data[day_data['touch_type'] == 'Previous Low']['reversal_move_pct'].median())
    
    x = np.arange(len(days_order))
    width = 0.2
    
    ax2.bar(x - 1.5*width, high_cont_10min_by_day, width, label='High Cont', color='lightgreen', alpha=0.8)
    ax2.bar(x - 0.5*width, high_rev_10min_by_day, width, label='High Rev', color='lightcoral', alpha=0.8)
    ax2.bar(x + 0.5*width, low_cont_10min_by_day, width, label='Low Cont', color='lightblue', alpha=0.8)
    ax2.bar(x + 1.5*width, low_rev_10min_by_day, width, label='Low Rev', color='lightyellow', alpha=0.8)
    
    ax2.set_xlabel('Day of Week')
    ax2.set_ylabel('Median Move (%)')
    ax2.set_title('10-Minute Moves by Day of Week')
    ax2.set_xticks(x)
    ax2.set_xticklabels(days_order, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 60-minute moves by day
    high_cont_60min_by_day = []
    high_rev_60min_by_day = []
    low_cont_60min_by_day = []
    low_rev_60min_by_day = []
    
    for day in days_order:
        day_data = df[df['day_of_week'] == day]
        high_cont_60min_by_day.append(day_data[day_data['touch_type'] == 'Previous High']['continuation_move_pct_60min'].median())
        high_rev_60min_by_day.append(day_data[day_data['touch_type'] == 'Previous High']['reversal_move_pct_60min'].median())
        low_cont_60min_by_day.append(day_data[day_data['touch_type'] == 'Previous Low']['continuation_move_pct_60min'].median())
        low_rev_60min_by_day.append(day_data[day_data['touch_type'] == 'Previous Low']['reversal_move_pct_60min'].median())
    
    ax3.bar(x - 1.5*width, high_cont_60min_by_day, width, label='High Cont', color='darkgreen', alpha=0.8)
    ax3.bar(x - 0.5*width, high_rev_60min_by_day, width, label='High Rev', color='darkred', alpha=0.8)
    ax3.bar(x + 0.5*width, low_cont_60min_by_day, width, label='Low Cont', color='darkblue', alpha=0.8)
    ax3.bar(x + 1.5*width, low_rev_60min_by_day, width, label='Low Rev', color='gold', alpha=0.8)
    
    ax3.set_xlabel('Day of Week')
    ax3.set_ylabel('Median Move (%)')
    ax3.set_title('60-Minute Moves by Day of Week')
    ax3.set_xticks(x)
    ax3.set_xticklabels(days_order, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Heatmap of day vs move type
    heatmap_data = []
    for day in days_order:
        day_data = df[df['day_of_week'] == day]
        day_row = []
        day_row.append(day_data[day_data['touch_type'] == 'Previous High']['continuation_move_pct'].median())
        day_row.append(day_data[day_data['touch_type'] == 'Previous High']['reversal_move_pct'].median())
        day_row.append(day_data[day_data['touch_type'] == 'Previous Low']['continuation_move_pct'].median())
        day_row.append(day_data[day_data['touch_type'] == 'Previous Low']['reversal_move_pct'].median())
        heatmap_data.append(day_row)
    
    heatmap_data = np.array(heatmap_data)
    im = ax4.imshow(heatmap_data, cmap='RdBu_r', aspect='auto')
    
    # Add text annotations
    for i in range(len(days_order)):
        for j in range(4):
            text = ax4.text(j, i, f'{heatmap_data[i, j]:.3f}',
                           ha="center", va="center", color="black", fontweight='bold')
    
    ax4.set_xticks(range(4))
    ax4.set_xticklabels(['High Cont', 'High Rev', 'Low Cont', 'Low Rev'], rotation=45)
    ax4.set_yticks(range(len(days_order)))
    ax4.set_yticklabels(days_order)
    ax4.set_title('Median Moves (%) by Day and Type')
    
    plt.colorbar(im, ax=ax4, label='Median Move (%)')
    plt.tight_layout()
    plt.savefig('charts/day_of_week_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_time_series_chart(df):
    """Create time series analysis chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('NASDAQ Time Series Analysis (2015-Present)', fontsize=16, fontweight='bold')
    
    # 1. Yearly distribution
    yearly_counts = df['year'].value_counts().sort_index()
    ax1.bar(yearly_counts.index, yearly_counts.values, color='steelblue', alpha=0.8)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of Instances')
    ax1.set_title('Trading Instances by Year')
    ax1.grid(True, alpha=0.3)
    
    # 2. Monthly pattern
    df['month'] = df['date'].dt.month
    monthly_counts = df['month'].value_counts().sort_index()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax2.bar(month_names, monthly_counts.values, color='lightcoral', alpha=0.8)
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Number of Instances')
    ax2.set_title('Trading Instances by Month')
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.get_xticklabels(), rotation=45)
    
    # 3. Performance over time (10-minute)
    yearly_performance_10min = df.groupby('year')['continuation_move_pct'].median()
    ax3.plot(yearly_performance_10min.index, yearly_performance_10min.values, 
             marker='o', linewidth=2, markersize=8, color='green', label='Continuation')
    
    yearly_reversal_10min = df.groupby('year')['reversal_move_pct'].median()
    ax3.plot(yearly_reversal_10min.index, yearly_reversal_10min.values, 
             marker='s', linewidth=2, markersize=8, color='red', label='Reversal')
    
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Median Move (%)')
    ax3.set_title('10-Minute Performance Over Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Performance over time (60-minute)
    yearly_performance_60min = df.groupby('year')['continuation_move_pct_60min'].median()
    ax4.plot(yearly_performance_60min.index, yearly_performance_60min.values, 
             marker='o', linewidth=2, markersize=8, color='darkgreen', label='Continuation')
    
    yearly_reversal_60min = df.groupby('year')['reversal_move_pct_60min'].median()
    ax4.plot(yearly_reversal_60min.index, yearly_reversal_60min.values, 
             marker='s', linewidth=2, markersize=8, color='darkred', label='Reversal')
    
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Median Move (%)')
    ax4.set_title('60-Minute Performance Over Time')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('charts/time_series_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_summary_chart(df):
    """Create a comprehensive summary chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('NASDAQ Previous High/Low Trading Summary (2100+ Days)', fontsize=16, fontweight='bold')
    
    # 1. Overall success rates
    high_cont_success = (df[df['touch_type'] == 'Previous High']['continuation_move_pct'] > 0).mean() * 100
    high_rev_success = (df[df['touch_type'] == 'Previous High']['reversal_move_pct'] > 0).mean() * 100
    low_cont_success = (df[df['touch_type'] == 'Previous Low']['continuation_move_pct'] > 0).mean() * 100
    low_rev_success = (df[df['touch_type'] == 'Previous Low']['reversal_move_pct'] > 0).mean() * 100
    
    categories = ['High Cont', 'High Rev', 'Low Cont', 'Low Rev']
    success_rates = [high_cont_success, high_rev_success, low_cont_success, low_rev_success]
    colors = ['lightgreen', 'lightcoral', 'lightblue', 'lightyellow']
    
    bars = ax1.bar(categories, success_rates, color=colors, alpha=0.8)
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('Overall Success Rates (10-Minute)')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 2. Average move sizes
    avg_moves_10min = [
        df[df['touch_type'] == 'Previous High']['continuation_move_pct'].mean(),
        df[df['touch_type'] == 'Previous High']['reversal_move_pct'].mean(),
        df[df['touch_type'] == 'Previous Low']['continuation_move_pct'].mean(),
        df[df['touch_type'] == 'Previous Low']['reversal_move_pct'].mean()
    ]
    
    bars = ax2.bar(categories, avg_moves_10min, color=colors, alpha=0.8)
    ax2.set_ylabel('Average Move (%)')
    ax2.set_title('Average Move Sizes (10-Minute)')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # 3. Best performing scenarios
    scenarios = ['Gap Up Reversal', 'Between High Cont', 'Between Low Rev', 'Gap Down Cont']
    scenario_performance = [
        df[df['open_position'] == 'Above Previous High']['reversal_move_pct'].median(),
        df[df['open_position'] == 'Between Previous High and Low']['continuation_move_pct'].median(),
        df[df['open_position'] == 'Between Previous High and Low']['reversal_move_pct'].median(),
        df[df['open_position'] == 'Below Previous Low']['continuation_move_pct'].median()
    ]
    
    bars = ax3.bar(scenarios, scenario_performance, color=['red', 'green', 'blue', 'orange'], alpha=0.8)
    ax3.set_ylabel('Median Move (%)')
    ax3.set_title('Best Performing Scenarios')
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.get_xticklabels(), rotation=45)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # 4. Risk vs Reward scatter
    # Calculate risk (std) vs reward (mean) for each scenario
    scenarios_data = []
    scenario_names = []
    
    for position in df['open_position'].unique():
        for touch_type in df['touch_type'].unique():
            subset = df[(df['open_position'] == position) & (df['touch_type'] == touch_type)]
            if len(subset) > 10:  # Only include scenarios with sufficient data
                mean_move = subset['continuation_move_pct'].mean()
                std_move = subset['continuation_move_pct'].std()
                scenarios_data.append([mean_move, std_move])
                scenario_names.append(f"{position[:10]}...\n{touch_type}")
    
    scenarios_data = np.array(scenarios_data)
    
    ax4.scatter(scenarios_data[:, 1], scenarios_data[:, 0], s=100, alpha=0.7, c='purple')
    ax4.set_xlabel('Risk (Standard Deviation)')
    ax4.set_ylabel('Reward (Mean Move %)')
    ax4.set_title('Risk vs Reward Analysis')
    ax4.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(scenarios_data[:, 1], scenarios_data[:, 0], 1)
    p = np.poly1d(z)
    ax4.plot(scenarios_data[:, 1], p(scenarios_data[:, 1]), "r--", alpha=0.8)
    
    plt.tight_layout()
    plt.savefig('charts/trading_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main function to generate all charts"""
    # Create charts directory
    if not os.path.exists('charts'):
        os.makedirs('charts')
    
    print("Loading data...")
    df = load_and_clean_data()
    
    print("Generating charts...")
    print("1. Overall statistics chart...")
    create_overall_statistics_chart(df)
    
    print("2. Position analysis chart...")
    create_position_analysis_chart(df)
    
    print("3. Day of week analysis chart...")
    create_day_of_week_chart(df)
    
    print("4. Time series analysis chart...")
    create_time_series_chart(df)
    
    print("5. Trading summary chart...")
    create_summary_chart(df)
    
    print("All charts generated successfully!")
    print("Charts saved in the 'charts' directory:")
    print("- overall_statistics.png")
    print("- position_analysis.png")
    print("- day_of_week_analysis.png")
    print("- time_series_analysis.png")
    print("- trading_summary.png")

if __name__ == "__main__":
    main()