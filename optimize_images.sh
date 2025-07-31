#!/bin/bash

# Script to optimize all PNG images in the static directory
echo "Optimizing PNG images..."

# Create backup directory
mkdir -p static/backup

# Function to optimize image
optimize_image() {
    local file=$1
    local size=$2
    local quality=$3
    
    echo "Optimizing $file..."
    convert "static/$file" -resize "$size" -quality "$quality" "static/${file%.png}_optimized.png"
    
    # Check if optimization was successful
    if [ -f "static/${file%.png}_optimized.png" ]; then
        original_size=$(stat -c%s "static/$file")
        optimized_size=$(stat -c%s "static/${file%.png}_optimized.png")
        reduction=$(( (original_size - optimized_size) * 100 / original_size ))
        
        echo "  Original: ${original_size}KB, Optimized: ${optimized_size}KB, Reduction: ${reduction}%"
        
        # Replace original with optimized version
        mv "static/${file%.png}_optimized.png" "static/$file"
    else
        echo "  Failed to optimize $file"
    fi
}

# Optimize images with appropriate sizes
optimize_image "simumetric.png" "400x300" "80"
optimize_image "simmetric.png" "400x300" "80"
optimize_image "metricnews.png" "400x300" "80"
optimize_image "metricearning.png" "400x300" "80"
optimize_image "blog_2.png" "500x400" "85"
optimize_image "Figure_5.png" "500x400" "85"
optimize_image "blog_1.png" "500x400" "85"
optimize_image "Figure_3.png" "500x400" "85"
optimize_image "blog_4.png" "500x400" "85"
optimize_image "Figure_4.png" "500x400" "85"
optimize_image "Figure_2.png" "500x400" "85"
optimize_image "blog_3.png" "500x400" "85"
optimize_image "blog_6.png" "500x400" "85"
optimize_image "metricreversal.png" "400x300" "80"
optimize_image "blog_5.png" "500x400" "85"
optimize_image "metricgapfill.png" "400x300" "80"

echo "Image optimization complete!"
echo "Current image sizes:"
ls -lh static/*.png | sort -k5 -hr