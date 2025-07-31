#!/bin/bash

# Script to create placeholder images for missing PNG files
echo "Creating placeholder images for missing files..."

# Function to create placeholder image
create_placeholder() {
    local filename=$1
    local text=$2
    local size=$3
    
    echo "Creating placeholder for $filename..."
    
    # Create a simple placeholder image with text
    convert -size "$size" xc:lightblue \
        -gravity center \
        -pointsize 24 \
        -fill black \
        -annotate +0+0 "$text" \
        -pointsize 16 \
        -annotate +0+40 "Placeholder Image" \
        "static/$filename"
    
    echo "  Created $filename ($size)"
}

# Create placeholders for QQQ gap analysis article
create_placeholder "qqq_fill_rates_by_size.png" "QQQ Fill Rates\nby Size" "600x400"
create_placeholder "qqq_day_of_week_analysis.png" "QQQ Day of Week\nAnalysis" "600x400"
create_placeholder "qqq_gap_direction_analysis.png" "QQQ Gap Direction\nAnalysis" "600x400"
create_placeholder "qqq_price_movement_zones.png" "QQQ Price Movement\nZones" "600x400"
create_placeholder "qqq_strategy_success_rates.png" "QQQ Strategy\nSuccess Rates" "600x400"
create_placeholder "qqq_timeline_analysis.png" "QQQ Timeline\nAnalysis" "600x400"

# Create placeholders for NASDAQ article
create_placeholder "overall_statistics.png" "NASDAQ Overall\nStatistics" "600x400"
create_placeholder "position_analysis.png" "Market Position\nAnalysis" "600x400"
create_placeholder "day_of_week_analysis.png" "Day of Week\nTrading Patterns" "600x400"
create_placeholder "time_series_analysis.png" "Time Series\nAnalysis" "600x400"
create_placeholder "trading_summary.png" "Trading Summary\nand Risk Analysis" "600x400"

echo "Placeholder images created!"
echo "Current image sizes:"
ls -lh static/*.png | sort -k5 -hr | head -15