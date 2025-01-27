class EarthquakeChart {
    constructor(canvasId) {
        this.ctx = document.getElementById(canvasId).getContext('2d');
        this.chart = null;
        this.loadingIndicator = document.getElementById('chartLoading');
    }

    updateChart(earthquakes, lookbackDays) {
        // Show loading indicator
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'block';
        }

        try {
            const groupedData = this.groupData(earthquakes, lookbackDays);

            if (this.chart) {
                this.chart.destroy();
            }

            this.chart = new Chart(this.ctx, {
                type: 'line',
                data: {
                    labels: groupedData.labels,
                    datasets: [{
                        label: 'Number of Earthquakes',
                        data: groupedData.counts,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Earthquake Frequency'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        } finally {
            // Hide loading indicator after chart is created (or if there's an error)
            if (this.loadingIndicator) {
                this.loadingIndicator.style.display = 'none';
            }
        }
    }

    groupData(earthquakes, lookbackDays) {
        let labels = [];
        let counts = [];

        // Group data based on lookback period
        if (lookbackDays <= 30) {
            // Daily grouping for 30 days or less
            const dailyData = this.groupByDay(earthquakes);
            labels = dailyData.labels;
            counts = dailyData.counts;
        } else if (lookbackDays <= 365) {
            // Monthly grouping for a year
            const monthlyData = this.groupByMonth(earthquakes);
            labels = monthlyData.labels;
            counts = monthlyData.counts;
        } else {
            // Yearly grouping for multiple years
            const yearlyData = this.groupByYear(earthquakes);
            labels = yearlyData.labels;
            counts = yearlyData.counts;
        }

        return { labels, counts };
    }

    parseDate(dateStr) {
        // Convert "DD-MM-YYYY" to "YYYY-MM-DD"
        const [day, month, year] = dateStr.split('-');
        return new Date(`${year}-${month}-${day}`);
    }

    groupByDay(earthquakes) {
        // Sort earthquakes by date first
        const sorted = [...earthquakes].sort((a, b) =>
            this.parseDate(a.date) - this.parseDate(b.date)
        );

        const grouped = {};
        sorted.forEach(eq => {
            const date = this.parseDate(eq.date);
            const formattedDate = date.toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'short',
                year: 'numeric'
            });
            grouped[formattedDate] = (grouped[formattedDate] || 0) + 1;
        });

        return {
            labels: Object.keys(grouped),
            counts: Object.values(grouped)
        };
    }

    groupByMonth(earthquakes) {
        const sorted = [...earthquakes].sort((a, b) =>
            this.parseDate(a.date) - this.parseDate(b.date)
        );

        const grouped = {};
        sorted.forEach(eq => {
            const date = this.parseDate(eq.date);
            const monthYear = date.toLocaleDateString('en-US', {
                month: 'short',
                year: 'numeric'
            });
            grouped[monthYear] = (grouped[monthYear] || 0) + 1;
        });

        return {
            labels: Object.keys(grouped),
            counts: Object.values(grouped)
        };
    }

    groupByYear(earthquakes) {
        const sorted = [...earthquakes].sort((a, b) =>
            this.parseDate(a.date) - this.parseDate(b.date)
        );

        const grouped = {};
        sorted.forEach(eq => {
            const year = this.parseDate(eq.date).getFullYear().toString();
            grouped[year] = (grouped[year] || 0) + 1;
        });

        return {
            labels: Object.keys(grouped),
            counts: Object.values(grouped)
        };
    }
}
