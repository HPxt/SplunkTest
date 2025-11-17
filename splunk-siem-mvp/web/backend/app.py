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

    Press Ctrl+C to stop the server
    ══════════════════════════════════════════════════════════════════
    """)

    app.run(host='0.0.0.0', port=5000, debug=True)
