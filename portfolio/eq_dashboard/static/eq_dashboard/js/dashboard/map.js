
class EarthquakeMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([39.0, 35.0], 6); // Center on Turkey

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        this.markers = L.featureGroup().addTo(this.map);
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

            if (!earthquakes || earthquakes.length === 0) {
                return;
            }

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
            });

            // Only try to fit bounds if we have markers
            if (this.markers.getLayers().length > 0) {
                this.map.fitBounds(this.markers.getBounds());
            }

        } catch (error) {
            console.error('Error updating map:', error);
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

