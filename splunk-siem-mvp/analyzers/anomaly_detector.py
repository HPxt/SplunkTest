#!/usr/bin/env python3
"""
Anomaly Detection System
Detects suspicious patterns and anomalies in logs
"""

import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
import re


class AnomalyDetector:
    """Detects security anomalies in parsed logs"""

    def __init__(self):
        self.alerts = []
        self.severity_levels = ['low', 'medium', 'high', 'critical']

        # Known malicious patterns
        self.malicious_patterns = {
            'sql_injection': [
                r"('|\")\s*(OR|AND)\s*('|\")?\s*=\s*('|\")",
                r"(UNION|SELECT|INSERT|UPDATE|DELETE|DROP)\s+(TABLE|FROM|INTO)",
                r"--",
                r";.*DROP",
            ],
            'xss': [
                r"<script[^>]*>",
                r"javascript:",
                r"onerror\s*=",
                r"<iframe",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"/etc/shadow",
                r"windows/system32",
            ],
            'command_injection': [
                r";\s*(ls|cat|wget|curl|nc|bash|sh)\s",
                r"\|\s*(nc|bash|sh)",
                r"`.*`",
            ],
        }

        # Known malicious IPs (example)
        self.known_malicious_ips = {
            '103.45.67.89', '185.220.101.23', '45.154.24.45'
        }

        # Suspicious user agents
        self.suspicious_ua_patterns = [
            'sqlmap', 'nikto', 'acunetix', 'nmap', 'masscan',
            'metasploit', 'burp', 'scanner'
        ]

    def create_alert(self, severity: str, alert_type: str, description: str,
                     log_entry: Dict, indicators: Dict = None) -> Dict:
        """Create a security alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'alert_type': alert_type,
            'description': description,
            'log_entry': log_entry,
            'indicators': indicators or {}
        }
        self.alerts.append(alert)
        return alert

    def detect_http_attacks(self, logs: List[Dict]) -> List[Dict]:
        """Detect HTTP-based attacks"""
        alerts = []

        for log in logs:
            if log.get('log_type') != 'http':
                continue

            path = log.get('path', '')
            user_agent = log.get('user_agent', '').lower()
            client_ip = log.get('client_ip', '')

            # Check for SQL injection
            for pattern in self.malicious_patterns['sql_injection']:
                if re.search(pattern, path, re.IGNORECASE):
                    alerts.append(self.create_alert(
                        severity='high',
                        alert_type='sql_injection',
                        description=f'SQL injection attempt detected in request path',
                        log_entry=log,
                        indicators={'pattern': pattern, 'path': path}
                    ))
                    break

            # Check for XSS
            for pattern in self.malicious_patterns['xss']:
                if re.search(pattern, path, re.IGNORECASE):
                    alerts.append(self.create_alert(
                        severity='medium',
                        alert_type='xss',
                        description=f'Cross-Site Scripting (XSS) attempt detected',
                        log_entry=log,
                        indicators={'pattern': pattern, 'path': path}
                    ))
                    break

            # Check for path traversal
            for pattern in self.malicious_patterns['path_traversal']:
                if re.search(pattern, path, re.IGNORECASE):
                    alerts.append(self.create_alert(
                        severity='high',
                        alert_type='path_traversal',
                        description=f'Path traversal attempt detected',
                        log_entry=log,
                        indicators={'pattern': pattern, 'path': path}
                    ))
                    break

            # Check for malicious user agents
            for ua_pattern in self.suspicious_ua_patterns:
                if ua_pattern in user_agent:
                    alerts.append(self.create_alert(
                        severity='medium',
                        alert_type='scanner_detected',
                        description=f'Security scanner or automated tool detected',
                        log_entry=log,
                        indicators={'user_agent': user_agent}
                    ))
                    break

            # Check for known malicious IPs
            if client_ip in self.known_malicious_ips:
                alerts.append(self.create_alert(
                    severity='critical',
                    alert_type='malicious_ip',
                    description=f'Request from known malicious IP address',
                    log_entry=log,
                    indicators={'ip': client_ip}
                ))

        return alerts

    def detect_ssh_brute_force(self, logs: List[Dict], threshold: int = 5,
                                time_window_minutes: int = 5) -> List[Dict]:
        """Detect SSH brute force attacks"""
        alerts = []
        ssh_logs = [log for log in logs if log.get('log_type') == 'ssh']

        # Group failed attempts by IP
        failed_attempts = defaultdict(list)

        for log in ssh_logs:
            if log.get('status') == 'failed':
                ip = log.get('source_ip')
                timestamp = log.get('timestamp')
                failed_attempts[ip].append((timestamp, log))

        # Check for brute force patterns
        for ip, attempts in failed_attempts.items():
            if len(attempts) >= threshold:
                # Check if attempts are within time window
                attempts.sort(key=lambda x: x[0])
                first_time = datetime.fromisoformat(attempts[0][0])
                last_time = datetime.fromisoformat(attempts[-1][0])
                time_diff = (last_time - first_time).total_seconds() / 60

                if time_diff <= time_window_minutes:
                    alerts.append(self.create_alert(
                        severity='high',
                        alert_type='ssh_brute_force',
                        description=f'SSH brute force attack detected from {ip}',
                        log_entry=attempts[-1][1],
                        indicators={
                            'source_ip': ip,
                            'attempt_count': len(attempts),
                            'time_window_minutes': time_diff,
                            'users_targeted': list(set(a[1].get('user') for a in attempts))
                        }
                    ))

        return alerts

    def detect_dns_anomalies(self, logs: List[Dict]) -> List[Dict]:
        """Detect DNS-based anomalies"""
        alerts = []

        for log in logs:
            if log.get('log_type') != 'dns':
                continue

            query = log.get('query', '')

            # Check for DNS tunneling (very long subdomains)
            if len(query) > 50:
                subdomain = query.split('.')[0]
                if len(subdomain) > 30:
                    alerts.append(self.create_alert(
                        severity='high',
                        alert_type='dns_tunneling',
                        description=f'Potential DNS tunneling detected',
                        log_entry=log,
                        indicators={'query': query, 'length': len(query)}
                    ))

            # Check for DGA (Domain Generation Algorithm) patterns
            # Simple heuristic: random-looking domain names
            if '.' in query:
                domain_parts = query.split('.')
                if len(domain_parts) >= 2:
                    domain_name = domain_parts[0]
                    # Check for high entropy (random-looking)
                    if (len(domain_name) > 8 and
                        not any(word in domain_name.lower() for word in
                               ['google', 'amazon', 'microsoft', 'facebook', 'apple'])):
                        # Count consonant clusters (DGA indicator)
                        consonants = re.findall(r'[bcdfghjklmnpqrstvwxyz]{3,}', domain_name.lower())
                        if len(consonants) >= 2:
                            alerts.append(self.create_alert(
                                severity='medium',
                                alert_type='dga_domain',
                                description=f'Potential DGA-generated domain detected',
                                log_entry=log,
                                indicators={'query': query, 'consonant_clusters': consonants}
                            ))

            # Check for excessive NXDOMAIN responses (potential C2 communication)
            if log.get('response_code') == 'NXDOMAIN':
                # This would need time-based aggregation in real implementation
                pass

        return alerts

    def detect_ftp_anomalies(self, logs: List[Dict]) -> List[Dict]:
        """Detect FTP-based anomalies"""
        alerts = []

        # Track failed login attempts
        failed_logins = defaultdict(int)

        for log in logs:
            if log.get('log_type') != 'ftp':
                continue

            # Check for unauthorized file access attempts
            if log.get('action') in ['download', 'upload']:
                details = log.get('details', '')
                file_path = log.get('file_path', '')

                # Check for sensitive files
                sensitive_patterns = ['/etc/', '/.ssh/', 'password', 'shadow', 'config']
                for pattern in sensitive_patterns:
                    if pattern in file_path.lower() or pattern in details.lower():
                        alerts.append(self.create_alert(
                            severity='high',
                            alert_type='unauthorized_access',
                            description=f'Attempt to access sensitive file via FTP',
                            log_entry=log,
                            indicators={'file_path': file_path}
                        ))
                        break

            # Track failed logins
            if log.get('event_type') == 'login' and log.get('status') == 'failed':
                ip = log.get('source_ip')
                failed_logins[ip] += 1

        # Alert on excessive failed logins
        for ip, count in failed_logins.items():
            if count >= 5:
                alerts.append(self.create_alert(
                    severity='high',
                    alert_type='ftp_brute_force',
                    description=f'Multiple failed FTP login attempts from {ip}',
                    log_entry={'source_ip': ip},
                    indicators={'failed_count': count}
                ))

        return alerts

    def analyze_all(self, logs: List[Dict]) -> Dict:
        """Run all anomaly detection rules"""
        all_alerts = []

        print("Running anomaly detection...")

        # HTTP attacks
        http_alerts = self.detect_http_attacks(logs)
        all_alerts.extend(http_alerts)
        print(f"  - HTTP attacks detected: {len(http_alerts)}")

        # SSH brute force
        ssh_alerts = self.detect_ssh_brute_force(logs)
        all_alerts.extend(ssh_alerts)
        print(f"  - SSH brute force detected: {len(ssh_alerts)}")

        # DNS anomalies
        dns_alerts = self.detect_dns_anomalies(logs)
        all_alerts.extend(dns_alerts)
        print(f"  - DNS anomalies detected: {len(dns_alerts)}")

        # FTP anomalies
        ftp_alerts = self.detect_ftp_anomalies(logs)
        all_alerts.extend(ftp_alerts)
        print(f"  - FTP anomalies detected: {len(ftp_alerts)}")

        # Categorize by severity
        severity_counts = Counter(alert['severity'] for alert in all_alerts)

        return {
            'total_alerts': len(all_alerts),
            'alerts': all_alerts,
            'severity_breakdown': dict(severity_counts),
            'alert_types': Counter(alert['alert_type'] for alert in all_alerts)
        }

    def save_alerts(self, alerts_data: Dict, output_file: str):
        """Save alerts to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)


if __name__ == '__main__':
    # Example usage
    detector = AnomalyDetector()

    # Load sample logs
    sample_logs = [
        {'log_type': 'http', 'path': "/login?user=admin' OR '1'='1", 'client_ip': '192.168.1.1', 'user_agent': 'Mozilla/5.0'},
        {'log_type': 'ssh', 'status': 'failed', 'source_ip': '103.45.67.89', 'user': 'root', 'timestamp': '2025-01-15T10:00:00'},
        {'log_type': 'dns', 'query': 'abcdefghijklmnopqrstuvwxyz.com', 'response_code': 'NXDOMAIN'},
    ]

    results = detector.analyze_all(sample_logs)
    print(f"\nTotal alerts: {results['total_alerts']}")
    print(f"Severity breakdown: {results['severity_breakdown']}")
