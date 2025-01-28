
class EarthquakeMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([39.0, 35.0], 6); // Center on Turkey

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
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
                console.log('No earthquakes to display');
                return;
            }

            const bounds = [];
            earthquakes.forEach(eq => {
                const latLng = [eq.latitude, eq.longitude];
                bounds.push(latLng);

                const marker = L.circle(latLng, {
                    color: this.getColorByMagnitude(eq.magnitude),
                    fillColor: this.getColorByMagnitude(eq.magnitude),
                    fillOpacity: 0.5,
                    radius: this.getRadiusByMagnitude(eq.magnitude)
                });

                marker.bindPopup(`
                    <strong>Magnitude:</strong> ${eq.magnitude}<br>
                    <strong>Date:</strong> ${this.parseDate(eq.date).toLocaleString('en-GB')}<br>
                    <strong>Depth:</strong> ${eq.depth} km
                `);

                this.markers.addLayer(marker);
            });

            if (bounds.length > 0) {
                this.map.fitBounds(L.latLngBounds(bounds));
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

