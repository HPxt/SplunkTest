#!/usr/bin/env python3
"""
DNS Log Generator
Generates realistic DNS query logs with normal and anomalous patterns
"""

import random
import datetime
import json
from typing import List, Dict

class DNSLogGenerator:
    def __init__(self):
        self.normal_domains = [
            'google.com', 'facebook.com', 'amazon.com', 'microsoft.com',
            'apple.com', 'netflix.com', 'github.com', 'stackoverflow.com',
            'linkedin.com', 'twitter.com', 'reddit.com', 'youtube.com'
        ]

        self.suspicious_domains = [
            'malicious-site.ru', 'phishing-bank.com', 'cryptominer.xyz',
            'c2-server.tk', 'ransomware-payload.ml', 'data-exfil.cc',
            'botnet-command.ga', 'fake-update.info'
        ]

        self.query_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'PTR']
        self.response_codes = ['NOERROR', 'NXDOMAIN', 'SERVFAIL', 'REFUSED']

        self.internal_ips = [f'192.168.1.{i}' for i in range(10, 250)]
        self.dns_servers = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '192.168.1.1']

    def generate_normal_log(self) -> Dict:
        """Generate a normal DNS query log"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        return {
            'timestamp': timestamp.isoformat(),
            'source_ip': random.choice(self.internal_ips),
            'dns_server': random.choice(self.dns_servers),
            'query': random.choice(self.normal_domains),
            'query_type': random.choice(self.query_types),
            'response_code': random.choice(['NOERROR'] * 9 + ['NXDOMAIN']),
            'response_time_ms': random.randint(5, 150),
            'is_suspicious': False
        }

    def generate_suspicious_log(self) -> Dict:
        """Generate a suspicious DNS query log"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        # Anomaly patterns
        anomaly_type = random.choice([
            'malicious_domain',
            'dns_tunneling',
            'high_frequency',
            'dga_domain'
        ])

        log = {
            'timestamp': timestamp.isoformat(),
            'source_ip': random.choice(self.internal_ips),
            'dns_server': random.choice(self.dns_servers),
            'query_type': random.choice(self.query_types),
            'is_suspicious': True,
            'anomaly_type': anomaly_type
        }

        if anomaly_type == 'malicious_domain':
            log['query'] = random.choice(self.suspicious_domains)
            log['response_code'] = 'NOERROR'
            log['response_time_ms'] = random.randint(100, 500)

        elif anomaly_type == 'dns_tunneling':
            # Long subdomain typical of DNS tunneling
            subdomain = ''.join(random.choices('abcdef0123456789', k=50))
            log['query'] = f'{subdomain}.tunnel.example.com'
            log['response_code'] = 'NOERROR'
            log['response_time_ms'] = random.randint(200, 600)
            log['query_type'] = 'TXT'

        elif anomaly_type == 'dga_domain':
            # Domain Generation Algorithm pattern
            dga_domain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=12)) + '.com'
            log['query'] = dga_domain
            log['response_code'] = 'NXDOMAIN'
            log['response_time_ms'] = random.randint(10, 100)

        else:  # high_frequency
            log['query'] = random.choice(self.normal_domains)
            log['response_code'] = 'NOERROR'
            log['response_time_ms'] = random.randint(5, 50)

        return log

    def generate_logs(self, count: int = 1000, suspicious_ratio: float = 0.05) -> List[Dict]:
        """Generate a mix of normal and suspicious logs"""
        logs = []
        suspicious_count = int(count * suspicious_ratio)
        normal_count = count - suspicious_count

        # Generate normal logs
        for _ in range(normal_count):
            logs.append(self.generate_normal_log())

        # Generate suspicious logs
        for _ in range(suspicious_count):
            logs.append(self.generate_suspicious_log())

        # Sort by timestamp
        logs.sort(key=lambda x: x['timestamp'])

        return logs

    def save_logs(self, logs: List[Dict], output_file: str, format: str = 'json'):
        """Save logs to file"""
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(logs, f, indent=2)

        elif format == 'csv':
            import csv
            if logs:
                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)

        elif format == 'syslog':
            with open(output_file, 'w') as f:
                for log in logs:
                    syslog_entry = (
                        f"{log['timestamp']} dns-server: "
                        f"client={log['source_ip']} "
                        f"query={log['query']} "
                        f"type={log['query_type']} "
                        f"response={log['response_code']} "
                        f"time={log['response_time_ms']}ms\n"
                    )
                    f.write(syslog_entry)


if __name__ == '__main__':
    generator = DNSLogGenerator()

    print("Generating DNS logs...")
    logs = generator.generate_logs(count=1000, suspicious_ratio=0.08)

    # Save in multiple formats
    generator.save_logs(logs, '../data/dns_logs.json', format='json')
    generator.save_logs(logs, '../data/dns_logs.csv', format='csv')
    generator.save_logs(logs, '../logs/dns.log', format='syslog')

    print(f"Generated {len(logs)} DNS logs")
    suspicious = sum(1 for log in logs if log.get('is_suspicious', False))
    print(f"Suspicious logs: {suspicious} ({suspicious/len(logs)*100:.2f}%)")
