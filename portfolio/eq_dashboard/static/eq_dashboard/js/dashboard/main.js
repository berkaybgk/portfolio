
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
            console.log(`Fetching data for ${lookbackDays} days`);

            const response = await fetch(`/eq-dashboard/api/data?lookback_days=${lookbackDays}`);

            // Log the response details
            console.log('Response status:', response.status);
            console.log('Response type:', response.headers.get('content-type'));

            if (!response.ok) { //
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
            console.log(`Received ${data.earthquakes?.length || 0} earthquakes`);

            if (!data.earthquakes) {
                throw new Error('No earthquake data received');
            }

            this.updateStatistics(data.earthquakes);
            this.chart.updateChart(data.earthquakes, lookbackDays);
            this.map.updateMap(data.earthquakes);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            // You might want to show this error to the user in a more friendly way
            if (error.message) {
                // Add error display to your UI
                const errorDiv = document.getElementById('error-message') || document.createElement('div');
                errorDiv.id = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = `Error: ${error.message}`;
                this.timeRange.parentNode.appendChild(errorDiv);
            }
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
