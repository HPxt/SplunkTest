#!/usr/bin/env python3
"""
Universal Log Parser
Parses and extracts fields from various log formats
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class LogParser:
    """Universal log parser with field extraction"""

    def __init__(self):
        # Regex patterns for different log formats
        self.patterns = {
            'apache': re.compile(
                r'(?P<client_ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
                r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
                r'(?P<status_code>\d+) (?P<response_size>\S+) '
                r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
            ),

            'dns': re.compile(
                r'(?P<timestamp>[\d\-T:\.]+) dns-server: '
                r'client=(?P<source_ip>\S+) '
                r'query=(?P<query>\S+) '
                r'type=(?P<query_type>\S+) '
                r'response=(?P<response_code>\S+) '
                r'time=(?P<response_time>\d+)ms'
            ),

            'ssh': re.compile(
                r'(?P<timestamp>[\d\-T:\.]+) sshd\[(?P<pid>\d+)\]: '
                r'(?P<status>\S+) (?P<auth_method>\S+) for (?P<user>\S+) '
                r'from (?P<source_ip>\S+) port (?P<source_port>\d+)'
            ),

            'ftp': re.compile(
                r'(?P<timestamp>[\d\-T:\.]+) \[pid (?P<pid>\d+)\] '
                r'\[(?P<user>\S+)\] (?P<action>\S+) '
                r'(?P<details>.*)'
            ),
        }

    def identify_log_type(self, log_line: str) -> Optional[str]:
        """Identify the type of log from a line"""
        for log_type, pattern in self.patterns.items():
            if pattern.search(log_line):
                return log_type
        return None

    def parse_apache_log(self, log_line: str) -> Optional[Dict]:
        """Parse Apache/HTTP access log"""
        match = self.patterns['apache'].match(log_line)
        if not match:
            return None

        data = match.groupdict()
        return {
            'log_type': 'http',
            'timestamp': data['timestamp'],
            'client_ip': data['client_ip'],
            'method': data['method'],
            'path': data['path'],
            'protocol': data['protocol'],
            'status_code': int(data['status_code']),
            'response_size': int(data['response_size']) if data['response_size'].isdigit() else 0,
            'referer': data['referer'],
            'user_agent': data['user_agent'],
            'raw': log_line
        }

    def parse_dns_log(self, log_line: str) -> Optional[Dict]:
        """Parse DNS log"""
        match = self.patterns['dns'].search(log_line)
        if not match:
            return None

        data = match.groupdict()
        return {
            'log_type': 'dns',
            'timestamp': data['timestamp'],
            'source_ip': data['source_ip'],
            'query': data['query'],
            'query_type': data['query_type'],
            'response_code': data['response_code'],
            'response_time_ms': int(data['response_time']),
            'raw': log_line
        }

    def parse_ssh_log(self, log_line: str) -> Optional[Dict]:
        """Parse SSH authentication log"""
        match = self.patterns['ssh'].search(log_line)
        if not match:
            return None

        data = match.groupdict()
        return {
            'log_type': 'ssh',
            'timestamp': data['timestamp'],
            'pid': int(data['pid']),
            'status': data['status'].lower(),
            'auth_method': data['auth_method'],
            'user': data['user'],
            'source_ip': data['source_ip'],
            'source_port': int(data['source_port']),
            'raw': log_line
        }

    def parse_ftp_log(self, log_line: str) -> Optional[Dict]:
        """Parse FTP log"""
        match = self.patterns['ftp'].search(log_line)
        if not match:
            return None

        data = match.groupdict()
        return {
            'log_type': 'ftp',
            'timestamp': data['timestamp'],
            'pid': int(data['pid']),
            'user': data['user'],
            'action': data['action'].lower(),
            'details': data['details'],
            'raw': log_line
        }

    def parse_line(self, log_line: str) -> Optional[Dict]:
        """Parse a single log line automatically detecting type"""
        log_line = log_line.strip()
        if not log_line:
            return None

        log_type = self.identify_log_type(log_line)

        if log_type == 'apache':
            return self.parse_apache_log(log_line)
        elif log_type == 'dns':
            return self.parse_dns_log(log_line)
        elif log_type == 'ssh':
            return self.parse_ssh_log(log_line)
        elif log_type == 'ftp':
            return self.parse_ftp_log(log_line)

        return None

    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse an entire log file"""
        parsed_logs = []

        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    parsed = self.parse_line(line)
                    if parsed:
                        parsed['line_number'] = line_num
                        parsed_logs.append(parsed)
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")

        return parsed_logs

    def extract_fields(self, parsed_logs: List[Dict], fields: List[str]) -> List[Dict]:
        """Extract specific fields from parsed logs"""
        extracted = []
        for log in parsed_logs:
            entry = {field: log.get(field) for field in fields if field in log}
            if entry:
                extracted.append(entry)
        return extracted

    def filter_logs(self, parsed_logs: List[Dict], **criteria) -> List[Dict]:
        """Filter logs based on criteria"""
        filtered = []
        for log in parsed_logs:
            match = True
            for key, value in criteria.items():
                if key not in log or log[key] != value:
                    match = False
                    break
            if match:
                filtered.append(log)
        return filtered

    def aggregate_by_field(self, parsed_logs: List[Dict], field: str) -> Dict:
        """Aggregate logs by a specific field"""
        aggregation = {}
        for log in parsed_logs:
            if field in log:
                key = log[field]
                if key not in aggregation:
                    aggregation[key] = []
                aggregation[key].append(log)
        return aggregation

    def count_by_field(self, parsed_logs: List[Dict], field: str) -> Dict:
        """Count occurrences by field"""
        counts = {}
        for log in parsed_logs:
            if field in log:
                key = log[field]
                counts[key] = counts.get(key, 0) + 1
        return counts


class JSONLogParser:
    """Parser for JSON-formatted logs"""

    @staticmethod
    def parse_file(file_path: str) -> List[Dict]:
        """Parse JSON log file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
        except Exception as e:
            print(f"Error parsing JSON file {file_path}: {e}")
        return []

    @staticmethod
    def parse_jsonl(file_path: str) -> List[Dict]:
        """Parse JSON Lines format (one JSON object per line)"""
        logs = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            print(f"Error parsing JSONL file {file_path}: {e}")
        return logs


def demo():
    """Demonstration of log parsing capabilities"""
    parser = LogParser()

    print("=" * 60)
    print("Log Parser Demo")
    print("=" * 60)

    # Example logs
    test_logs = [
        '192.168.1.100 - - [2025-01-15T10:30:45] "GET /index.html HTTP/1.1" 200 1234 "https://google.com" "Mozilla/5.0"',
        '2025-01-15T10:31:00 dns-server: client=192.168.1.50 query=example.com type=A response=NOERROR time=25ms',
        '2025-01-15T10:32:15 sshd[1234]: SUCCESS publickey for admin from 192.168.1.25 port 54321',
    ]

    for log in test_logs:
        parsed = parser.parse_line(log)
        if parsed:
            print(f"\nLog Type: {parsed['log_type']}")
            print(f"Parsed: {json.dumps(parsed, indent=2)}")


if __name__ == '__main__':
    demo()
