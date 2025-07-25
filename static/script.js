// JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Gap Insights functionality
    const gapInsightsForm = document.getElementById('gap-insights-form');
    if (gapInsightsForm) {
        gapInsightsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const gapSize = formData.get('gap_size');
            const day = formData.get('day');
            const gapDirection = formData.get('gap_direction');
            
            if (!gapSize || !day || !gapDirection) {
                alert('Please select all required fields: gap size, day, and direction.');
                return;
            }
            
            try {
                const response = await fetch(`/api/gap_insights?gap_size=${encodeURIComponent(gapSize)}&day=${encodeURIComponent(day)}&gap_direction=${encodeURIComponent(gapDirection)}&main_action=get_insights`);
                
                if (response.status === 429) {
                    const errorData = await response.json();
                    alert(errorData.error);
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayGapInsights(data.insights);
                
            } catch (error) {
                console.error('Error fetching gap insights:', error);
                alert('Error fetching gap insights. Please try again.');
            }
        });
    }

    // Previous High/Low Insights functionality
    const previousHighLowForm = document.getElementById('previous-high-low-form');
    if (previousHighLowForm) {
        previousHighLowForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const openPosition = formData.get('open_position');
            const dayOfWeek = formData.get('day_of_week');
            
            if (!openPosition) {
                alert('Please select the open position relative to previous high/low.');
                return;
            }
            
            try {
                let url = `/api/previous_high_low_insights?open_position=${encodeURIComponent(openPosition)}&main_action=get_insights`;
                if (dayOfWeek) {
                    url += `&day_of_week=${encodeURIComponent(dayOfWeek)}`;
                }
                
                const response = await fetch(url);
                
                if (response.status === 429) {
                    const errorData = await response.json();
                    alert(errorData.error);
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayPreviousHighLowInsights(data.insights, data.open_position, data.day_of_week, data.data_points);
                
            } catch (error) {
                console.error('Error fetching previous high/low insights:', error);
                alert('Error fetching previous high/low insights. Please try again.');
            }
        });
    }

    // Filter toggle functionality for previous high/low
    const previousHighLowFilterRadios = document.querySelectorAll('input[name="previous-high-low-filter-type"]');
    const bothFiltersSection = document.getElementById('both-filters-section');
    const positionOnlySection = document.getElementById('position-only-section');
    
    previousHighLowFilterRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'both-filters') {
                bothFiltersSection.classList.add('active');
                positionOnlySection.classList.remove('active');
            } else {
                bothFiltersSection.classList.remove('active');
                positionOnlySection.classList.add('active');
            }
        });
    });

    // News Event Insights functionality
});

// Display functions
function displayGapInsights(insights) {
    const resultsContainer = document.getElementById('gap-insights-results');
    if (!resultsContainer) return;

    if (!insights || Object.keys(insights).length === 0) {
        resultsContainer.innerHTML = '<p>No insights available for the selected criteria.</p>';
        return;
    }

    let html = '<div class="insights-container">';
    html += '<h3>Nasdaq Gap Insights</h3>';

    // Display each insight metric
    Object.keys(insights).forEach(key => {
        const insight = insights[key];
        html += '<div class="insights-row two-metrics">';
        
        if (insight.median !== undefined && insight.average !== undefined) {
            // Single metric display
            html += `
                <div class="insight-metric">
                    <div class="metric-name">${insight.description || key}</div>
                    <div class="metric-median">Median: ${insight.median}%</div>
                    <div class="metric-average">Average: ${insight.average}%</div>
                </div>
            `;
        } else if (insight.median_move_before_fill !== undefined) {
            // Complex metric with price info
            html += `
                <div class="insight-metric">
                    <div class="metric-name">${insight.description || key}</div>
                    <div class="metric-median">Median: ${insight.median_move_before_fill}%</div>
                    <div class="metric-average">Average: ${insight.average_move_before_fill}%</div>
                    ${insight.median_price ? `<div class="metric-price-median">Price: $${insight.median_price}</div>` : ''}
                    ${insight.average_price ? `<div class="metric-price-average">Avg Price: $${insight.average_price}</div>` : ''}
                    ${insight.price_description ? `<div class="metric-price-description">${insight.price_description}</div>` : ''}
                </div>
            `;
        } else if (insight.continuation_median !== undefined) {
            // Continuation/reversal metrics
            html += `
                <div class="insight-metric">
                    <div class="metric-name">${insight.continuation_description || 'Continuation'}</div>
                    <div class="metric-median">Median: ${insight.continuation_median}%</div>
                    <div class="metric-average">Average: ${insight.continuation_average}%</div>
                </div>
                <div class="insight-metric">
                    <div class="metric-name">${insight.reversal_description || 'Reversal'}</div>
                    <div class="metric-median">Median: ${insight.reversal_median}%</div>
                    <div class="metric-average">Average: ${insight.reversal_average}%</div>
                </div>
            `;
        }
        
        html += '</div>';
    });

    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayPreviousHighLowInsights(insights, openPosition, dayOfWeek, dataPoints) {
    const resultsContainer = document.getElementById('previous-high-low-results');
    if (!resultsContainer) return;

    if (!insights || Object.keys(insights).length === 0) {
        resultsContainer.innerHTML = '<p>No insights available for the selected criteria.</p>';
        return;
    }

    let html = '<div class="insights-container">';
    html += '<h3>NASDAQ Previous High/Low Insights</h3>';
    
    // Add filter summary
    let filterSummary = `Filters: ${openPosition}`;
    if (dayOfWeek) {
        filterSummary += `, ${dayOfWeek}`;
    }
    filterSummary += ` (${dataPoints} data points)`;
    html += `<p style="text-align: center; font-weight: bold; color: var(--primary-blue);">${filterSummary}</p>`;

    // Display each insight metric
    Object.keys(insights).forEach(key => {
        const insight = insights[key];
        html += '<div class="insights-row two-metrics">';
        
        if (insight.continuation_median !== undefined) {
            // Continuation/reversal metrics
            html += `
                <div class="insight-metric">
                    <div class="metric-name">${insight.continuation_description || 'Continuation'}</div>
                    <div class="metric-median">Median: ${insight.continuation_median}%</div>
                    <div class="metric-average">Average: ${insight.continuation_average}%</div>
                    ${insight.continuation_count ? `<div class="metric-counts">Count: ${insight.continuation_count}</div>` : ''}
                </div>
                <div class="insight-metric">
                    <div class="metric-name">${insight.reversal_description || 'Reversal'}</div>
                    <div class="metric-median">Median: ${insight.reversal_median}%</div>
                    <div class="metric-average">Average: ${insight.reversal_average}%</div>
                    ${insight.reversal_count ? `<div class="metric-counts">Count: ${insight.reversal_count}</div>` : ''}
                </div>
            `;
        }
        
        html += '</div>';
    });

    html += '</div>';
    resultsContainer.innerHTML = html;
}