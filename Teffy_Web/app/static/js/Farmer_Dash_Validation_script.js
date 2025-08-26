class ValidationManager {
    constructor() {
        this.uid = this.getCookie('uid');
        this.container = document.getElementById('validationContainer');
    }
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    async fetchValidationData() {
        try {
            const response = await fetch(`/api/validation/${this.uid}`);
            if (!response.ok) throw new Error('Failed to fetch validation data');
            return await response.json();
        } catch (error) {
            console.error('Error fetching validation data:', error);
            throw error;
        }
    }

    createDataItem(label, value) {
        return `
            <div class="data-item">
                <div class="data-label">${label}</div>
                <div class="data-value">${value}</div>
            </div>
        `;
    }

    getStatusBadge(isValid) {
        return `
            <div class="status-badge ${isValid ? 'status-valid' : 'status-invalid'}">
                ${isValid ? 'Valid' : 'Invalid'}
            </div>
        `;
    }

    renderValidationCard(data) {
        const dataItems = Object.entries(data)
            .filter(([key]) => key !== 'isValid')
            .map(([key, value]) => this.createDataItem(
                key.replace(/([A-Z])/g, ' $1').trim(),
                typeof value === 'object' ? JSON.stringify(value, null, 2) : value
            ))
            .join('');

        return `
            <div class="validation-card">
                <div class="data-grid">
                    ${dataItems}
                </div>
                ${this.getStatusBadge(data.isValid)}
            </div>
        `;
    }

    showLoading() {
        this.container.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
            </div>
        `;
    }

    showError(message) {
        this.container.innerHTML = `
            <div class="error-message">
                ${message}
            </div>
        `;
    }

    async initialize() {
        if (!this.uid) {
            this.showError('No UID found. Please ensure you are properly authenticated.');
            return;
        }

        this.showLoading();

        try {
            const data = await this.fetchValidationData();
            this.container.innerHTML = this.renderValidationCard(data);

            document.querySelectorAll('.validation-card').forEach(card => {
                card.addEventListener('mousemove', (e) => {
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    card.style.setProperty('--mouse-x', `${x}px`);
                    card.style.setProperty('--mouse-y', `${y}px`);
                });
            });

        } catch (error) {
            this.showError('Failed to load validation data. Please try again later.');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const validationManager = new ValidationManager();
    validationManager.initialize();
});
