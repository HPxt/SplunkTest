// Splunk SIEM Web Application - Frontend JavaScript

const API_BASE = '/api';
let currentData = {
    logs: [],
    alerts: [],
    stats: {}
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    checkHealth();
    loadStats();
    setInterval(loadStats, 30000); // Refresh every 30 seconds
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const pageName = this.dataset.page;
            navigateTo(pageName);
        });
    });
}

function navigateTo(pageName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });

    // Update pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`page-${pageName}`).classList.add('active');

    // Update header
    const titles = {
        dashboard: ['Security Dashboard', 'Real-time threat monitoring and analysis'],
        logs: ['Event Logs', 'Browse and search security events'],
        alerts: ['Security Alerts', 'Review detected threats and anomalies'],
        search: ['SPL Search', 'Execute custom queries'],
        analysis: ['Security Analysis', 'Run comprehensive threat analysis'],
        settings: ['Settings', 'Configure SIEM parameters']
    };

    if (titles[pageName]) {
        document.getElementById('page-title').textContent = titles[pageName][0];
        document.getElementById('page-subtitle').textContent = titles[pageName][1];
    }

    // Load page data
    if (pageName === 'logs') loadLogs();
    if (pageName === 'alerts') loadAlerts();
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast('API Error: ' + error.message, 'error');
        return null;
    }
}

async function checkHealth() {
    const result = await apiCall('/health');
    if (result) {
        document.getElementById('backend-status').textContent = 'Online';
        document.getElementById('backend-status').className = 'badge badge-success';
    } else {
        document.getElementById('backend-status').textContent = 'Offline';
        document.getElementById('backend-status').className = 'badge badge-danger';
    }
}

async function loadStats() {
    const result = await apiCall('/stats');
    if (result && result.success) {
        currentData.stats = result.stats;
        updateDashboard(result.stats);
        updateHeaderStats(result.stats);
    }
}

function updateHeaderStats(stats) {
    document.getElementById('total-events').textContent = stats.total_logs || 0;
    document.getElementById('total-alerts').textContent = stats.total_alerts || 0;
}

function updateDashboard(stats) {
    // Update stat cards
    document.getElementById('dash-total-events').textContent = (stats.total_logs || 0).toLocaleString();
    document.getElementById('dash-total-alerts').textContent = stats.total_alerts || 0;
    document.getElementById('dash-high-alerts').textContent = stats.high_alerts || 0;
    document.getElementById('dash-log-types').textContent = stats.log_types || 0;

    // Update log distribution chart
    renderLogDistribution(stats.logs_by_type || {});

    // Update threat chart
    renderTopThreats(stats.alert_types || {});

    // Load recent alerts
    loadRecentAlerts();
}

function renderLogDistribution(logsBy Type) {
    const container = document.getElementById('chart-log-distribution');
    if (Object.keys(logsByType).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No data available</p>';
        return;
    }

    const total = Math.max(...Object.values(logsByType));
    let html = '<div class="bar-chart">';

    for (const [type, count] of Object.entries(logsByType)) {
        const percentage = total > 0 ? (count / total) * 100 : 0;
        html += `
            <div class="bar-item">
                <div class="bar-label">${type.toUpperCase()}</div>
                <div class="bar-wrapper">
                    <div class="bar-fill" style="width: ${percentage}%">
                        ${count.toLocaleString()} events
                    </div>
                </div>
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

function renderTopThreats(alertTypes) {
    const container = document.getElementById('chart-top-threats');
    if (Object.keys(alertTypes).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No threats detected</p>';
        return;
    }

    // Sort and get top 5
    const sorted = Object.entries(alertTypes)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    const maxCount = sorted[0][1];
    let html = '<div class="bar-chart">';

    sorted.forEach(([type, count]) => {
        const percentage = (count / maxCount) * 100;
        const displayName = type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `
            <div class="bar-item">
                <div class="bar-label">${displayName}</div>
                <div class="bar-wrapper">
                    <div class="bar-fill" style="width: ${percentage}%; background: linear-gradient(90deg, var(--danger-color), #c53030)">
                        ${count} incidents
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

async function loadRecentAlerts() {
    const result = await apiCall('/alerts?limit=5');
    if (result && result.success) {
        renderRecentAlerts(result.alerts);
    }
}

function renderRecentAlerts(alerts) {
    const container = document.getElementById('recent-alerts');

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No alerts to display</p>';
        return;
    }

    let html = '';
    alerts.forEach(alert => {
        const severity = alert.severity || 'low';
        const alertType = (alert.alert_type || 'unknown').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        html += `
            <div class="alert-item ${severity}">
                <div class="alert-header">
                    <span class="alert-type">${alertType}</span>
                    <span class="severity-badge ${severity}">${severity}</span>
                </div>
                <div class="alert-description">${alert.description || 'No description'}</div>
                <div class="alert-timestamp">${formatTimestamp(alert.timestamp)}</div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Log Functions
async function loadLogs() {
    showLoading();
    const type = document.getElementById('log-type-filter').value;
    const url = type ? `/logs?type=${type}&limit=100` : '/logs?limit=100';

    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        currentData.logs = result.logs;
        renderLogsTable(result.logs);
    }
}

function renderLogsTable(logs) {
    const tbody = document.getElementById('logs-tbody');

    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No logs available</td></tr>';
        return;
    }

    let html = '';
    logs.forEach(log => {
        const status = log.is_suspicious ? '🔴 Suspicious' : '✅ Normal';
        const summary = formatLogSummary(log);
        const source = log.source_ip || log.client_ip || 'N/A';

        html += `
            <tr>
                <td>${formatTimestamp(log.timestamp)}</td>
                <td><span class="badge">${(log.log_type || '').toUpperCase()}</span></td>
                <td>${summary}</td>
                <td>${source}</td>
                <td>${status}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

function formatLogSummary(log) {
    if (log.log_type === 'http' || log.path) {
        return `${log.method || 'GET'} ${log.path || 'N/A'} - ${log.status_code || 'N/A'}`;
    } else if (log.log_type === 'ssh') {
        return `SSH ${log.status || 'N/A'} - User: ${log.user || 'N/A'}`;
    } else if (log.log_type === 'dns') {
        return `DNS Query: ${log.query || 'N/A'} - ${log.response_code || 'N/A'}`;
    } else if (log.log_type === 'ftp') {
        return `FTP ${log.action || 'N/A'} - User: ${log.user || 'N/A'}`;
    }
    return 'N/A';
}

function filterLogs() {
    loadLogs();
}

function searchLogs() {
    const searchTerm = document.getElementById('log-search').value.toLowerCase();
    if (!searchTerm) {
        renderLogsTable(currentData.logs);
        return;
    }

    const filtered = currentData.logs.filter(log => {
        return JSON.stringify(log).toLowerCase().includes(searchTerm);
    });

    renderLogsTable(filtered);
}

// Alert Functions
async function loadAlerts() {
    showLoading();
    const severity = document.getElementById('alert-severity-filter')?.value || '';
    const url = severity ? `/alerts?severity=${severity}&limit=50` : '/alerts?limit=50';

    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        currentData.alerts = result.alerts;
        renderAlertsGrid(result.alerts);
    }
}

function renderAlertsGrid(alerts) {
    const container = document.getElementById('alerts-container');

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No alerts to display</p>';
        return;
    }

    let html = '';
    alerts.forEach(alert => {
        const severity = alert.severity || 'low';
        const alertType = (alert.alert_type || 'unknown').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const indicators = alert.indicators ? JSON.stringify(alert.indicators, null, 2) : 'None';

        html += `
            <div class="alert-item ${severity}">
                <div class="alert-header">
                    <span class="alert-type">${alertType}</span>
                    <span class="severity-badge ${severity}">${severity}</span>
                </div>
                <div class="alert-description">${alert.description || 'No description'}</div>
                <details style="margin-top: 10px;">
                    <summary style="cursor: pointer; color: var(--primary-color);">View Details</summary>
                    <pre style="margin-top: 10px; padding: 10px; background: var(--bg-dark); border-radius: 5px; overflow-x: auto; font-size: 0.85em;">${indicators}</pre>
                </details>
                <div class="alert-timestamp">${formatTimestamp(alert.timestamp)}</div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function filterAlerts() {
    loadAlerts();
}

// Query Functions
async function executeQuery() {
    const query = document.getElementById('spl-query').value.trim();
    if (!query) {
        showToast('Please enter a query', 'warning');
        return;
    }

    showLoading();
    const result = await apiCall('/query', {
        method: 'POST',
        body: JSON.stringify({ query })
    });
    hideLoading();

    if (result && result.success) {
        renderQueryResults(result.results, query);
        showToast('Query executed successfully', 'success');
    } else {
        showToast('Query failed: ' + (result?.error || 'Unknown error'), 'error');
    }
}

function renderQueryResults(results, query) {
    const container = document.getElementById('query-results');

    if (!results) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No results</p>';
        return;
    }

    let html = `<h3>Query Results</h3><p style="color: var(--text-secondary); margin-bottom: 15px;">${query}</p>`;

    if (Array.isArray(results)) {
        html += `<p><strong>Results: ${results.length} records</strong></p>`;
        html += '<pre style="background: var(--bg-card); padding: 15px; border-radius: 8px; overflow-x: auto; max-height: 500px;">';
        html += JSON.stringify(results, null, 2);
        html += '</pre>';
    } else {
        html += '<pre style="background: var(--bg-card); padding: 15px; border-radius: 8px; overflow-x: auto;">';
        html += JSON.stringify(results, null, 2);
        html += '</pre>';
    }

    container.innerHTML = html;
}

function showExampleQueries() {
    const examples = [
        'search http | where status_code>400',
        'search ssh | where status=failed',
        'search dns | top query',
        'search http | stats count by status_code',
        'search is_suspicious=true'
    ];

    const exampleText = examples.join('\n');
    document.getElementById('spl-query').value = exampleText;
    showToast('Example queries loaded', 'info');
}

// Settings Functions
async function generateLogs() {
    const count = parseInt(document.getElementById('log-count').value);
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    const types = Array.from(checkboxes).map(cb => cb.value);

    if (types.length === 0) {
        showToast('Please select at least one log type', 'warning');
        return;
    }

    showLoading();
    const result = await apiCall('/generate-logs', {
        method: 'POST',
        body: JSON.stringify({ count, types })
    });
    hideLoading();

    if (result && result.success) {
        showToast(result.message, 'success');
        document.getElementById('last-update').textContent = new Date().toLocaleString();
        loadStats();
    } else {
        showToast('Failed to generate logs: ' + (result?.error || 'Unknown error'), 'error');
    }
}

// Analysis Functions
async function runAnalysis() {
    showLoading();
    const result = await apiCall('/analyze', {
        method: 'POST'
    });
    hideLoading();

    if (result && result.success) {
        showToast(`Analysis complete: ${result.total_alerts} alerts detected`, 'success');
        renderAnalysisResults(result);
        loadStats();
    } else {
        showToast('Analysis failed: ' + (result?.error || 'Unknown error'), 'error');
    }
}

function renderAnalysisResults(result) {
    const container = document.getElementById('analysis-results');

    let html = `
        <h3>Analysis Results</h3>
        <div class="stats-grid" style="margin-top: 20px;">
            <div class="stat-card danger">
                <div class="stat-info">
                    <h3>Total Alerts</h3>
                    <div class="stat-number">${result.total_alerts}</div>
                </div>
            </div>
        </div>
        <h4 style="margin-top: 20px;">Severity Breakdown</h4>
        <pre style="background: var(--bg-card); padding: 15px; border-radius: 8px; margin-top: 10px;">${JSON.stringify(result.severity_breakdown, null, 2)}</pre>
        <h4 style="margin-top: 20px;">Alert Types</h4>
        <pre style="background: var(--bg-card); padding: 15px; border-radius: 8px; margin-top: 10px;">${JSON.stringify(result.alert_types, null, 2)}</pre>
    `;

    container.innerHTML = html;
}

async function clearAllData() {
    if (!confirm('Are you sure you want to clear all data?')) {
        return;
    }

    showLoading();
    const result = await apiCall('/clear', {
        method: 'POST'
    });
    hideLoading();

    if (result && result.success) {
        showToast('All data cleared', 'success');
        loadStats();
        document.getElementById('analysis-results').innerHTML = '';
    } else {
        showToast('Failed to clear data', 'error');
    }
}

// Utility Functions
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function refreshData() {
    loadStats();
    showToast('Data refreshed', 'info');
}
