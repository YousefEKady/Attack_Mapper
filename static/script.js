class ScanManager {
    constructor() {
        this.apiEndpoint = '/api/scan/scan';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('scanForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Add animation classes on page load
        document.addEventListener('DOMContentLoaded', () => {
            this.addAnimationClasses();
        });
    }

    addAnimationClasses() {
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const domain = formData.get('domain');
        const selectedScans = formData.getAll('scans');

        if (!domain.trim()) {
            this.showError('Please enter a domain to scan.');
            return;
        }

        if (selectedScans.length === 0) {
            this.showError('Please select at least one scan type.');
            return;
        }

        const requestData = {
            domain: domain.trim(),
            scans: selectedScans
        };

        this.startScan(requestData);
    }

    async startScan(requestData) {
        try {
            this.showLoading();
            this.hideResults();
            this.hideError();

            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayResults(data);

        } catch (error) {
            console.error('Scan error:', error);
            this.showError(`Scan failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const scanBtn = document.getElementById('scanBtn');
        
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
            loadingIndicator.classList.add('fade-in');
        }
        
        if (scanBtn) {
            scanBtn.disabled = true;
            scanBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Scanning...';
        }
    }

    hideLoading() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const scanBtn = document.getElementById('scanBtn');
        
        if (loadingIndicator) {
            loadingIndicator.classList.add('d-none');
        }
        
        if (scanBtn) {
            scanBtn.disabled = false;
            scanBtn.innerHTML = '<i class="bi bi-play-circle"></i> Start Scan';
        }
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorSection && errorMessage) {
            errorMessage.textContent = message;
            errorSection.classList.remove('d-none');
            errorSection.classList.add('slide-in');
            
            // Auto-hide error after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
        }
    }

    hideError() {
        const errorSection = document.getElementById('errorSection');
        if (errorSection) {
            errorSection.classList.add('d-none');
        }
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.add('d-none');
        }
    }

    displayResults(data) {
        this.updateStatistics(data);
        this.displayDetailedResults(data);
        
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.remove('d-none');
            resultsSection.classList.add('fade-in');
        }
    }

    updateStatistics(data) {
        // Update subdomain count
        const subdomainCount = document.getElementById('subdomainCount');
        if (subdomainCount) {
            const count = data.subdomains ? data.subdomains.length : 0;
            subdomainCount.textContent = count;
            this.animateCounter(subdomainCount, count);
        }

        // Update live host count
        const liveHostCount = document.getElementById('liveHostCount');
        if (liveHostCount) {
            const count = data.live_hosts ? data.live_hosts.length : 0;
            liveHostCount.textContent = count;
            this.animateCounter(liveHostCount, count);
        }

        // Update technology count
        const techCount = document.getElementById('techCount');
        if (techCount) {
            const count = data.technologies ? Object.keys(data.technologies).length : 0;
            techCount.textContent = count;
            this.animateCounter(techCount, count);
        }

        // Update vulnerability count
        const vulnCount = document.getElementById('vulnCount');
        if (vulnCount) {
            const count = data.vulnerabilities ? data.vulnerabilities.length : 0;
            vulnCount.textContent = count;
            this.animateCounter(vulnCount, count);
        }
    }

    animateCounter(element, finalValue) {
        const startValue = 0;
        const duration = 1000;
        const increment = finalValue / (duration / 16);
        let currentValue = startValue;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            element.textContent = Math.floor(currentValue);
        }, 16);
    }

    displayDetailedResults(data) {
        const detailedResults = document.getElementById('detailedResults');
        if (!detailedResults) return;

        let html = '';

        // Subdomains Section
        if (data.subdomains && data.subdomains.length > 0) {
            html += this.createResultCard(
                'Subdomains Discovered',
                'bi-diagram-3',
                'primary',
                this.formatSubdomains(data.subdomains),
                data.subdomain_errors
            );
        }

        // Live Hosts Section
        if (data.live_hosts && data.live_hosts.length > 0) {
            html += this.createResultCard(
                'Live Hosts Detected',
                'bi-activity',
                'success',
                this.formatLiveHosts(data.live_hosts),
                data.probe_errors
            );
        }

        // Technologies Section
        if (data.technologies && Object.keys(data.technologies).length > 0) {
            html += this.createResultCard(
                'Technologies Detected',
                'bi-cpu',
                'info',
                this.formatTechnologies(data.technologies),
                data.techdetect_errors
            );
        }

        // Vulnerabilities Section
        if (data.vulnerabilities && data.vulnerabilities.length > 0) {
            html += this.createResultCard(
                'Vulnerabilities Found',
                'bi-exclamation-triangle',
                'warning',
                this.formatVulnerabilities(data.vulnerabilities),
                data.vulnscan_errors
            );
        }

        // Notes and Warnings
        if (data.note || data.vulnscan_note) {
            html += this.createNotesSection(data.note, data.vulnscan_note);
        }

        detailedResults.innerHTML = html;
    }

    createResultCard(title, icon, color, content, errors = null) {
        let html = `
            <div class="card result-card slide-in">
                <div class="card-header bg-${color} text-white">
                    <h4 class="card-title mb-0">
                        <i class="bi ${icon}"></i>
                        ${title}
                    </h4>
                </div>
                <div class="card-body">
                    ${content}
                </div>
        `;

        if (errors && errors.length > 0) {
            html += `
                <div class="card-footer bg-light">
                    <h6 class="text-danger mb-2">
                        <i class="bi bi-exclamation-circle"></i>
                        Errors:
                    </h6>
                    <ul class="list-unstyled mb-0">
                        ${errors.map(error => `<li class="text-danger small">• ${error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    formatSubdomains(subdomains) {
        return `
            <div class="list-group">
                ${subdomains.map(subdomain => `
                    <div class="list-group-item d-flex align-items-center">
                        <i class="bi bi-link-45deg text-primary me-2"></i>
                        <span class="font-monospace">${subdomain}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    formatLiveHosts(liveHosts) {
        return `
            <div class="list-group">
                ${liveHosts.map(host => `
                    <div class="list-group-item d-flex align-items-center justify-content-between">
                        <div>
                            <i class="bi bi-globe text-success me-2"></i>
                            <span class="font-monospace">${host.url}</span>
                        </div>
                        <div>
                            <span class="badge bg-success">${host.status_code || 'Live'}</span>
                            ${host.title ? `<span class="badge bg-info ms-1">${host.title}</span>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    formatTechnologies(technologies) {
        let html = '<div class="row">';
        
        Object.entries(technologies).forEach(([category, techs]) => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card border-0 bg-light">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0">${category}</h6>
                        </div>
                        <div class="card-body">
                            ${techs.map(tech => `
                                <span class="badge bg-info me-1 mb-1">${tech}</span>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    formatVulnerabilities(vulnerabilities) {
        return `
            <div class="list-group">
                ${vulnerabilities.map(vuln => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-0 text-danger">
                                <i class="bi bi-exclamation-triangle"></i>
                                ${vuln.name || vuln.template || 'Vulnerability'}
                            </h6>
                            <span class="badge bg-warning text-dark">${vuln.severity || 'Unknown'}</span>
                        </div>
                        ${vuln.url ? `<p class="mb-1"><strong>URL:</strong> <span class="font-monospace">${vuln.url}</span></p>` : ''}
                        ${vuln.description ? `<p class="mb-1"><strong>Description:</strong> ${vuln.description}</p>` : ''}
                        ${vuln.extracted_results ? `<p class="mb-0"><strong>Details:</strong> ${vuln.extracted_results}</p>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    createNotesSection(note, vulnscanNote) {
        let html = '<div class="card result-card slide-in">';
        html += '<div class="card-header bg-info text-white">';
        html += '<h4 class="card-title mb-0"><i class="bi bi-info-circle"></i> Notes</h4>';
        html += '</div><div class="card-body">';
        
        if (note) {
            html += `<div class="alert alert-info mb-2"><i class="bi bi-info-circle"></i> ${note}</div>`;
        }
        
        if (vulnscanNote) {
            html += `<div class="alert alert-warning mb-0"><i class="bi bi-exclamation-triangle"></i> ${vulnscanNote}</div>`;
        }
        
        html += '</div></div>';
        return html;
    }
}

// Initialize the scan manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ScanManager();
});

// Add some utility functions for better UX
document.addEventListener('DOMContentLoaded', () => {
    // Auto-focus on domain input
    const domainInput = document.getElementById('domain');
    if (domainInput) {
        domainInput.focus();
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter to submit form
        if (e.ctrlKey && e.key === 'Enter') {
            const form = document.getElementById('scanForm');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Add form validation feedback
    const form = document.getElementById('scanForm');
    if (form) {
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.value.trim() === '') {
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
        });
    }
});