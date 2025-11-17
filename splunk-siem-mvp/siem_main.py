#!/usr/bin/env python3
"""
Splunk SIEM MVP - Main Application
Integrates all components: log generation, parsing, analysis, and visualization
"""

import sys
import json
import argparse
from pathlib import Path

# Add subdirectories to path
sys.path.insert(0, str(Path(__file__).parent / 'generators'))
sys.path.insert(0, str(Path(__file__).parent / 'parsers'))
sys.path.insert(0, str(Path(__file__).parent / 'analyzers'))
sys.path.insert(0, str(Path(__file__).parent / 'dashboard'))

from dns_log_generator import DNSLogGenerator
from http_log_generator import HTTPLogGenerator
from ssh_log_generator import SSHLogGenerator
from ftp_log_generator import FTPLogGenerator
from log_parser import LogParser, JSONLogParser
from anomaly_detector import AnomalyDetector
from spl_query_engine import SPLParser
from generate_dashboard import DashboardGenerator


class SplunkSIEM:
    """Main SIEM application class"""

    def __init__(self, data_dir='data', logs_dir='logs', reports_dir='reports'):
        self.data_dir = Path(data_dir)
        self.logs_dir = Path(logs_dir)
        self.reports_dir = Path(reports_dir)

        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        self.all_logs = {}
        self.alerts = {}

    def generate_logs(self, count=1000):
        """Generate all types of logs"""
        print("\n" + "="*70)
        print("STEP 1: GENERATING LOGS")
        print("="*70)

        # DNS Logs
        print("\n[1/4] Generating DNS logs...")
        dns_gen = DNSLogGenerator()
        dns_logs = dns_gen.generate_logs(count=count, suspicious_ratio=0.08)
        dns_gen.save_logs(dns_logs, str(self.data_dir / 'dns_logs.json'), format='json')
        dns_gen.save_logs(dns_logs, str(self.logs_dir / 'dns.log'), format='syslog')
        self.all_logs['dns'] = dns_logs
        print(f"  ✓ Generated {len(dns_logs)} DNS logs")

        # HTTP Logs
        print("[2/4] Generating HTTP logs...")
        http_gen = HTTPLogGenerator()
        http_logs = http_gen.generate_logs(count=count, attack_ratio=0.12)
        http_gen.save_logs(http_logs, str(self.data_dir / 'http_logs.json'), format='json')
        http_gen.save_logs(http_logs, str(self.logs_dir / 'apache_access.log'), format='apache')
        self.all_logs['http'] = http_logs
        print(f"  ✓ Generated {len(http_logs)} HTTP logs")

        # SSH Logs
        print("[3/4] Generating SSH logs...")
        ssh_gen = SSHLogGenerator()
        ssh_logs = ssh_gen.generate_logs(count=count)
        ssh_gen.save_logs(ssh_logs, str(self.data_dir / 'ssh_logs.json'), format='json')
        ssh_gen.save_logs(ssh_logs, str(self.logs_dir / 'auth.log'), format='syslog')
        self.all_logs['ssh'] = ssh_logs
        print(f"  ✓ Generated {len(ssh_logs)} SSH logs")

        # FTP Logs
        print("[4/4] Generating FTP logs...")
        ftp_gen = FTPLogGenerator()
        ftp_logs = ftp_gen.generate_logs(count=count, attack_ratio=0.1)
        ftp_gen.save_logs(ftp_logs, str(self.data_dir / 'ftp_logs.json'), format='json')
        ftp_gen.save_logs(ftp_logs, str(self.logs_dir / 'vsftpd.log'), format='vsftpd')
        self.all_logs['ftp'] = ftp_logs
        print(f"  ✓ Generated {len(ftp_logs)} FTP logs")

        total = sum(len(logs) for logs in self.all_logs.values())
        print(f"\n✅ Total logs generated: {total:,}")

    def run_analysis(self):
        """Run anomaly detection on all logs"""
        print("\n" + "="*70)
        print("STEP 2: RUNNING SECURITY ANALYSIS")
        print("="*70 + "\n")

        # Flatten all logs for analysis
        all_logs_list = []
        for log_type, logs in self.all_logs.items():
            for log in logs:
                log['log_type'] = log_type
                all_logs_list.append(log)

        # Run anomaly detection
        detector = AnomalyDetector()
        self.alerts = detector.analyze_all(all_logs_list)

        # Save alerts
        alerts_file = self.reports_dir / 'security_alerts.json'
        detector.save_alerts(self.alerts, str(alerts_file))

        print(f"\n✅ Analysis complete. Total alerts: {self.alerts['total_alerts']}")
        print(f"📊 Severity breakdown: {self.alerts['severity_breakdown']}")
        print(f"💾 Alerts saved to: {alerts_file}")

        return self.alerts

    def generate_dashboard(self):
        """Generate HTML dashboard"""
        print("\n" + "="*70)
        print("STEP 3: GENERATING DASHBOARD")
        print("="*70 + "\n")

        dashboard_file = self.reports_dir / 'dashboard.html'

        generator = DashboardGenerator(self.all_logs, self.alerts)
        generator.generate_html(str(dashboard_file))

        print(f"✅ Dashboard generated: {dashboard_file}")
        print(f"🌐 Open in browser: file://{dashboard_file.absolute()}")

    def run_spl_query(self, query: str):
        """Execute SPL query"""
        print("\n" + "="*70)
        print(f"EXECUTING SPL QUERY: {query}")
        print("="*70 + "\n")

        # Flatten logs
        all_logs_list = []
        for log_type, logs in self.all_logs.items():
            for log in logs:
                log['log_type'] = log_type
                all_logs_list.append(log)

        parser = SPLParser(all_logs_list)
        results = parser.execute(query)

        print(f"\nResults ({len(results) if isinstance(results, list) else 'N/A'} records):")
        print(json.dumps(results, indent=2))

        return results

    def show_summary(self):
        """Show complete summary"""
        print("\n" + "="*70)
        print("SPLUNK SIEM MVP - SUMMARY")
        print("="*70)

        total_logs = sum(len(logs) for logs in self.all_logs.values())
        total_alerts = self.alerts.get('total_alerts', 0)

        print(f"\n📊 STATISTICS:")
        print(f"  Total Logs Processed: {total_logs:,}")
        print(f"  Security Alerts: {total_alerts}")

        if self.alerts.get('severity_breakdown'):
            print(f"\n⚠️  SEVERITY BREAKDOWN:")
            for severity, count in self.alerts['severity_breakdown'].items():
                print(f"  {severity.upper()}: {count}")

        if self.alerts.get('alert_types'):
            print(f"\n🎯 TOP THREAT TYPES:")
            for threat_type, count in list(self.alerts['alert_types'].most_common(5)):
                print(f"  {threat_type.replace('_', ' ').title()}: {count}")

        print(f"\n📁 OUTPUT FILES:")
        print(f"  Data: {self.data_dir}/")
        print(f"  Logs: {self.logs_dir}/")
        print(f"  Reports: {self.reports_dir}/")
        print(f"  Dashboard: {self.reports_dir}/dashboard.html")

        print("\n" + "="*70)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='Splunk SIEM MVP - Security Information and Event Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete analysis pipeline
  python siem_main.py --full

  # Generate only logs
  python siem_main.py --generate-logs --count 5000

  # Run analysis on existing data
  python siem_main.py --analyze

  # Execute SPL query
  python siem_main.py --query "search http | stats count by status_code"

  # Generate dashboard only
  python siem_main.py --dashboard
        """
    )

    parser.add_argument('--full', action='store_true',
                        help='Run complete pipeline (generate, analyze, dashboard)')
    parser.add_argument('--generate-logs', action='store_true',
                        help='Generate log files')
    parser.add_argument('--analyze', action='store_true',
                        help='Run security analysis')
    parser.add_argument('--dashboard', action='store_true',
                        help='Generate HTML dashboard')
    parser.add_argument('--query', type=str,
                        help='Execute SPL query')
    parser.add_argument('--count', type=int, default=1000,
                        help='Number of logs to generate per type (default: 1000)')

    args = parser.parse_args()

    # Initialize SIEM
    siem = SplunkSIEM()

    print("""
    ███████╗██████╗ ██╗     ██╗   ██╗███╗   ██╗██╗  ██╗
    ██╔════╝██╔══██╗██║     ██║   ██║████╗  ██║██║ ██╔╝
    ███████╗██████╔╝██║     ██║   ██║██╔██╗ ██║█████╔╝
    ╚════██║██╔═══╝ ██║     ██║   ██║██║╚██╗██║██╔═██╗
    ███████║██║     ███████╗╚██████╔╝██║ ╚████║██║  ██╗
    ╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝

           Security Information and Event Management
                        MVP Version 1.0
    """)

    # Run based on arguments
    if args.full:
        siem.generate_logs(count=args.count)
        siem.run_analysis()
        siem.generate_dashboard()
        siem.show_summary()

    elif args.generate_logs:
        siem.generate_logs(count=args.count)

    elif args.analyze:
        # Load existing data
        print("Loading existing log data...")
        for log_type in ['dns', 'http', 'ssh', 'ftp']:
            json_file = Path('data') / f'{log_type}_logs.json'
            if json_file.exists():
                with open(json_file) as f:
                    siem.all_logs[log_type] = json.load(f)
                print(f"  Loaded {len(siem.all_logs[log_type])} {log_type} logs")

        siem.run_analysis()

    elif args.dashboard:
        # Load data and alerts
        print("Loading data for dashboard...")
        for log_type in ['dns', 'http', 'ssh', 'ftp']:
            json_file = Path('data') / f'{log_type}_logs.json'
            if json_file.exists():
                with open(json_file) as f:
                    siem.all_logs[log_type] = json.load(f)

        alerts_file = Path('reports') / 'security_alerts.json'
        if alerts_file.exists():
            with open(alerts_file) as f:
                siem.alerts = json.load(f)

        siem.generate_dashboard()

    elif args.query:
        # Load existing data
        for log_type in ['dns', 'http', 'ssh', 'ftp']:
            json_file = Path('data') / f'{log_type}_logs.json'
            if json_file.exists():
                with open(json_file) as f:
                    siem.all_logs[log_type] = json.load(f)

        siem.run_spl_query(args.query)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
