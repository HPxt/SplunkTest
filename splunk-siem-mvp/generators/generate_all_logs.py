#!/usr/bin/env python3
"""
Master Log Generator
Generates all types of logs at once
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dns_log_generator import DNSLogGenerator
from http_log_generator import HTTPLogGenerator
from ssh_log_generator import SSHLogGenerator
from ftp_log_generator import FTPLogGenerator


def generate_all_logs(log_count: int = 1000):
    """Generate all types of logs"""

    print("=" * 60)
    print("SPLUNK SIEM MVP - Log Generator")
    print("=" * 60)
    print()

    # DNS Logs
    print("[1/4] Generating DNS logs...")
    dns_gen = DNSLogGenerator()
    dns_logs = dns_gen.generate_logs(count=log_count, suspicious_ratio=0.08)
    dns_gen.save_logs(dns_logs, '../data/dns_logs.json', format='json')
    dns_gen.save_logs(dns_logs, '../data/dns_logs.csv', format='csv')
    dns_gen.save_logs(dns_logs, '../logs/dns.log', format='syslog')

    dns_suspicious = sum(1 for log in dns_logs if log.get('is_suspicious', False))
    print(f"  ✓ Generated {len(dns_logs)} DNS logs ({dns_suspicious} suspicious)")

    # HTTP Logs
    print("\n[2/4] Generating HTTP logs...")
    http_gen = HTTPLogGenerator()
    http_logs = http_gen.generate_logs(count=log_count, attack_ratio=0.12)
    http_gen.save_logs(http_logs, '../data/http_logs.json', format='json')
    http_gen.save_logs(http_logs, '../data/http_logs.csv', format='csv')
    http_gen.save_logs(http_logs, '../logs/apache_access.log', format='apache')

    http_attacks = sum(1 for log in http_logs if log.get('is_suspicious', False))
    print(f"  ✓ Generated {len(http_logs)} HTTP logs ({http_attacks} attacks)")

    # SSH Logs
    print("\n[3/4] Generating SSH logs...")
    ssh_gen = SSHLogGenerator()
    ssh_logs = ssh_gen.generate_logs(count=log_count)
    ssh_gen.save_logs(ssh_logs, '../data/ssh_logs.json', format='json')
    ssh_gen.save_logs(ssh_logs, '../data/ssh_logs.csv', format='csv')
    ssh_gen.save_logs(ssh_logs, '../logs/auth.log', format='syslog')

    ssh_suspicious = sum(1 for log in ssh_logs if log.get('is_suspicious', False))
    print(f"  ✓ Generated {len(ssh_logs)} SSH logs ({ssh_suspicious} suspicious)")

    # FTP Logs
    print("\n[4/4] Generating FTP logs...")
    ftp_gen = FTPLogGenerator()
    ftp_logs = ftp_gen.generate_logs(count=log_count, attack_ratio=0.1)
    ftp_gen.save_logs(ftp_logs, '../data/ftp_logs.json', format='json')
    ftp_gen.save_logs(ftp_logs, '../data/ftp_logs.csv', format='csv')
    ftp_gen.save_logs(ftp_logs, '../logs/vsftpd.log', format='vsftpd')

    ftp_suspicious = sum(1 for log in ftp_logs if log.get('is_suspicious', False))
    print(f"  ✓ Generated {len(ftp_logs)} FTP logs ({ftp_suspicious} suspicious)")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_logs = len(dns_logs) + len(http_logs) + len(ssh_logs) + len(ftp_logs)
    total_suspicious = dns_suspicious + http_attacks + ssh_suspicious + ftp_suspicious

    print(f"Total logs generated: {total_logs}")
    print(f"Total suspicious/attack logs: {total_suspicious} ({total_suspicious/total_logs*100:.2f}%)")
    print()
    print("Output locations:")
    print("  - JSON data: ../data/")
    print("  - CSV data: ../data/")
    print("  - Raw logs: ../logs/")
    print("=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate logs for SIEM analysis')
    parser.add_argument('--count', type=int, default=1000,
                        help='Number of logs to generate per type (default: 1000)')

    args = parser.parse_args()
    generate_all_logs(log_count=args.count)
