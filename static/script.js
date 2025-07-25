// JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing JavaScript...');
    
    // Gap Insights functionality
    const gapInsightsForm = document.getElementById('gap-insights-form');
    if (gapInsightsForm) {
        console.log('Gap insights form found');
        gapInsightsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Gap insights form submitted');
            
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
        console.log('Previous high/low form found');
        previousHighLowForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Previous high/low form submitted');
            
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
                
                console.log('Fetching from URL:', url);
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
                console.log('Received data:', data);
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
    const newsEventInsightsForm = document.getElementById('news-event-insights-form');
    if (newsEventInsightsForm) {
        newsEventInsightsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const eventType = formData.get('event_type');
            const day = formData.get('day');
            
            if (!eventType || !day) {
                alert('Please select both event type and day.');
                return;
            }
            
            try {
                const response = await fetch(`/api/news_event_insights?event_type=${encodeURIComponent(eventType)}&day=${encodeURIComponent(day)}&main_action=get_insights`);
                
                if (response.status === 429) {
                    const errorData = await response.json();
                    alert(errorData.error);
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayNewsEventInsights(data.insights);
                
            } catch (error) {
                console.error('Error fetching news event insights:', error);
                alert('Error fetching news event insights. Please try again.');
            }
        });
    }

    // Gap Analysis functionality
    const gapAnalysisForm = document.getElementById('gap-analysis-form');
    if (gapAnalysisForm) {
        gapAnalysisForm.addEventListener('submit', async function(e) {
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
                const response = await fetch(`/api/gap_analysis?gap_size=${encodeURIComponent(gapSize)}&day=${encodeURIComponent(day)}&gap_direction=${encodeURIComponent(gapDirection)}&main_action=get_analysis`);
                
                if (response.status === 429) {
                    const errorData = await response.json();
                    alert(errorData.error);
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayGapAnalysis(data.analysis);
                
            } catch (error) {
                console.error('Error fetching gap analysis:', error);
                alert('Error fetching gap analysis. Please try again.');
            }
        });
    }

    // Events Analysis functionality
    const eventsAnalysisForm = document.getElementById('events-analysis-form');
    if (eventsAnalysisForm) {
        eventsAnalysisForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const eventType = formData.get('event_type');
            const day = formData.get('day');
            
            if (!eventType || !day) {
                alert('Please select both event type and day.');
                return;
            }
            
            try {
                const response = await fetch(`/api/events_analysis?event_type=${encodeURIComponent(eventType)}&day=${encodeURIComponent(day)}&main_action=get_analysis`);
                
                if (response.status === 429) {
                    const errorData = await response.json();
                    alert(errorData.error);
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayEventsAnalysis(data.analysis);
                
            } catch (error) {
                console.error('Error fetching events analysis:', error);
                alert('Error fetching events analysis. Please try again.');
            }
        });
    }

    // Earnings Analysis functionality
    const earningsAnalysisForm = document.getElementById('earnings-analysis-form');
    if (earningsAnalysisForm) {
        earningsAnalysisForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const earningsType = formData.get('earnings_type');
            const day = formData.get('day');
            
            if (!earningsType || !day) {
                alert('Please select both earnings type and day.');
                return;
            }
            
            try {
                const response = await fetch(`/api/earnings_analysis?earnings_type=${encodeURIComponent(earningsType)}&day=${encodeURIComponent(day)}&main_action=get_analysis`);
                
                if (response.status === 429) {
                    const errorData = await response.json();
                    alert(errorData.error);
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayEarningsAnalysis(data.analysis);
                
            } catch (error) {
                console.error('Error fetching earnings analysis:', error);
                alert('Error fetching earnings analysis. Please try again.');
            }
        });
    }
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
            html += '<div class="metric-card">';
            html += '<h4>Median</h4>';
            html += '<div class="metric-value">' + insight.median.toFixed(2) + '%</div>';
            html += '</div>';
            
            html += '<div class="metric-card">';
            html += '<h4>Average</h4>';
            html += '<div class="metric-value">' + insight.average.toFixed(2) + '%</div>';
            html += '</div>';
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
    
    // Add filter info
    let filterInfo = `Open Position: ${openPosition}`;
    if (dayOfWeek) {
        filterInfo += ` | Day: ${dayOfWeek}`;
    }
    html += `<p class="filter-info">${filterInfo}</p>`;
    
    if (dataPoints) {
        html += `<p class="data-points">Data Points: ${dataPoints}</p>`;
    }

    // Display each insight metric
    Object.keys(insights).forEach(key => {
        const insight = insights[key];
        html += '<div class="insights-row two-metrics">';
        
        if (insight.median !== undefined && insight.average !== undefined) {
            html += '<div class="metric-card">';
            html += '<h4>Median</h4>';
            html += '<div class="metric-value">' + insight.median.toFixed(2) + '%</div>';
            html += '</div>';
            
            html += '<div class="metric-card">';
            html += '<h4>Average</h4>';
            html += '<div class="metric-value">' + insight.average.toFixed(2) + '%</div>';
            html += '</div>';
        }
        
        html += '</div>';
    });

    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayNewsEventInsights(insights) {
    const resultsContainer = document.getElementById('news-event-insights-results');
    if (!resultsContainer) return;

    if (!insights || Object.keys(insights).length === 0) {
        resultsContainer.innerHTML = '<p>No insights available for the selected criteria.</p>';
        return;
    }

    let html = '<div class="insights-container">';
    html += '<h3>News Event Insights</h3>';

    Object.keys(insights).forEach(key => {
        const insight = insights[key];
        html += '<div class="insights-row two-metrics">';
        
        if (insight.median !== undefined && insight.average !== undefined) {
            html += '<div class="metric-card">';
            html += '<h4>Median</h4>';
            html += '<div class="metric-value">' + insight.median.toFixed(2) + '%</div>';
            html += '</div>';
            
            html += '<div class="metric-card">';
            html += '<h4>Average</h4>';
            html += '<div class="metric-value">' + insight.average.toFixed(2) + '%</div>';
            html += '</div>';
        }
        
        html += '</div>';
    });

    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayGapAnalysis(analysis) {
    const resultsContainer = document.getElementById('gap-analysis-results');
    if (!resultsContainer) return;

    if (!analysis || Object.keys(analysis).length === 0) {
        resultsContainer.innerHTML = '<p>No analysis available for the selected criteria.</p>';
        return;
    }

    let html = '<div class="analysis-container">';
    html += '<h3>Gap Analysis</h3>';

    // Display market data summary
    if (analysis.market_data) {
        html += '<div class="market-data-summary">';
        html += '<h4>Market Data Summary</h4>';
        html += '<div class="market-data-grid">';
        
        Object.keys(analysis.market_data).forEach(key => {
            const value = analysis.market_data[key];
            html += '<div class="market-data-item">';
            html += '<div class="market-data-label">' + key.replace(/_/g, ' ').toUpperCase() + '</div>';
            html += '<div class="market-data-value">' + value + '</div>';
            html += '</div>';
        });
        
        html += '</div>';
        html += '</div>';
    }

    // Display analysis results
    if (analysis.results) {
        html += '<div class="analysis-results">';
        Object.keys(analysis.results).forEach(key => {
            const result = analysis.results[key];
            html += '<div class="result-item">';
            html += '<h4>' + key.replace(/_/g, ' ').toUpperCase() + '</h4>';
            html += '<p>' + result + '</p>';
            html += '</div>';
        });
        html += '</div>';
    }

    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayEventsAnalysis(analysis) {
    const resultsContainer = document.getElementById('events-analysis-results');
    if (!resultsContainer) return;

    if (!analysis || Object.keys(analysis).length === 0) {
        resultsContainer.innerHTML = '<p>No analysis available for the selected criteria.</p>';
        return;
    }

    let html = '<div class="analysis-container">';
    html += '<h3>Events Analysis</h3>';

    // Display market data summary
    if (analysis.market_data) {
        html += '<div class="market-data-summary">';
        html += '<h4>Market Data Summary</h4>';
        html += '<div class="market-data-grid">';
        
        Object.keys(analysis.market_data).forEach(key => {
            const value = analysis.market_data[key];
            html += '<div class="market-data-item">';
            html += '<div class="market-data-label">' + key.replace(/_/g, ' ').toUpperCase() + '</div>';
            html += '<div class="market-data-value">' + value + '</div>';
            html += '</div>';
        });
        
        html += '</div>';
        html += '</div>';
    }

    // Display analysis results
    if (analysis.results) {
        html += '<div class="analysis-results">';
        Object.keys(analysis.results).forEach(key => {
            const result = analysis.results[key];
            html += '<div class="result-item">';
            html += '<h4>' + key.replace(/_/g, ' ').toUpperCase() + '</h4>';
            html += '<p>' + result + '</p>';
            html += '</div>';
        });
        html += '</div>';
    }

    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayEarningsAnalysis(analysis) {
    const resultsContainer = document.getElementById('earnings-analysis-results');
    if (!resultsContainer) return;

    if (!analysis || Object.keys(analysis).length === 0) {
        resultsContainer.innerHTML = '<p>No analysis available for the selected criteria.</p>';
        return;
    }

    let html = '<div class="analysis-container">';
    html += '<h3>Earnings Analysis</h3>';

    // Display market data summary
    if (analysis.market_data) {
        html += '<div class="market-data-summary">';
        html += '<h4>Market Data Summary</h4>';
        html += '<div class="market-data-grid">';
        
        Object.keys(analysis.market_data).forEach(key => {
            const value = analysis.market_data[key];
            html += '<div class="market-data-item">';
            html += '<div class="market-data-label">' + key.replace(/_/g, ' ').toUpperCase() + '</div>';
            html += '<div class="market-data-value">' + value + '</div>';
            html += '</div>';
        });
        
        html += '</div>';
        html += '</div>';
    }

    // Display analysis results
    if (analysis.results) {
        html += '<div class="analysis-results">';
        Object.keys(analysis.results).forEach(key => {
            const result = analysis.results[key];
            html += '<div class="result-item">';
            html += '<h4>' + key.replace(/_/g, ' ').toUpperCase() + '</h4>';
            html += '<p>' + result + '</p>';
            html += '</div>';
        });
        html += '</div>';
    }

    html += '</div>';
    resultsContainer.innerHTML = html;
}