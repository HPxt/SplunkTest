#!/usr/bin/env python3
"""
FTP Log Generator
Generates realistic FTP session and transfer logs
"""

import random
import datetime
import json
from typing import List, Dict

class FTPLogGenerator:
    def __init__(self):
        self.legitimate_users = ['ftp_user', 'backup', 'webmaster', 'uploads']
        self.attacker_users = ['admin', 'root', 'anonymous', 'test', 'ftpuser']

        self.legitimate_ips = [f'192.168.1.{i}' for i in range(10, 50)]
        self.attacker_ips = [
            '45.142.212.61', '89.248.163.158', '103.75.201.2',
            '185.156.73.54', '194.169.175.32'
        ]

        self.normal_files = [
            '/uploads/document.pdf', '/public/image.jpg', '/backup/database.sql',
            '/files/report.xlsx', '/data/export.csv', '/docs/readme.txt',
            '/images/logo.png', '/videos/tutorial.mp4'
        ]

        self.suspicious_files = [
            '/etc/passwd', '/../../../etc/shadow', '/backup/credit_cards.csv',
            '/shell.php', '/cmd.exe', '/backdoor.asp', '/.ssh/id_rsa',
            '/../../windows/system32/config/sam'
        ]

        self.commands = [
            'USER', 'PASS', 'LIST', 'RETR', 'STOR', 'DELE', 'CWD',
            'PWD', 'QUIT', 'TYPE', 'PORT', 'PASV', 'MKD', 'RMD'
        ]

    def generate_login_event(self, is_attack: bool = False) -> Dict:
        """Generate FTP login event"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        if is_attack:
            user = random.choice(self.attacker_users)
            source_ip = random.choice(self.attacker_ips)
            status = random.choice(['failed'] * 9 + ['success'])
        else:
            user = random.choice(self.legitimate_users)
            source_ip = random.choice(self.legitimate_ips)
            status = random.choice(['success'] * 9 + ['failed'])

        return {
            'timestamp': timestamp.isoformat(),
            'event_type': 'login',
            'user': user,
            'source_ip': source_ip,
            'status': status,
            'auth_method': random.choice(['password', 'anonymous']),
            'is_suspicious': is_attack,
            'attack_type': 'brute_force' if (is_attack and status == 'failed') else None
        }

    def generate_transfer_event(self, is_attack: bool = False) -> Dict:
        """Generate FTP file transfer event"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        action = random.choice(['download', 'upload', 'delete'])

        if is_attack:
            file_path = random.choice(self.suspicious_files)
            user = random.choice(self.legitimate_users + self.attacker_users)
            source_ip = random.choice(self.legitimate_ips + self.attacker_ips)

            attack_type = random.choice([
                'data_exfiltration',
                'unauthorized_access',
                'path_traversal',
                'malware_upload'
            ])
        else:
            file_path = random.choice(self.normal_files)
            user = random.choice(self.legitimate_users)
            source_ip = random.choice(self.legitimate_ips)
            attack_type = None

        log = {
            'timestamp': timestamp.isoformat(),
            'event_type': 'transfer',
            'action': action,
            'user': user,
            'source_ip': source_ip,
            'file_path': file_path,
            'file_size': random.randint(1024, 104857600),
            'transfer_time_sec': random.randint(1, 300),
            'status': random.choice(['success'] * 9 + ['failed']),
            'is_suspicious': is_attack,
            'attack_type': attack_type
        }

        if action == 'download':
            log['transfer_rate_kbps'] = random.randint(100, 10000)
        elif action == 'upload':
            log['transfer_rate_kbps'] = random.randint(50, 5000)

        return log

    def generate_command_event(self) -> Dict:
        """Generate FTP command event"""
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )

        command = random.choice(self.commands)
        user = random.choice(self.legitimate_users)

        log = {
            'timestamp': timestamp.isoformat(),
            'event_type': 'command',
            'command': command,
            'user': user,
            'source_ip': random.choice(self.legitimate_ips),
            'response_code': random.choice([200, 220, 226, 230, 250, 331, 425, 426, 500, 550]),
            'is_suspicious': False
        }

        # Add command-specific details
        if command in ['RETR', 'STOR', 'DELE']:
            log['argument'] = random.choice(self.normal_files)
        elif command == 'CWD':
            log['argument'] = random.choice(['/uploads', '/public', '/backup', '/files'])
        elif command == 'USER':
            log['argument'] = user

        return log

    def generate_logs(self, count: int = 1000, attack_ratio: float = 0.08) -> List[Dict]:
        """Generate a mix of FTP logs"""
        logs = []
        attack_count = int(count * attack_ratio)
        normal_count = count - attack_count

        # Distribution: 30% login, 50% transfer, 20% commands
        for _ in range(normal_count):
            event_type = random.choices(
                ['login', 'transfer', 'command'],
                weights=[0.3, 0.5, 0.2]
            )[0]

            if event_type == 'login':
                logs.append(self.generate_login_event(is_attack=False))
            elif event_type == 'transfer':
                logs.append(self.generate_transfer_event(is_attack=False))
            else:
                logs.append(self.generate_command_event())

        # Generate attack logs
        for _ in range(attack_count):
            attack_type = random.choice(['login', 'transfer'])
            if attack_type == 'login':
                logs.append(self.generate_login_event(is_attack=True))
            else:
                logs.append(self.generate_transfer_event(is_attack=True))

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
                all_keys = set()
                for log in logs:
                    all_keys.update(log.keys())

                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    writer.writerows(logs)

        elif format == 'vsftpd':
            with open(output_file, 'w') as f:
                for log in logs:
                    if log['event_type'] == 'login':
                        vsftpd_log = (
                            f"{log['timestamp']} [pid {random.randint(1000, 9999)}] "
                            f"[{log['user']}] {log['status'].upper()} LOGIN. "
                            f"Client \"{log['source_ip']}\"\n"
                        )
                    elif log['event_type'] == 'transfer':
                        vsftpd_log = (
                            f"{log['timestamp']} [pid {random.randint(1000, 9999)}] "
                            f"[{log['user']}] {log['action'].upper()} {log['file_path']} "
                            f"{log['file_size']} bytes\n"
                        )
                    else:
                        vsftpd_log = (
                            f"{log['timestamp']} [pid {random.randint(1000, 9999)}] "
                            f"COMMAND {log['command']}\n"
                        )
                    f.write(vsftpd_log)


if __name__ == '__main__':
    generator = FTPLogGenerator()

    print("Generating FTP logs...")
    logs = generator.generate_logs(count=1000, attack_ratio=0.1)

    generator.save_logs(logs, '../data/ftp_logs.json', format='json')
    generator.save_logs(logs, '../data/ftp_logs.csv', format='csv')
    generator.save_logs(logs, '../logs/vsftpd.log', format='vsftpd')

    print(f"Generated {len(logs)} FTP logs")
    suspicious = sum(1 for log in logs if log.get('is_suspicious', False))
    print(f"Suspicious logs: {suspicious} ({suspicious/len(logs)*100:.2f}%)")
