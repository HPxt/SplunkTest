#!/usr/bin/env python3
"""
Dashboard Generator
Creates HTML dashboard with security metrics and visualizations
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime


class DashboardGenerator:
    """Generate interactive HTML dashboard"""

    def __init__(self, logs_data: dict, alerts_data: dict = None):
        self.logs_data = logs_data
        self.alerts_data = alerts_data or {}

    def generate_html(self, output_file: str):
        """Generate complete HTML dashboard"""

        # Calculate statistics
        stats = self._calculate_statistics()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Splunk SIEM Dashboard - Security Analytics</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f0f1e;
            color: #e0e0e0;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: #1a1a2e;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}

        .stat-card.primary {{
            border-color: #667eea;
        }}

        .stat-card.danger {{
            border-color: #f56565;
        }}

        .stat-card.warning {{
            border-color: #ed8936;
        }}

        .stat-card.success {{
            border-color: #48bb78;
        }}

        .stat-card h3 {{
            color: #a0a0a0;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-label {{
            color: #808080;
            font-size: 0.9em;
        }}

        .alerts-section {{
            background: #1a1a2e;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}

        .alerts-section h2 {{
            margin-bottom: 20px;
            color: #f56565;
        }}

        .alert-item {{
            background: #252538;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid;
        }}

        .alert-item.critical {{
            border-color: #c53030;
        }}

        .alert-item.high {{
            border-color: #f56565;
        }}

        .alert-item.medium {{
            border-color: #ed8936;
        }}

        .alert-item.low {{
            border-color: #ecc94b;
        }}

        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .alert-type {{
            font-weight: bold;
            font-size: 1.1em;
        }}

        .severity-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .severity-badge.critical {{
            background: #c53030;
        }}

        .severity-badge.high {{
            background: #f56565;
        }}

        .severity-badge.medium {{
            background: #ed8936;
        }}

        .severity-badge.low {{
            background: #ecc94b;
            color: #1a1a2e;
        }}

        .chart-container {{
            background: #1a1a2e;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}

        .chart-container h2 {{
            margin-bottom: 20px;
        }}

        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .bar-item {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .bar-label {{
            min-width: 150px;
            font-weight: 500;
        }}

        .bar-wrapper {{
            flex: 1;
            background: #252538;
            border-radius: 5px;
            overflow: hidden;
        }}

        .bar-fill {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}

        .log-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .log-table th {{
            background: #252538;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #667eea;
        }}

        .log-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #2a2a3e;
        }}

        .log-table tr:hover {{
            background: #252538;
        }}

        .timestamp {{
            color: #9ca3af;
            font-size: 0.9em;
        }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ Splunk SIEM Dashboard</h1>
            <p class="subtitle">Security Information and Event Management - Real-time Analytics</p>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card primary">
                <h3>Total Events</h3>
                <div class="stat-value">{stats['total_logs']:,}</div>
                <div class="stat-label">Logs processed</div>
            </div>

            <div class="stat-card danger">
                <h3>Security Alerts</h3>
                <div class="stat-value">{stats['total_alerts']}</div>
                <div class="stat-label">Threats detected</div>
            </div>

            <div class="stat-card warning">
                <h3>Critical Events</h3>
                <div class="stat-value">{stats['critical_count']}</div>
                <div class="stat-label">Requires attention</div>
            </div>

            <div class="stat-card success">
                <h3>Log Sources</h3>
                <div class="stat-value">{stats['log_types']}</div>
                <div class="stat-label">Active sources</div>
            </div>
        </div>

        {self._generate_alerts_section()}

        {self._generate_log_distribution_chart(stats)}

        {self._generate_top_threats_chart(stats)}

        {self._generate_recent_events_table(stats)}

        <footer>
            <p>Splunk SIEM MVP - Security Analytics Platform</p>
            <p>Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </footer>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"Dashboard generated: {output_file}")

    def _calculate_statistics(self) -> dict:
        """Calculate dashboard statistics"""
        total_logs = sum(len(logs) for logs in self.logs_data.values())
        total_alerts = self.alerts_data.get('total_alerts', 0)

        critical_count = 0
        if 'alerts' in self.alerts_data:
            critical_count = sum(1 for alert in self.alerts_data['alerts']
                               if alert.get('severity') == 'critical')

        log_types = len(self.logs_data.keys())

        return {
            'total_logs': total_logs,
            'total_alerts': total_alerts,
            'critical_count': critical_count,
            'log_types': log_types,
            'logs_data': self.logs_data,
            'alerts_data': self.alerts_data
        }

    def _generate_alerts_section(self) -> str:
        """Generate alerts section HTML"""
        if not self.alerts_data or 'alerts' not in self.alerts_data:
            return ""

        alerts = self.alerts_data['alerts'][:10]  # Top 10 alerts

        alerts_html = """
        <div class="alerts-section">
            <h2>🚨 Recent Security Alerts</h2>
        """

        for alert in alerts:
            severity = alert.get('severity', 'low')
            alert_type = alert.get('alert_type', 'unknown')
            description = alert.get('description', 'No description')

            alerts_html += f"""
            <div class="alert-item {severity}">
                <div class="alert-header">
                    <span class="alert-type">{alert_type.replace('_', ' ').title()}</span>
                    <span class="severity-badge {severity}">{severity}</span>
                </div>
                <p>{description}</p>
                <p class="timestamp">{alert.get('timestamp', 'N/A')}</p>
            </div>
            """

        alerts_html += "</div>"
        return alerts_html

    def _generate_log_distribution_chart(self, stats: dict) -> str:
        """Generate log distribution bar chart"""
        log_counts = {log_type: len(logs) for log_type, logs in self.logs_data.items()}
        max_count = max(log_counts.values()) if log_counts else 1

        chart_html = """
        <div class="chart-container">
            <h2>📊 Log Distribution by Type</h2>
            <div class="bar-chart">
        """

        for log_type, count in sorted(log_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / max_count) * 100

            chart_html += f"""
                <div class="bar-item">
                    <div class="bar-label">{log_type.upper()}</div>
                    <div class="bar-wrapper">
                        <div class="bar-fill" style="width: {percentage}%">
                            {count:,} events
                        </div>
                    </div>
                </div>
            """

        chart_html += """
            </div>
        </div>
        """
        return chart_html

    def _generate_top_threats_chart(self, stats: dict) -> str:
        """Generate top threats chart"""
        if not self.alerts_data or 'alert_types' not in self.alerts_data:
            return ""

        alert_types = dict(self.alerts_data['alert_types'].most_common(10))
        max_count = max(alert_types.values()) if alert_types else 1

        chart_html = """
        <div class="chart-container">
            <h2>⚠️ Top Threat Types</h2>
            <div class="bar-chart">
        """

        for threat_type, count in alert_types.items():
            percentage = (count / max_count) * 100

            chart_html += f"""
                <div class="bar-item">
                    <div class="bar-label">{threat_type.replace('_', ' ').title()}</div>
                    <div class="bar-wrapper">
                        <div class="bar-fill" style="width: {percentage}%; background: linear-gradient(90deg, #f56565 0%, #c53030 100%)">
                            {count} incidents
                        </div>
                    </div>
                </div>
            """

        chart_html += """
            </div>
        </div>
        """
        return chart_html

    def _generate_recent_events_table(self, stats: dict) -> str:
        """Generate recent events table"""
        # Collect recent events from all log types
        recent_events = []

        for log_type, logs in self.logs_data.items():
            for log in logs[-5:]:  # Last 5 from each type
                recent_events.append({
                    'type': log_type,
                    'timestamp': log.get('timestamp', 'N/A'),
                    'summary': self._format_log_summary(log),
                    'suspicious': log.get('is_suspicious', False)
                })

        # Sort by timestamp
        recent_events.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_events = recent_events[:20]  # Top 20

        table_html = """
        <div class="chart-container">
            <h2>📋 Recent Events</h2>
            <table class="log-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Type</th>
                        <th>Event Summary</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """

        for event in recent_events:
            status = '🔴 Suspicious' if event['suspicious'] else '✅ Normal'
            table_html += f"""
                <tr>
                    <td class="timestamp">{event['timestamp']}</td>
                    <td>{event['type'].upper()}</td>
                    <td>{event['summary']}</td>
                    <td>{status}</td>
                </tr>
            """

        table_html += """
                </tbody>
            </table>
        </div>
        """
        return table_html

    def _format_log_summary(self, log: dict) -> str:
        """Format log entry into readable summary"""
        log_type = log.get('log_type', '')

        if log_type == 'http' or 'path' in log:
            return f"{log.get('method', 'GET')} {log.get('path', 'N/A')} - {log.get('status_code', 'N/A')}"
        elif log_type == 'ssh' or 'user' in log:
            return f"SSH {log.get('status', 'N/A')} - User: {log.get('user', 'N/A')} from {log.get('source_ip', 'N/A')}"
        elif log_type == 'dns' or 'query' in log:
            return f"DNS Query: {log.get('query', 'N/A')} - {log.get('response_code', 'N/A')}"
        elif log_type == 'ftp':
            return f"FTP {log.get('action', 'N/A')} - User: {log.get('user', 'N/A')}"
        else:
            return str(log)[:100]


if __name__ == '__main__':
    # Example usage
    print("Dashboard Generator - Run with log data to generate HTML dashboard")
