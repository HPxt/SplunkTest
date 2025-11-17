// Splunk SIEM Web Application - Frontend JavaScript
// Fixed and Complete Version

const API_BASE = '/api';
let currentData = {
    logs: [],
    alerts: [],
    stats: {}
};

// Initialize app
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Splunk SIEM initializing...');
    initNavigation();
    checkHealth();
    loadStats();
    setInterval(loadStats, 30000); // Refresh every 30 seconds
    console.log('✅ Splunk SIEM ready!');
});

// ============================================================================
// NAVIGATION
// ============================================================================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    console.log(`Found ${navItems.length} navigation items`);

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const pageName = this.dataset.page;
            console.log(`Navigating to: ${pageName}`);
            navigateTo(pageName);
        });
    });
}

function navigateTo(pageName) {
    console.log(`Loading page: ${pageName}`);

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

    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
    } else {
        console.error(`Page not found: page-${pageName}`);
        return;
    }

    // Update header
    const titles = {
        dashboard: ['Security Dashboard', 'Real-time threat monitoring and analysis'],
        logs: ['Event Logs', 'Browse and search security events'],
        alerts: ['Security Alerts', 'Review detected threats and anomalies'],
        search: ['SPL Search', 'Execute custom queries'],
        analysis: ['Security Analysis', 'Run comprehensive threat analysis'],
        'incident-response': ['Incident Response', 'Block IPs, report incidents, and manage responses'],
        settings: ['Settings', 'Configure SIEM parameters']
    };

    if (titles[pageName]) {
        document.getElementById('page-title').textContent = titles[pageName][0];
        document.getElementById('page-subtitle').textContent = titles[pageName][1];
    }

    // Load page data
    if (pageName === 'logs') {
        loadLogs();
    } else if (pageName === 'alerts') {
        loadAlerts();
    } else if (pageName === 'incident-response') {
        loadBlockedIPs();
        loadIncidentReports();
        loadResponseActions();
    } else if (pageName === 'dashboard') {
        loadStats();
    }
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

async function apiCall(endpoint, options = {}) {
    try {
        console.log(`API Call: ${endpoint}`);
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();
        console.log(`API Response:`, data);
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast('API Error: ' + error.message, 'error');
        return null;
    }
}

async function checkHealth() {
    const result = await apiCall('/health');
    const statusElement = document.getElementById('backend-status');

    if (result) {
        statusElement.textContent = 'Online';
        statusElement.className = 'badge badge-success';
        console.log('✅ Backend is online');
    } else {
        statusElement.textContent = 'Offline';
        statusElement.className = 'badge badge-danger';
        console.warn('⚠️ Backend is offline');
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

// ============================================================================
// DASHBOARD
// ============================================================================

function updateDashboard(stats) {
    console.log('Updating dashboard with stats:', stats);

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

function renderLogDistribution(logsByType) {
    const container = document.getElementById('chart-log-distribution');

    if (!container) {
        console.error('Log distribution container not found');
        return;
    }

    if (Object.keys(logsByType).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">No data available. Generate logs in Settings.</p>';
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

    if (!container) {
        console.error('Top threats container not found');
        return;
    }

    if (Object.keys(alertTypes).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">No threats detected yet.</p>';
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

    if (!container) {
        console.error('Recent alerts container not found');
        return;
    }

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">No alerts to display. Run analysis to detect threats.</p>';
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

// ============================================================================
// LOGS PAGE
// ============================================================================

async function loadLogs() {
    showLoading();
    const type = document.getElementById('log-type-filter')?.value || '';
    const url = type ? `/logs?type=${type}&limit=100` : '/logs?limit=100';

    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        currentData.logs = result.logs;
        renderLogsTable(result.logs);
        showToast(`Loaded ${result.logs.length} logs`, 'success');
    } else {
        renderLogsTable([]);
        showToast('No logs available. Generate logs in Settings.', 'warning');
    }
}

function renderLogsTable(logs) {
    const tbody = document.getElementById('logs-tbody');

    if (!tbody) {
        console.error('Logs table body not found');
        return;
    }

    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-secondary); padding: 20px;">No logs available. Go to Settings to generate logs.</td></tr>';
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
    showToast(`Found ${filtered.length} matching logs`, 'info');
}

// ============================================================================
// ALERTS PAGE
// ============================================================================

async function loadAlerts() {
    showLoading();
    const severity = document.getElementById('alert-severity-filter')?.value || '';
    const url = severity ? `/alerts?severity=${severity}&limit=50` : '/alerts?limit=50';

    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        currentData.alerts = result.alerts;
        renderAlertsGrid(result.alerts);
        showToast(`Loaded ${result.alerts.length} alerts`, 'success');
    } else {
        renderAlertsGrid([]);
        showToast('No alerts available. Run analysis first.', 'warning');
    }
}

function renderAlertsGrid(alerts) {
    const container = document.getElementById('alerts-container');

    if (!container) {
        console.error('Alerts container not found');
        return;
    }

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">No alerts to display. Go to Analysis page and run analysis.</p>';
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

// ============================================================================
// SEARCH PAGE (SPL)
// ============================================================================

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

    if (!container) {
        console.error('Query results container not found');
        return;
    }

    if (!results) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 20px;">No results</p>';
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

    const exampleText = examples.join('\n\n# Try these queries:\n\n');
    document.getElementById('spl-query').value = '# Example Queries:\n\n' + exampleText;
    showToast('Example queries loaded', 'info');
}

// ============================================================================
// ANALYSIS PAGE
// ============================================================================

async function runAnalysis() {
    showLoading();
    const result = await apiCall('/analyze', {
        method: 'POST'
    });
    hideLoading();

    if (result && result.success) {
        showToast(`Analysis complete: ${result.total_alerts} alerts detected`, 'success');
        renderAnalysisResults(result);
        loadStats(); // Refresh stats
    } else {
        showToast('Analysis failed: ' + (result?.error || 'No logs to analyze. Generate logs first.'), 'error');
    }
}

function renderAnalysisResults(result) {
    const container = document.getElementById('analysis-results');

    if (!container) {
        console.error('Analysis results container not found');
        return;
    }

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
        currentData = { logs: [], alerts: [], stats: {} };
    } else {
        showToast('Failed to clear data', 'error');
    }
}

// ============================================================================
// SETTINGS PAGE
// ============================================================================

async function generateLogs() {
    const count = parseInt(document.getElementById('log-count').value);
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    const types = Array.from(checkboxes).map(cb => cb.value);

    if (types.length === 0) {
        showToast('Please select at least one log type', 'warning');
        return;
    }

    if (count < 10 || count > 10000) {
        showToast('Count must be between 10 and 10000', 'warning');
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

        // Navigate to dashboard
        setTimeout(() => {
            navigateTo('dashboard');
        }, 1000);
    } else {
        showToast('Failed to generate logs: ' + (result?.error || 'Unknown error'), 'error');
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

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
    try {
        const date = new Date(timestamp);
        return date.toLocaleString();
    } catch (e) {
        return timestamp;
    }
}

function refreshData() {
    loadStats();
    showToast('Data refreshed', 'info');
}

// ============================================================================
// GLOBAL ERROR HANDLER
// ============================================================================

window.addEventListener('error', function (e) {
    console.error('Global error:', e.error);
});

// ============================================================================
// INCIDENT RESPONSE FUNCTIONS
// ============================================================================

async function blockIP() {
    const ip = document.getElementById('block-ip-input').value.trim();
    const reason = document.getElementById('block-reason-input').value.trim() || 'Suspicious activity detected';

    if (!ip) {
        showToast('Please enter an IP address', 'warning');
        return;
    }

    showLoading();
    const result = await apiCall('/block-ip', {
        method: 'POST',
        body: JSON.stringify({
            ip: ip,
            reason: reason,
            blocked_by: 'User'
        })
    });
    hideLoading();

    if (result && result.success) {
        showToast(result.message, 'success');
        document.getElementById('block-ip-input').value = '';
        document.getElementById('block-reason-input').value = '';
        loadBlockedIPs();
        loadResponseActions();
        // Update stats to reflect removed alerts
        loadStats();
    } else {
        showToast('Failed to block IP: ' + (result?.error || 'Unknown error'), 'error');
    }
}

async function unblockIP(ip) {
    if (!confirm(`Are you sure you want to unblock ${ip}?`)) {
        return;
    }

    showLoading();
    const result = await apiCall('/unblock-ip', {
        method: 'POST',
        body: JSON.stringify({
            ip: ip,
            unblocked_by: 'User'
        })
    });
    hideLoading();

    if (result && result.success) {
        showToast(result.message, 'success');
        loadBlockedIPs();
        loadResponseActions();
    } else {
        showToast('Failed to unblock IP: ' + (result?.error || 'Unknown error'), 'error');
    }
}

async function loadBlockedIPs() {
    const statusFilter = document.getElementById('blocked-ip-filter')?.value || 'all';
    const url = `/blocked-ips?status=${statusFilter}&include_history=true`;

    showLoading();
    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        renderBlockedIPs(result.blocked_ips, result.active_blocks, result.history);
    }
}

function renderBlockedIPs(blockedIPs, activeBlocks, history) {
    const container = document.getElementById('blocked-ips-container');

    if (!blockedIPs || Object.keys(blockedIPs).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No blocked IPs</p>';
        return;
    }

    let html = `<div style="margin-bottom: 15px;"><strong>Active Blocks: ${activeBlocks}</strong></div>`;
    html += '<div class="blocked-ips-grid">';

    for (const [ip, info] of Object.entries(blockedIPs)) {
        const status = info.status || 'blocked';
        const statusClass = status === 'blocked' ? 'danger' : 'success';
        const timestamp = formatTimestamp(info.timestamp);
        const historyItems = info.history || [];

        html += `
            <div class="blocked-ip-card ${statusClass}">
                <div class="blocked-ip-header">
                    <span class="ip-address">${ip}</span>
                    <span class="badge badge-${statusClass}">${status}</span>
                </div>
                <div class="blocked-ip-info">
                    <p><strong>Current Reason:</strong> ${info.reason || 'N/A'}</p>
                    <p><strong>Blocked:</strong> ${timestamp}</p>
                    <p><strong>By:</strong> ${info.blocked_by || 'System'}</p>
                    ${info.source ? `<p><strong>Source:</strong> ${info.source}</p>` : ''}
                    ${info.unblocked_at ? `<p><strong>Unblocked:</strong> ${formatTimestamp(info.unblocked_at)}</p>` : ''}
                </div>
                ${historyItems.length > 0 ? `
                    <details style="margin-top: 10px;">
                        <summary style="cursor: pointer; color: var(--primary-color); font-weight: bold;">📜 View History (${historyItems.length} entries)</summary>
                        <div style="margin-top: 10px; padding: 10px; background: var(--bg-dark); border-radius: 5px; max-height: 200px; overflow-y: auto;">
                            ${historyItems.map(h => `
                                <div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border-color);">
                                    <p><strong>${h.action === 'blocked' ? '🚫 Blocked' : '✅ Unblocked'}</strong> - ${formatTimestamp(h.timestamp)}</p>
                                    <p style="font-size: 0.9em; color: var(--text-secondary);"><strong>Reason:</strong> ${h.reason || 'N/A'}</p>
                                    <p style="font-size: 0.85em; color: var(--text-secondary);">By: ${h.by || 'System'}</p>
                                </div>
                            `).join('')}
                        </div>
                    </details>
                ` : ''}
                <div class="blocked-ip-actions">
                    ${status === 'blocked' ? `<button class="btn-small btn-success" onclick="unblockIP('${ip}')">Unblock</button>` : ''}
                    <button class="btn-small btn-danger" onclick="quickBlockIP('${ip}')">Block Again</button>
                </div>
            </div>
        `;
    }

    html += '</div>';

    // Add global history section
    if (history && history.length > 0) {
        html += `
            <div style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px;">📜 Complete Block History</h3>
                <div style="max-height: 400px; overflow-y: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>IP</th>
                                <th>Action</th>
                                <th>Reason</th>
                                <th>By</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${history.slice().reverse().map(h => `
                                <tr>
                                    <td>${formatTimestamp(h.timestamp)}</td>
                                    <td><code>${h.ip}</code></td>
                                    <td>${h.action === 'blocked' ? '🚫 Blocked' : '✅ Unblocked'}</td>
                                    <td>${h.reason || 'N/A'}</td>
                                    <td>${h.blocked_by || h.unblocked_by || 'System'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

async function quickBlockIP(ip) {
    if (!confirm(`Block IP ${ip}?`)) {
        return;
    }

    showLoading();
    const result = await apiCall('/quick-block', {
        method: 'POST',
        body: JSON.stringify({
            ip: ip,
            source: 'manual'
        })
    });
    hideLoading();

    if (result && result.success) {
        showToast(result.message, 'success');
        loadBlockedIPs();
        loadResponseActions();
        // Update stats to reflect removed alerts
        loadStats();
    } else {
        showToast('Failed to block IP: ' + (result?.error || 'Unknown error'), 'error');
    }
}

function showReportModal() {
    const modal = document.getElementById('report-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeReportModal() {
    const modal = document.getElementById('report-modal');
    if (modal) {
        modal.classList.add('hidden');
        // Clear form
        document.getElementById('modal-report-title').value = '';
        document.getElementById('modal-report-description').value = '';
        document.getElementById('modal-report-ips').value = '';
    }
}

async function createIncidentReport() {
    const title = document.getElementById('modal-report-title').value.trim();
    const description = document.getElementById('modal-report-description').value.trim();
    const severity = document.getElementById('modal-report-severity').value;
    const ipsInput = document.getElementById('modal-report-ips').value.trim();

    if (!title) {
        showToast('Title is required', 'warning');
        return;
    }

    const relatedIPs = ipsInput ? ipsInput.split(',').map(ip => ip.trim()).filter(ip => ip) : [];

    showLoading();
    const result = await apiCall('/report-incident', {
        method: 'POST',
        body: JSON.stringify({
            title: title,
            description: description,
            severity: severity,
            related_ips: relatedIPs,
            reported_by: 'User'
        })
    });
    hideLoading();

    if (result && result.success) {
        showToast('Incident report created successfully', 'success');
        closeReportModal();
        loadIncidentReports();
        loadResponseActions();
    } else {
        showToast('Failed to create report: ' + (result?.error || 'Unknown error'), 'error');
    }
}

async function loadIncidentReports() {
    const statusFilter = document.getElementById('report-status-filter')?.value || 'all';
    const severityFilter = document.getElementById('report-severity-filter')?.value || '';

    let url = `/incident-reports?status=${statusFilter}`;
    if (severityFilter) {
        url += `&severity=${severityFilter}`;
    }

    showLoading();
    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        renderIncidentReports(result.reports, result.open);
    }
}

function renderIncidentReports(reports, openCount) {
    const container = document.getElementById('incident-reports-container');

    if (!reports || reports.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No incident reports</p>';
        return;
    }

    let html = `<div style="margin-bottom: 15px;"><strong>Open Reports: ${openCount}</strong></div>`;
    html += '<div class="incident-reports-grid">';

    reports.forEach(report => {
        const severity = report.severity || 'medium';
        const status = report.status || 'open';
        const severityColors = {
            critical: 'danger',
            high: 'warning',
            medium: 'info',
            low: 'success'
        };
        const severityColor = severityColors[severity] || 'info';

        html += `
            <div class="incident-report-card ${severityColor}">
                <div class="report-header">
                    <div>
                        <h4>#${report.id} - ${report.title}</h4>
                        <span class="badge badge-${severityColor}">${severity}</span>
                        <span class="badge">${status}</span>
                    </div>
                </div>
                <div class="report-body">
                    <p>${report.description || 'No description'}</p>
                    ${report.related_ips && report.related_ips.length > 0 ?
                `<p><strong>Related IPs:</strong> ${report.related_ips.join(', ')}</p>` : ''}
                    <p><strong>Reported by:</strong> ${report.reported_by}</p>
                    <p><strong>Created:</strong> ${formatTimestamp(report.created_at)}</p>
                </div>
                <div class="report-actions">
                    <select class="form-select" onchange="updateIncidentStatus(${report.id}, this.value)" style="margin-right: 10px;">
                        <option value="open" ${status === 'open' ? 'selected' : ''}>Open</option>
                        <option value="investigating" ${status === 'investigating' ? 'selected' : ''}>Investigating</option>
                        <option value="resolved" ${status === 'resolved' ? 'selected' : ''}>Resolved</option>
                        <option value="closed" ${status === 'closed' ? 'selected' : ''}>Closed</option>
                    </select>
                    <button class="btn-small btn-danger" onclick="quickBlockFromReport(${report.id})">Block Related IPs</button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

async function updateIncidentStatus(reportId, status) {
    showLoading();
    const result = await apiCall('/update-incident', {
        method: 'POST',
        body: JSON.stringify({
            id: reportId,
            status: status
        })
    });
    hideLoading();

    if (result && result.success) {
        showToast('Incident status updated', 'success');
        loadIncidentReports();
    } else {
        showToast('Failed to update incident: ' + (result?.error || 'Unknown error'), 'error');
    }
}

async function quickBlockFromReport(reportId) {
    const reports = await apiCall('/incident-reports');
    if (!reports || !reports.success) {
        showToast('Failed to load report', 'error');
        return;
    }

    const report = reports.reports.find(r => r.id === reportId);
    if (!report || !report.related_ips || report.related_ips.length === 0) {
        showToast('No IPs to block in this report', 'warning');
        return;
    }

    if (!confirm(`Block ${report.related_ips.length} IP(s) from this report?`)) {
        return;
    }

    let blocked = 0;
    for (const ip of report.related_ips) {
        const result = await apiCall('/quick-block', {
            method: 'POST',
            body: JSON.stringify({
                ip: ip,
                source: 'incident_report',
                source_id: reportId
            })
        });
        if (result && result.success) {
            blocked++;
        }
    }

    showToast(`Blocked ${blocked} IP(s) successfully`, 'success');
    loadBlockedIPs();
    loadResponseActions();
    // Update stats to reflect removed alerts
    loadStats();
}

async function loadResponseActions() {
    const actionFilter = document.getElementById('action-filter')?.value || '';

    let url = '/response-actions?limit=50';
    if (actionFilter) {
        url += `&action=${actionFilter}`;
    }

    showLoading();
    const result = await apiCall(url);
    hideLoading();

    if (result && result.success) {
        renderResponseActions(result.actions);
    }
}

function renderResponseActions(actions) {
    const container = document.getElementById('response-actions-container');

    if (!actions || actions.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No response actions</p>';
        return;
    }

    let html = '<div class="response-actions-table">';
    html += '<table class="data-table"><thead><tr><th>Time</th><th>Action</th><th>Target</th><th>Reason</th><th>User</th></tr></thead><tbody>';

    actions.forEach(action => {
        const actionIcons = {
            block_ip: '🚫',
            unblock_ip: '✅',
            quick_block: '⚡',
            report_incident: '📝'
        };
        const icon = actionIcons[action.action] || '🔧';

        html += `
            <tr>
                <td>${formatTimestamp(action.timestamp)}</td>
                <td>${icon} ${action.action.replace(/_/g, ' ')}</td>
                <td><code>${action.target}</code></td>
                <td>${action.reason || 'N/A'}</td>
                <td>${action.user || 'System'}</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Quick block from alerts page
function quickBlockFromAlert(ip, alertId) {
    if (!confirm(`Block IP ${ip}?`)) {
        return;
    }

    showLoading();
    apiCall('/quick-block', {
        method: 'POST',
        body: JSON.stringify({
            ip: ip,
            source: 'alert',
            source_id: alertId
        })
    }).then(result => {
        hideLoading();
        if (result && result.success) {
            showToast(`IP ${ip} blocked successfully`, 'success');
            loadBlockedIPs();
            loadResponseActions();
            // Update stats to reflect removed alerts
            loadStats();
        } else {
            showToast('Failed to block IP', 'error');
        }
    });
}

console.log('✅ Splunk SIEM app.js loaded successfully');
