
class EarthquakeMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([39.0, 35.0], 6); // Center on Turkey

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        this.markers = L.layerGroup().addTo(this.map);
    }

    parseDate(dateStr) {
        const [day, month, year] = dateStr.split('-');
        return new Date(`${year}-${month}-${day}`);
    }

    updateMap(earthquakes) {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'block';
        }

        try {
            this.markers.clearLayers();

            if (earthquakes.length === 0) {
                return;
            }

            const latLngs = [];

            earthquakes.forEach(eq => {
                const date = this.parseDate(eq.date);
                const formattedDate = date.toLocaleString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                const marker = L.circle([eq.latitude, eq.longitude], {
                    color: this.getColorByMagnitude(eq.magnitude),
                    fillColor: this.getColorByMagnitude(eq.magnitude),
                    fillOpacity: 0.5,
                    radius: this.getRadiusByMagnitude(eq.magnitude)
                });

                marker.bindPopup(`
                    <strong>Magnitude:</strong> ${eq.magnitude}<br>
                    <strong>Date:</strong> ${formattedDate}<br>
                    <strong>Depth:</strong> ${eq.depth} km
                `);

                this.markers.addLayer(marker);
                latLngs.push([eq.latitude, eq.longitude]);
            });

            // Use latLngBounds instead of trying to get bounds from the layer group
            if (latLngs.length > 0) {
                const bounds = L.latLngBounds(latLngs);
                this.map.fitBounds(bounds);
            }
        } finally {
            if (this.loadingIndicator) {
                this.loadingIndicator.style.display = 'none';
            }
        }
    }

    getColorByMagnitude(magnitude) {
        if (magnitude >= 6.0) return '#ff0000';
        if (magnitude >= 5.0) return '#ff6600';
        if (magnitude >= 4.0) return '#ffa500';
        return '#ffcc00';
    }

    getRadiusByMagnitude(magnitude) {
        // Scale radius based on magnitude (in meters)
        return Math.pow(2, magnitude) * 500;
    }
}

