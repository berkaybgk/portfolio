
class DashboardManager {
    constructor() {
        this.timeRange = document.getElementById('timeRange');
        this.totalEarthquakes = document.getElementById('totalEarthquakes');
        this.strongestMagnitude = document.getElementById('strongestMagnitude');
        this.earthquakesPerDay = document.getElementById('earthquakesPerDay');
        this.averageMagnitude = document.getElementById('averageMagnitude');

        // Initialize chart and map
        this.chart = new EarthquakeChart('earthquakeChart');
        this.map = new EarthquakeMap('map');

        // Bind events
        this.timeRange.addEventListener('change', () => this.updateDashboard());

        // Initial load
        this.updateDashboard();
    }

    async updateDashboard() {
        try {
            const lookbackDays = this.timeRange.value;
            const response = await fetch(`/eq-dashboard/api/data?lookback_days=${lookbackDays}`);

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            this.updateStatistics(data.earthquakes);
            this.chart.updateChart(data.earthquakes, lookbackDays);
            this.map.updateMap(data.earthquakes);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            // You might want to show an error message to the user
        }
    }

    updateStatistics(earthquakes) {
        // Total earthquakes
        this.totalEarthquakes.textContent = earthquakes.length;

        // Strongest magnitude
        const strongest = Math.max(...earthquakes.map(eq => eq.magnitude));
        this.strongestMagnitude.textContent = strongest.toFixed(1);

        // Average magnitude
        const average = earthquakes.reduce((sum, eq) => sum + eq.magnitude, 0) / earthquakes.length;
        this.averageMagnitude.textContent = average.toFixed(2);

        // Calculate earthquakes per day
        const lookbackDays = parseInt(this.timeRange.value);
        const earthquakesPerDay = (earthquakes.length / lookbackDays).toFixed(3);
        this.earthquakesPerDay.textContent = earthquakesPerDay;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});
