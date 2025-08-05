// DOM Elements
const scanForm = document.getElementById('scanForm');
const domainInput = document.getElementById('domain');
const scanTypesSelect = document.getElementById('scanTypes');
const scanBtn = document.getElementById('scanBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const summaryCards = document.getElementById('summaryCards');
const rawJson = document.getElementById('rawJson');

// Content containers
const subdomainsContent = document.getElementById('subdomainsContent');
const liveHostsContent = document.getElementById('liveHostsContent');
const technologiesContent = document.getElementById('technologiesContent');
const vulnerabilitiesContent = document.getElementById('vulnerabilitiesContent');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Handle scan type selection
    scanTypesSelect.addEventListener('change', function() {
        const selectedOptions = Array.from(this.selectedOptions).map(option => option.value);
        
        // If "all" is selected, deselect other options and vice versa
        if (selectedOptions.includes('all')) {
            Array.from(this.options).forEach(option => {
                if (option.value !== 'all') {
                    option.selected = false;
                }
            });
        } else if (selectedOptions.length > 0) {
            // If other options are selected, deselect "all"
            this.querySelector('option[value="all"]').selected = false;
        }
    });

    // Handle form submission
    scanForm.addEventListener('submit', handleScanSubmit);
});

// Handle scan form submission
async function handleScanSubmit(e) {
    e.preventDefault();
    
    const domain = domainInput.value.trim();
    const selectedOptions = Array.from(scanTypesSelect.selectedOptions).map(option => option.value);
    
    if (!domain) {
        showAlert('Please enter a domain', 'warning');
        return;
    }
    
    if (selectedOptions.length === 0) {
        showAlert('Please select at least one scan type', 'warning');
        return;
    }
    
    // Prepare request data
    const requestData = {
        domain: domain,
        scans: selectedOptions.includes('all') ? ['all'] : selectedOptions
    };
    
    // Show loading state
    showLoading(true);
    
    try {
        const response = await fetch('/api/scan', {
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
        displayResults(data);
        
    } catch (error) {
        console.error('Scan error:', error);
        showAlert(`Scan failed: ${error.message}`, 'danger');
    } finally {
        showLoading(false);
    }
}

// Show/hide loading spinner
function showLoading(show) {
    if (show) {
        loadingSpinner.style.display = 'block';
        resultsSection.style.display = 'none';
        scanBtn.disabled = true;
        scanBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Scanning...';
    } else {
        loadingSpinner.style.display = 'none';
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i class="bi bi-play-circle me-2"></i>Start Scan';
    }
}

// Display scan results
function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Update raw JSON
    rawJson.textContent = JSON.stringify(data, null, 2);
    
    // Generate summary cards
    generateSummaryCards(data);
    
    // Update detailed results
    updateSubdomains(data);
    updateLiveHosts(data);
    updateTechnologies(data);
    updateVulnerabilities(data);
    
    // Add fade-in animation
    resultsSection.classList.add('fade-in');
}

// Generate summary cards
function generateSummaryCards(data) {
    const summaryData = [
        {
            title: 'Subdomains',
            count: data.subdomains?.length || 0,
            icon: 'bi-diagram-3',
            color: 'info',
            errors: data.subdomain_errors?.length || 0
        },
        {
            title: 'Live Hosts',
            count: data.live_hosts?.length || 0,
            icon: 'bi-hdd-network',
            color: 'success',
            errors: data.probe_errors?.length || 0
        },
        {
            title: 'Technologies',
            count: data.technologies?.length || 0,
            icon: 'bi-gear',
            color: 'warning',
            errors: data.techdetect_errors?.length || 0
        },
        {
            title: 'Vulnerabilities',
            count: data.vulnerabilities?.length || 0,
            icon: 'bi-exclamation-triangle',
            color: 'danger',
            errors: data.vulnscan_errors?.length || 0
        }
    ];
    
    summaryCards.innerHTML = summaryData.map(item => `
        <div class="col-md-3 col-sm-6 mb-3">
            <div class="summary-card">
                <i class="bi ${item.icon} text-${item.color} fs-1 mb-2"></i>
                <div class="number text-${item.color}">${item.count}</div>
                <div class="label text-muted">${item.title}</div>
                ${item.errors > 0 ? `<small class="text-warning">${item.errors} errors</small>` : ''}
            </div>
        </div>
    `).join('');
}

// Update subdomains section
function updateSubdomains(data) {
    const subdomains = data.subdomains || [];
    const errors = data.subdomain_errors || [];
    
    if (subdomains.length === 0 && errors.length === 0) {
        subdomainsContent.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-info-circle fs-1"></i>
                <p>No subdomains found</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Display subdomains
    if (subdomains.length > 0) {
        html += '<h6 class="text-info mb-3">Discovered Subdomains</h6>';
        subdomains.forEach(subdomain => {
            html += `
                <div class="result-item info">
                    <i class="bi bi-globe me-2"></i>
                    <strong>${subdomain}</strong>
                </div>
            `;
        });
    }
    
    // Display errors
    if (errors.length > 0) {
        html += '<h6 class="text-warning mb-3 mt-4">Errors</h6>';
        errors.forEach(error => {
            html += `
                <div class="result-item warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${error}
                </div>
            `;
        });
    }
    
    subdomainsContent.innerHTML = html;
}

// Update live hosts section
function updateLiveHosts(data) {
    const liveHosts = data.live_hosts || [];
    const errors = data.probe_errors || [];
    
    if (liveHosts.length === 0 && errors.length === 0) {
        liveHostsContent.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-info-circle fs-1"></i>
                <p>No live hosts found</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Display live hosts
    if (liveHosts.length > 0) {
        html += '<h6 class="text-success mb-3">Live Hosts</h6>';
        liveHosts.forEach(host => {
            html += `
                <div class="result-item success">
                    <i class="bi bi-check-circle me-2"></i>
                    <strong>${host}</strong>
                </div>
            `;
        });
    }
    
    // Display errors
    if (errors.length > 0) {
        html += '<h6 class="text-warning mb-3 mt-4">Errors</h6>';
        errors.forEach(error => {
            html += `
                <div class="result-item warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${error}
                </div>
            `;
        });
    }
    
    liveHostsContent.innerHTML = html;
}

// Update technologies section
function updateTechnologies(data) {
    const technologies = data.technologies || [];
    const errors = data.techdetect_errors || [];
    
    if (technologies.length === 0 && errors.length === 0) {
        technologiesContent.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-info-circle fs-1"></i>
                <p>No technologies detected</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Display technologies
    if (technologies.length > 0) {
        html += '<h6 class="text-warning mb-3">Detected Technologies</h6>';
        technologies.forEach(tech => {
            html += `
                <div class="result-item warning">
                    <i class="bi bi-gear me-2"></i>
                    <strong>${tech}</strong>
                </div>
            `;
        });
    }
    
    // Display errors
    if (errors.length > 0) {
        html += '<h6 class="text-warning mb-3 mt-4">Errors</h6>';
        errors.forEach(error => {
            html += `
                <div class="result-item warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${error}
                </div>
            `;
        });
    }
    
    technologiesContent.innerHTML = html;
}

// Update vulnerabilities section
function updateVulnerabilities(data) {
    const vulnerabilities = data.vulnerabilities || [];
    const errors = data.vulnscan_errors || [];
    
    if (vulnerabilities.length === 0 && errors.length === 0) {
        vulnerabilitiesContent.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-shield-check fs-1"></i>
                <p>No vulnerabilities found</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Display vulnerabilities
    if (vulnerabilities.length > 0) {
        html += '<h6 class="text-danger mb-3">Vulnerabilities Found</h6>';
        vulnerabilities.forEach(vuln => {
            html += `
                <div class="result-item danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>${vuln}</strong>
                </div>
            `;
        });
    }
    
    // Display errors
    if (errors.length > 0) {
        html += '<h6 class="text-warning mb-3 mt-4">Errors</h6>';
        errors.forEach(error => {
            html += `
                <div class="result-item warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${error}
                </div>
            `;
        });
    }
    
    vulnerabilitiesContent.innerHTML = html;
}

// Show alert message
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at the top of the main content
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Utility function to format data for display
function formatData(data) {
    if (typeof data === 'string') {
        return data;
    }
    if (Array.isArray(data)) {
        return data.join(', ');
    }
    if (typeof data === 'object') {
        return JSON.stringify(data, null, 2);
    }
    return String(data);
}

// Add some example data for testing (remove in production)
function addExampleData() {
    domainInput.value = 'example.com';
    scanTypesSelect.querySelector('option[value="all"]').selected = true;
}

// Optional: Add example data on page load for testing
// Uncomment the line below to add example data automatically
// document.addEventListener('DOMContentLoaded', addExampleData);