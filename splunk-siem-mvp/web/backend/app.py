#!/usr/bin/env python3
"""
Splunk SIEM Web Application - Backend
Flask REST API Server
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generators.dns_log_generator import DNSLogGenerator
from generators.http_log_generator import HTTPLogGenerator
from generators.ssh_log_generator import SSHLogGenerator
from generators.ftp_log_generator import FTPLogGenerator
from parsers.log_parser import JSONLogParser
from analyzers.anomaly_detector import AnomalyDetector
from analyzers.spl_query_engine import SPLParser

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Global state
logs_cache = {}
alerts_cache = {}
blocked_ips = {}  # {ip: {'reason': str, 'timestamp': str, 'blocked_by': str, 'history': []}}
blocked_ips_history = []  # Complete history of all block/unblock actions
incident_reports = []  # List of incident reports
response_actions = []  # List of response actions taken


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/generate-logs', methods=['POST'])
def generate_logs():
    """Generate logs endpoint"""
    try:
        data = request.json
        count = data.get('count', 100)
        log_types = data.get('types', ['dns', 'http', 'ssh', 'ftp'])

        generated = {}

        if 'dns' in log_types:
            dns_gen = DNSLogGenerator()
            generated['dns'] = dns_gen.generate_logs(count=count, suspicious_ratio=0.08)

        if 'http' in log_types:
            http_gen = HTTPLogGenerator()
            generated['http'] = http_gen.generate_logs(count=count, attack_ratio=0.12)

        if 'ssh' in log_types:
            ssh_gen = SSHLogGenerator()
            generated['ssh'] = ssh_gen.generate_logs(count=count)

        if 'ftp' in log_types:
            ftp_gen = FTPLogGenerator()
            generated['ftp'] = ftp_gen.generate_logs(count=count, attack_ratio=0.1)

        # Cache logs
        logs_cache.update(generated)

        total = sum(len(logs) for logs in generated.values())

        return jsonify({
            'success': True,
            'message': f'Generated {total} logs',
            'details': {k: len(v) for k, v in generated.items()}
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    """Run security analysis"""
    try:
        if not logs_cache:
            return jsonify({'success': False, 'error': 'No logs to analyze'}), 400

        # Flatten logs
        all_logs = []
        for log_type, logs in logs_cache.items():
            for log in logs:
                log['log_type'] = log_type
                all_logs.append(log)

        # Run analysis
        detector = AnomalyDetector()
        results = detector.analyze_all(all_logs)

        # Cache alerts
        alerts_cache.update(results)

        return jsonify({
            'success': True,
            'total_alerts': results['total_alerts'],
            'severity_breakdown': results['severity_breakdown'],
            'alert_types': dict(results['alert_types'])
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute SPL query"""
    try:
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400

        if not logs_cache:
            return jsonify({'success': False, 'error': 'No logs available'}), 400

        # Flatten logs
        all_logs = []
        for log_type, logs in logs_cache.items():
            for log in logs:
                log['log_type'] = log_type
                all_logs.append(log)

        # Execute query
        parser = SPLParser(all_logs)
        results = parser.execute(query)

        # Limit results
        if isinstance(results, list):
            results = results[:100]  # Limit to 100 results

        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logs')
def get_logs():
    """Get all logs"""
    try:
        log_type = request.args.get('type')
        limit = int(request.args.get('limit', 100))

        if log_type and log_type in logs_cache:
            logs = logs_cache[log_type][:limit]
        else:
            # Get all logs
            all_logs = []
            for lt, log_list in logs_cache.items():
                for log in log_list[:limit]:
                    log['log_type'] = lt
                    all_logs.append(log)
            logs = all_logs[:limit]

        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': logs
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts')
def get_alerts():
    """Get security alerts"""
    try:
        if not alerts_cache:
            return jsonify({
                'success': True,
                'total_alerts': 0,
                'alerts': []
            })

        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity')

        alerts = alerts_cache.get('alerts', [])

        if severity:
            alerts = [a for a in alerts if a.get('severity') == severity]

        return jsonify({
            'success': True,
            'total_alerts': len(alerts),
            'alerts': alerts[:limit]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get SIEM statistics"""
    try:
        total_logs = sum(len(logs) for logs in logs_cache.values())
        total_alerts = alerts_cache.get('total_alerts', 0)

        stats = {
            'total_logs': total_logs,
            'total_alerts': total_alerts,
            'log_types': len(logs_cache),
            'critical_alerts': sum(1 for alert in alerts_cache.get('alerts', [])
                                  if alert.get('severity') == 'critical'),
            'high_alerts': sum(1 for alert in alerts_cache.get('alerts', [])
                              if alert.get('severity') == 'high'),
            'medium_alerts': sum(1 for alert in alerts_cache.get('alerts', [])
                                if alert.get('severity') == 'medium'),
            'low_alerts': sum(1 for alert in alerts_cache.get('alerts', [])
                             if alert.get('severity') == 'low'),
            'logs_by_type': {k: len(v) for k, v in logs_cache.items()},
            'alert_types': dict(alerts_cache.get('alert_types', {}))
        }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear all data"""
    try:
        logs_cache.clear()
        alerts_cache.clear()

        return jsonify({
            'success': True,
            'message': 'All data cleared'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INCIDENT RESPONSE ENDPOINTS
# ============================================================================

@app.route('/api/block-ip', methods=['POST'])
def block_ip():
    """Block an IP address"""
    try:
        data = request.json
        ip = data.get('ip', '').strip()
        reason = data.get('reason', 'Suspicious activity detected')
        blocked_by = data.get('blocked_by', 'System')

        if not ip:
            return jsonify({'success': False, 'error': 'IP address is required'}), 400

        # Validate IP format (basic)
        if not (ip.count('.') == 3 or ':' in ip):  # IPv4 or IPv6
            return jsonify({'success': False, 'error': 'Invalid IP address format'}), 400

        # Check if IP was previously blocked
        was_blocked = ip in blocked_ips and blocked_ips[ip].get('status') == 'blocked'
        
        # Create or update blocked IP entry
        if ip not in blocked_ips:
            blocked_ips[ip] = {
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'blocked_by': blocked_by,
                'status': 'blocked',
                'history': []
            }
        else:
            # Add to history
            if 'history' not in blocked_ips[ip]:
                blocked_ips[ip]['history'] = []
            blocked_ips[ip]['history'].append({
                'action': 'unblocked' if blocked_ips[ip].get('status') == 'unblocked' else 're-blocked',
                'timestamp': blocked_ips[ip].get('timestamp'),
                'reason': blocked_ips[ip].get('reason'),
                'by': blocked_ips[ip].get('blocked_by')
            })
            # Update current status
            blocked_ips[ip]['reason'] = reason
            blocked_ips[ip]['timestamp'] = datetime.now().isoformat()
            blocked_ips[ip]['blocked_by'] = blocked_by
            blocked_ips[ip]['status'] = 'blocked'

        # Add to global history
        blocked_ips_history.append({
            'ip': ip,
            'action': 'blocked',
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'blocked_by': blocked_by
        })

        # Remove alerts related to this IP
        alerts_removed = 0
        if alerts_cache and 'alerts' in alerts_cache:
            original_count = len(alerts_cache['alerts'])
            alerts_cache['alerts'] = [
                alert for alert in alerts_cache['alerts']
                if alert.get('indicators', {}).get('source_ip') != ip
                and alert.get('indicators', {}).get('client_ip') != ip
                and alert.get('indicators', {}).get('ip') != ip
            ]
            alerts_removed = original_count - len(alerts_cache['alerts'])
            
            # Update total_alerts
            if 'total_alerts' in alerts_cache:
                alerts_cache['total_alerts'] = max(0, alerts_cache['total_alerts'] - alerts_removed)

        # Log response action
        response_actions.append({
            'action': 'block_ip',
            'target': ip,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'user': blocked_by,
            'alerts_removed': alerts_removed
        })

        return jsonify({
            'success': True,
            'message': f'IP {ip} blocked successfully. {alerts_removed} related alert(s) removed.',
            'blocked_ip': blocked_ips[ip],
            'alerts_removed': alerts_removed
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/unblock-ip', methods=['POST'])
def unblock_ip():
    """Unblock an IP address"""
    try:
        data = request.json
        ip = data.get('ip', '').strip()
        unblocked_by = data.get('unblocked_by', 'System')

        if not ip:
            return jsonify({'success': False, 'error': 'IP address is required'}), 400

        if ip not in blocked_ips:
            return jsonify({'success': False, 'error': 'IP is not blocked'}), 404

        # Add to history before unblocking
        if 'history' not in blocked_ips[ip]:
            blocked_ips[ip]['history'] = []
        blocked_ips[ip]['history'].append({
            'action': 'blocked',
            'timestamp': blocked_ips[ip].get('timestamp'),
            'reason': blocked_ips[ip].get('reason'),
            'by': blocked_ips[ip].get('blocked_by')
        })

        # Mark as unblocked but keep history
        blocked_ips[ip]['status'] = 'unblocked'
        blocked_ips[ip]['unblocked_at'] = datetime.now().isoformat()
        blocked_ips[ip]['unblocked_by'] = unblocked_by

        # Add to global history
        blocked_ips_history.append({
            'ip': ip,
            'action': 'unblocked',
            'reason': 'Manual unblock',
            'timestamp': datetime.now().isoformat(),
            'unblocked_by': unblocked_by
        })

        # Log response action
        response_actions.append({
            'action': 'unblock_ip',
            'target': ip,
            'reason': 'Manual unblock',
            'timestamp': datetime.now().isoformat(),
            'user': unblocked_by
        })

        return jsonify({
            'success': True,
            'message': f'IP {ip} unblocked successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/blocked-ips')
def get_blocked_ips():
    """Get list of blocked IPs"""
    try:
        status_filter = request.args.get('status', 'all')  # all, blocked, unblocked
        include_history = request.args.get('include_history', 'false').lower() == 'true'

        if status_filter == 'blocked':
            filtered = {ip: info for ip, info in blocked_ips.items() if info.get('status') == 'blocked'}
        elif status_filter == 'unblocked':
            filtered = {ip: info for ip, info in blocked_ips.items() if info.get('status') == 'unblocked'}
        else:
            filtered = blocked_ips

        return jsonify({
            'success': True,
            'blocked_ips': filtered,
            'total': len(filtered),
            'active_blocks': sum(1 for info in blocked_ips.values() if info.get('status') == 'blocked'),
            'history': blocked_ips_history if include_history else []
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/report-incident', methods=['POST'])
def report_incident():
    """Create an incident report"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        severity = data.get('severity', 'medium')
        related_ips = data.get('related_ips', [])
        related_alerts = data.get('related_alerts', [])
        reported_by = data.get('reported_by', 'User')

        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400

        report = {
            'id': len(incident_reports) + 1,
            'title': title,
            'description': description,
            'severity': severity,
            'related_ips': related_ips if isinstance(related_ips, list) else [],
            'related_alerts': related_alerts if isinstance(related_alerts, list) else [],
            'reported_by': reported_by,
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        incident_reports.append(report)

        # Log response action
        response_actions.append({
            'action': 'report_incident',
            'target': f"Report #{report['id']}",
            'reason': title,
            'timestamp': datetime.now().isoformat(),
            'user': reported_by
        })

        return jsonify({
            'success': True,
            'message': 'Incident report created successfully',
            'report': report
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/incident-reports')
def get_incident_reports():
    """Get all incident reports"""
    try:
        status_filter = request.args.get('status')  # open, closed, all
        severity_filter = request.args.get('severity')  # critical, high, medium, low

        filtered = incident_reports.copy()

        if status_filter and status_filter != 'all':
            filtered = [r for r in filtered if r.get('status') == status_filter]

        if severity_filter:
            filtered = [r for r in filtered if r.get('severity') == severity_filter]

        # Sort by created_at (newest first)
        filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'reports': filtered,
            'total': len(filtered),
            'open': sum(1 for r in incident_reports if r.get('status') == 'open')
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/update-incident', methods=['POST'])
def update_incident():
    """Update incident report status"""
    try:
        data = request.json
        report_id = data.get('id')
        status = data.get('status')  # open, investigating, resolved, closed
        notes = data.get('notes', '')

        if not report_id:
            return jsonify({'success': False, 'error': 'Report ID is required'}), 400

        # Find report
        report = next((r for r in incident_reports if r.get('id') == report_id), None)
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404

        if status:
            report['status'] = status
        if notes:
            if 'notes' not in report:
                report['notes'] = []
            report['notes'].append({
                'note': notes,
                'timestamp': datetime.now().isoformat()
            })
        report['updated_at'] = datetime.now().isoformat()

        return jsonify({
            'success': True,
            'message': 'Incident report updated',
            'report': report
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/response-actions')
def get_response_actions():
    """Get all response actions taken"""
    try:
        limit = int(request.args.get('limit', 50))
        action_filter = request.args.get('action')  # block_ip, unblock_ip, report_incident, etc.

        filtered = response_actions.copy()

        if action_filter:
            filtered = [a for a in filtered if a.get('action') == action_filter]

        # Sort by timestamp (newest first)
        filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return jsonify({
            'success': True,
            'actions': filtered[:limit],
            'total': len(filtered)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/quick-block', methods=['POST'])
def quick_block():
    """Quick block IP from alert or log"""
    try:
        data = request.json
        ip = data.get('ip', '').strip()
        source = data.get('source', 'manual')  # alert, log, manual
        source_id = data.get('source_id')

        if not ip:
            return jsonify({'success': False, 'error': 'IP address is required'}), 400

        reason = f'Quick block from {source}'
        if source_id:
            reason += f' (ID: {source_id})'

        # Check if IP was previously blocked
        was_blocked = ip in blocked_ips and blocked_ips[ip].get('status') == 'blocked'
        
        # Create or update blocked IP entry
        if ip not in blocked_ips:
            blocked_ips[ip] = {
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'blocked_by': 'System',
                'status': 'blocked',
                'source': source,
                'source_id': source_id,
                'history': []
            }
        else:
            # Add to history
            if 'history' not in blocked_ips[ip]:
                blocked_ips[ip]['history'] = []
            if blocked_ips[ip].get('status') != 'blocked':
                blocked_ips[ip]['history'].append({
                    'action': 'unblocked',
                    'timestamp': blocked_ips[ip].get('unblocked_at'),
                    'reason': 'Previous unblock',
                    'by': blocked_ips[ip].get('unblocked_by', 'System')
                })
            # Update current status
            blocked_ips[ip]['reason'] = reason
            blocked_ips[ip]['timestamp'] = datetime.now().isoformat()
            blocked_ips[ip]['blocked_by'] = 'System'
            blocked_ips[ip]['status'] = 'blocked'
            blocked_ips[ip]['source'] = source
            blocked_ips[ip]['source_id'] = source_id

        # Add to global history
        blocked_ips_history.append({
            'ip': ip,
            'action': 'blocked',
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'blocked_by': 'System',
            'source': source,
            'source_id': source_id
        })

        # Remove alerts related to this IP
        alerts_removed = 0
        if alerts_cache and 'alerts' in alerts_cache:
            original_count = len(alerts_cache['alerts'])
            alerts_cache['alerts'] = [
                alert for alert in alerts_cache['alerts']
                if alert.get('indicators', {}).get('source_ip') != ip
                and alert.get('indicators', {}).get('client_ip') != ip
                and alert.get('indicators', {}).get('ip') != ip
            ]
            alerts_removed = original_count - len(alerts_cache['alerts'])
            
            # Update total_alerts
            if 'total_alerts' in alerts_cache:
                alerts_cache['total_alerts'] = max(0, alerts_cache['total_alerts'] - alerts_removed)

        # Log action
        response_actions.append({
            'action': 'quick_block',
            'target': ip,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'user': 'System',
            'alerts_removed': alerts_removed
        })

        return jsonify({
            'success': True,
            'message': f'IP {ip} blocked successfully',
            'blocked_ip': blocked_ips[ip]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         SPLUNK SIEM WEB APPLICATION - BACKEND                ║
    ╚══════════════════════════════════════════════════════════════╝

    Starting Flask server...

    🌐 Web Interface: http://localhost:5000
    📡 API Endpoint: http://localhost:5000/api

    Available Endpoints:
    - GET  /                    - Main dashboard
    - GET  /api/health         - Health check
    - POST /api/generate-logs  - Generate logs
    - POST /api/analyze        - Run security analysis
    - POST /api/query          - Execute SPL query
    - GET  /api/logs           - Get logs
    - GET  /api/alerts         - Get alerts
    - GET  /api/stats          - Get statistics
    - POST /api/clear          - Clear all data
    - POST /api/block-ip       - Block IP address
    - POST /api/unblock-ip     - Unblock IP address
    - GET  /api/blocked-ips    - Get blocked IPs
    - POST /api/report-incident - Create incident report
    - GET  /api/incident-reports - Get incident reports
    - POST /api/update-incident - Update incident status
    - GET  /api/response-actions - Get response actions
    - POST /api/quick-block    - Quick block IP

    Press Ctrl+C to stop the server
    ══════════════════════════════════════════════════════════════════
    """)

    app.run(host='0.0.0.0', port=5000, debug=True)
