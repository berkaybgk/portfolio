class DashboardManager {
    constructor() {
        this.timeRange = document.getElementById('timeRange');
        this.totalEarthquakes = document.getElementById('totalEarthquakes');
        this.strongestMagnitude = document.getElementById('strongestMagnitude');
        this.earthquakesPerDay = document.getElementById('earthquakesPerDay');
        this.averageMagnitude = document.getElementById('averageMagnitude');
        this.pieChartLoading = document.getElementById('pieChartLoading');

        // Add magnitude slider elements
        this.magnitudeSlider = document.getElementById('magnitudeRange');
        this.magnitudeValue = document.getElementById('magnitudeValue');

        this.timeSelector = new TimeSelector(() => this.updateDashboard());

        // Initialize chart and map
        this.chart = new EarthquakeChart('earthquakeChart');
        this.map = new EarthquakeMap('map');

        // Initialize pie chart
        this.initializePieChart();

        // Bind events
        this.timeRange.addEventListener('change', () => this.updateDashboard());

        // Add magnitude slider event listener
        this.magnitudeSlider.addEventListener('input', (e) => {
            this.magnitudeValue.textContent = parseFloat(e.target.value).toFixed(1);
        });

        this.magnitudeSlider.addEventListener('change', () => {
            this.updateDashboard();
        });

        // Initial load
        this.updateDashboard();
    }

    initializePieChart() {
        const pieCtx = document.getElementById('magnitudePieChart').getContext('2d');
        this.magnitudePieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: ['3.0-3.9', '4.0-4.9', '5.0-5.9', '6.0+'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(191, 232, 102, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(255, 0, 0, 0.7)'
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dataset = context.dataset;
                                const total = dataset.data.reduce((acc, data) => acc + data, 0);
                                const value = dataset.data[context.dataIndex];
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    },
                    datalabels: {
                        formatter: (value, ctx) => {
                            const dataset = ctx.dataset;
                            const total = dataset.data.reduce((acc, data) => acc + data, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${percentage}%`;
                        },
                        color: '#000',
                        anchor: 'end',
                        align: 'start',
                        offset: 8,
                        display: function(context) {
                            return context.dataset.data[context.dataIndex] > 0;
                        }
                    }
                }
            }
        });
    }

    async updateDashboard() {
        try {
            if (this.pieChartLoading) {
                this.pieChartLoading.style.display = 'block';
            }
            const { startDate, endDate } = this.timeSelector.getSelectedDates();
            const minMagnitude = parseFloat(this.magnitudeSlider.value); // Get value from slider

            const response = await fetch(`/eq-dashboard/api/data/?start_date=${startDate}&end_date=${endDate}&min_magnitude=${minMagnitude}`);

            // Get the lookback days from the difference between the start and end date
            // Dates are given as strings in the format 'YYYY-MM-DD'
            const start = new Date(startDate);
            const end = new Date(endDate);
            const lookbackDays = Math.floor((end - start) / (1000 * 60 * 60 * 24));

            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Server error');
                } else {
                    const text = await response.text();
                    console.error('Server returned non-JSON response:', text);
                    throw new Error('Server returned an invalid response');
                }
            }

            const data = await response.json();

            if (!data.earthquakes) {
                throw new Error('No earthquake data received');
            }

            // Update all visualizations and statistics
            this.updateStatistics(data.earthquakes, lookbackDays);
            this.updateMagnitudeDistribution(data.earthquakes);
            this.updateTrendAnalysis(data.earthquakes, data.trend_earthquakes, lookbackDays);
            this.chart.updateChart(data.earthquakes, lookbackDays);
            this.map.updateMap(data.earthquakes);

            if (this.pieChartLoading) {
                this.pieChartLoading.style.display = 'none';
            }

        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            if (this.pieChartLoading) {
                this.pieChartLoading.style.display = 'none';
            }

            if (error.message) {
                const errorDiv = document.getElementById('error-message') || document.createElement('div');
                errorDiv.id = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = `Error: ${error.message}`;
                this.timeRange.parentNode.appendChild(errorDiv);
            }
        }
    }

    updateStatistics(earthquakes, lookbackDays) {
        // Total earthquakes
        this.totalEarthquakes.textContent = earthquakes.length;

        // Strongest magnitude
        const strongest = earthquakes.length > 0
            ? Math.max(...earthquakes.map(eq => eq.magnitude))
            : 0;
        this.strongestMagnitude.textContent = strongest.toFixed(1);

        // Average magnitude
        const average = earthquakes.reduce((sum, eq) => sum + eq.magnitude, 0) / earthquakes.length;
        this.averageMagnitude.textContent = average.toFixed(2);

        // Calculate earthquakes per day
        const earthquakesPerDay = (earthquakes.length / lookbackDays).toFixed(3);
        this.earthquakesPerDay.textContent = earthquakesPerDay;
    }

    updateMagnitudeDistribution(earthquakes) {
        const distribution = [0, 0, 0, 0];
        
        earthquakes.forEach(eq => {
            const mag = eq.magnitude;
            if (mag >= 3.0 && mag < 4.0) distribution[0]++;
            else if (mag >= 4.0 && mag < 5.0) distribution[1]++;
            else if (mag >= 5.0 && mag < 6.0) distribution[2]++;
            else if (mag >= 6.0) distribution[3]++;
        });

        this.magnitudePieChart.data.datasets[0].data = distribution;
        this.magnitudePieChart.update();
    }

    updateTrendAnalysis(currentEarthquakes, previousEarthquakes, lookbackDays) {
        // Calculate stats for current period
        const currentPeriod = {
            count: currentEarthquakes.length,
            avgMagnitude: currentEarthquakes.reduce((sum, eq) => sum + eq.magnitude, 0) / currentEarthquakes.length || 0
        };

        // Calculate stats for previous period
        const previousPeriod = {
            count: previousEarthquakes.length,
            avgMagnitude: previousEarthquakes.reduce((sum, eq) => sum + eq.magnitude, 0) / previousEarthquakes.length || 0
        };

        // Calculate percentage changes
        const frequencyChange = previousPeriod.count > 0
            ? ((currentPeriod.count - previousPeriod.count) / previousPeriod.count * 100).toFixed(1)
            : 0;

        const magnitudeChange = previousPeriod.avgMagnitude > 0
            ? ((currentPeriod.avgMagnitude - previousPeriod.avgMagnitude) / previousPeriod.avgMagnitude * 100).toFixed(1)
            : 0;

        // Update the UI
        document.getElementById('frequencyChange').textContent = `${Math.abs(frequencyChange)}%`;
        document.getElementById('magnitudeChange').textContent = `${Math.abs(magnitudeChange)}%`;

        // Update comparison period text
        const periodText = this.getPeriodText(lookbackDays);
        document.getElementById('frequencyComparisonPeriod').textContent = `vs previous ${periodText}`;
        document.getElementById('magnitudeComparisonPeriod').textContent = `vs previous ${periodText}`;

        // Update trend indicators
        this.updateTrendIndicator(
            document.querySelector('.trend-stat'),
            parseFloat(frequencyChange)
        );
        this.updateTrendIndicator(
            document.querySelectorAll('.trend-stat')[1],
            parseFloat(magnitudeChange)
        );
    }

    getPeriodText(lookbackDays) {
        if (lookbackDays === '30') return 'month';
        if (lookbackDays === '365') return 'year';
        if (lookbackDays === '3650') return 'decade';
        return `${lookbackDays} days`;
    }

    updateTrendIndicator(element, value) {
        const direction = element.querySelector('.trend-direction');
        if (value > 0) {
            direction.innerHTML = '↑';
            direction.style.color = '#ff4444';
            direction.style.fontSize = '2em';
        } else if (value < 0) {
            direction.innerHTML = '↓';
            direction.style.color = '#00C851';
            direction.style.fontSize = '2em';
        } else {
            direction.innerHTML = '→';
            direction.style.color = '#ffbb33';
            direction.style.fontSize = '2em';
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});