class TimeSelector {
    constructor(updateCallback) {
        this.timeRange = document.getElementById('timeRange');
        this.startDate = document.getElementById('start-date');
        this.endDate = document.getElementById('end-date');
        this.customRange = document.querySelector('.custom-range');
        this.updateCallback = updateCallback;

        this.initializeEventListeners();
        this.setDefaultDates();
    }

    initializeEventListeners() {
        this.timeRange.addEventListener('change', () => this.handleTimeRangeChange());
        this.startDate.addEventListener('change', () => this.handleCustomDateChange());
        this.endDate.addEventListener('change', () => this.handleCustomDateChange());
    }

    setDefaultDates() {
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - 30); // Default to last 30 days

        this.endDate.value = this.formatDate(end);
        this.startDate.value = this.formatDate(start);
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    handleTimeRangeChange() {
        const value = this.timeRange.value;

        if (value === 'custom') {
            this.customRange.style.display = 'block';
            // Don't update the dashboard yet, wait for date selection
        } else {
            this.customRange.style.display = 'none';

            const end = new Date();
            const start = new Date();
            start.setDate(start.getDate() - parseInt(value));

            this.endDate.value = this.formatDate(end);
            this.startDate.value = this.formatDate(start);

            this.updateCallback();
        }
    }

    handleCustomDateChange() {
        if (this.startDate.value && this.endDate.value) {
            if (new Date(this.endDate.value) < new Date(this.startDate.value)) {
                alert('End date cannot be before start date');
                return;
            }
            this.updateCallback();
        }
    }

    getSelectedDates() {
        return {
            startDate: this.startDate.value,
            endDate: this.endDate.value
        };
    }
}