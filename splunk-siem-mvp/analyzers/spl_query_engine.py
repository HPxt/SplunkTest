#!/usr/bin/env python3
"""
SPL Query Engine
Implements Splunk-like Search Processing Language queries
"""

import re
import json
from collections import Counter, defaultdict
from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta


class SPLQueryEngine:
    """Execute Splunk-style queries on log data"""

    def __init__(self, logs: List[Dict]):
        self.logs = logs
        self.results = logs.copy()

    def search(self, pattern: str) -> 'SPLQueryEngine':
        """Search for pattern in logs (like Splunk's search command)"""
        filtered = []
        pattern_lower = pattern.lower()

        for log in self.results:
            # Search in all string fields
            for value in log.values():
                if isinstance(value, str) and pattern_lower in value.lower():
                    filtered.append(log)
                    break

        self.results = filtered
        return self

    def where(self, condition: str) -> 'SPLQueryEngine':
        """Filter logs based on condition"""
        filtered = []

        # Parse simple conditions like "status_code=200" or "status_code>400"
        match = re.match(r'(\w+)\s*([=<>!]+)\s*(.+)', condition)
        if not match:
            return self

        field, operator, value = match.groups()
        value = value.strip('"\'')

        # Try to convert value to appropriate type
        try:
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        except:
            pass

        for log in self.results:
            if field not in log:
                continue

            log_value = log[field]

            # Perform comparison
            try:
                if operator == '=' or operator == '==':
                    if log_value == value:
                        filtered.append(log)
                elif operator == '!=':
                    if log_value != value:
                        filtered.append(log)
                elif operator == '>':
                    if log_value > value:
                        filtered.append(log)
                elif operator == '<':
                    if log_value < value:
                        filtered.append(log)
                elif operator == '>=':
                    if log_value >= value:
                        filtered.append(log)
                elif operator == '<=':
                    if log_value <= value:
                        filtered.append(log)
            except:
                continue

        self.results = filtered
        return self

    def stats(self, operation: str, field: str = None, by: str = None) -> Dict:
        """Aggregate statistics (like Splunk's stats command)"""
        if operation == 'count':
            if by:
                # Count by field
                counts = Counter(log.get(by) for log in self.results if by in log)
                return {'stats': dict(counts), 'operation': 'count', 'by': by}
            else:
                return {'stats': {'count': len(self.results)}, 'operation': 'count'}

        elif operation == 'sum' and field:
            if by:
                sums = defaultdict(int)
                for log in self.results:
                    if field in log and by in log:
                        try:
                            sums[log[by]] += float(log[field])
                        except:
                            pass
                return {'stats': dict(sums), 'operation': 'sum', 'field': field, 'by': by}
            else:
                total = sum(float(log[field]) for log in self.results if field in log)
                return {'stats': {'sum': total}, 'operation': 'sum', 'field': field}

        elif operation == 'avg' and field:
            values = [float(log[field]) for log in self.results if field in log]
            if values:
                avg = sum(values) / len(values)
                return {'stats': {'avg': avg}, 'operation': 'avg', 'field': field}

        elif operation == 'max' and field:
            values = [float(log[field]) for log in self.results if field in log]
            if values:
                return {'stats': {'max': max(values)}, 'operation': 'max', 'field': field}

        elif operation == 'min' and field:
            values = [float(log[field]) for log in self.results if field in log]
            if values:
                return {'stats': {'min': min(values)}, 'operation': 'min', 'field': field}

        return {'stats': {}, 'operation': operation}

    def top(self, field: str, limit: int = 10) -> List[Dict]:
        """Get top values for a field (like Splunk's top command)"""
        if not field:
            return []

        counts = Counter(log.get(field) for log in self.results if field in log)
        top_items = counts.most_common(limit)

        return [
            {'value': value, 'count': count, 'percent': (count / len(self.results)) * 100}
            for value, count in top_items
        ]

    def rare(self, field: str, limit: int = 10) -> List[Dict]:
        """Get rare values for a field (like Splunk's rare command)"""
        if not field:
            return []

        counts = Counter(log.get(field) for log in self.results if field in log)
        rare_items = counts.most_common()[-limit:]

        return [
            {'value': value, 'count': count, 'percent': (count / len(self.results)) * 100}
            for value, count in rare_items
        ]

    def fields(self, *field_names: str) -> 'SPLQueryEngine':
        """Select specific fields (like Splunk's fields command)"""
        filtered_results = []
        for log in self.results:
            filtered_log = {field: log.get(field) for field in field_names if field in log}
            if filtered_log:
                filtered_results.append(filtered_log)

        self.results = filtered_results
        return self

    def head(self, limit: int = 10) -> 'SPLQueryEngine':
        """Return first N results (like Splunk's head command)"""
        self.results = self.results[:limit]
        return self

    def tail(self, limit: int = 10) -> 'SPLQueryEngine':
        """Return last N results (like Splunk's tail command)"""
        self.results = self.results[-limit:]
        return self

    def sort(self, field: str, reverse: bool = False) -> 'SPLQueryEngine':
        """Sort results by field (like Splunk's sort command)"""
        self.results.sort(key=lambda x: x.get(field, ''), reverse=reverse)
        return self

    def dedup(self, field: str) -> 'SPLQueryEngine':
        """Remove duplicate values (like Splunk's dedup command)"""
        seen = set()
        deduped = []

        for log in self.results:
            value = log.get(field)
            if value not in seen:
                seen.add(value)
                deduped.append(log)

        self.results = deduped
        return self

    def timechart(self, field: str, span: str = '1h') -> Dict:
        """Create time-based chart (like Splunk's timechart command)"""
        # Simplified implementation
        time_buckets = defaultdict(list)

        for log in self.results:
            if 'timestamp' in log:
                try:
                    ts = datetime.fromisoformat(log['timestamp'])
                    # Round to hour for simplicity
                    bucket = ts.replace(minute=0, second=0, microsecond=0)
                    if field in log:
                        time_buckets[bucket.isoformat()].append(log[field])
                except:
                    pass

        return {
            'timechart': {
                bucket: len(values) for bucket, values in time_buckets.items()
            },
            'field': field,
            'span': span
        }

    def get_results(self) -> List[Dict]:
        """Get current results"""
        return self.results

    def count(self) -> int:
        """Get count of current results"""
        return len(self.results)


class SPLParser:
    """Parse and execute SPL queries"""

    def __init__(self, logs: List[Dict]):
        self.logs = logs

    def execute(self, query: str) -> Any:
        """Execute a full SPL query string"""
        print(f"Executing SPL query: {query}")

        engine = SPLQueryEngine(self.logs)

        # Split query into commands (separated by |)
        commands = [cmd.strip() for cmd in query.split('|')]

        for cmd in commands:
            parts = cmd.split(None, 1)
            if not parts:
                continue

            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''

            try:
                if command == 'search':
                    engine.search(args)

                elif command == 'where':
                    engine.where(args)

                elif command == 'stats':
                    # Parse stats command: stats count by field
                    match = re.match(r'(\w+)(?:\s+(\w+))?(?:\s+by\s+(\w+))?', args)
                    if match:
                        operation, field, by_field = match.groups()
                        return engine.stats(operation, field, by_field)

                elif command == 'top':
                    # Parse: top limit=10 field
                    limit = 10
                    field = args
                    if 'limit=' in args:
                        parts = args.split()
                        for part in parts:
                            if part.startswith('limit='):
                                limit = int(part.split('=')[1])
                            else:
                                field = part
                    return engine.top(field, limit)

                elif command == 'rare':
                    limit = 10
                    field = args
                    if 'limit=' in args:
                        parts = args.split()
                        for part in parts:
                            if part.startswith('limit='):
                                limit = int(part.split('=')[1])
                            else:
                                field = part
                    return engine.rare(field, limit)

                elif command == 'fields':
                    fields = [f.strip() for f in args.split(',')]
                    engine.fields(*fields)

                elif command == 'head':
                    limit = int(args) if args else 10
                    engine.head(limit)

                elif command == 'tail':
                    limit = int(args) if args else 10
                    engine.tail(limit)

                elif command == 'sort':
                    # Parse: sort -field or sort field
                    reverse = args.startswith('-')
                    field = args[1:] if reverse else args
                    engine.sort(field.strip(), reverse)

                elif command == 'dedup':
                    engine.dedup(args)

                elif command == 'timechart':
                    # Simplified: timechart count by field
                    return engine.timechart(args)

            except Exception as e:
                print(f"Error executing command '{command}': {e}")

        return engine.get_results()


def demo():
    """Demo SPL queries"""
    # Sample logs
    sample_logs = [
        {'log_type': 'http', 'status_code': 200, 'client_ip': '192.168.1.1', 'path': '/index.html'},
        {'log_type': 'http', 'status_code': 404, 'client_ip': '192.168.1.2', 'path': '/missing'},
        {'log_type': 'http', 'status_code': 200, 'client_ip': '192.168.1.1', 'path': '/about'},
        {'log_type': 'ssh', 'status': 'failed', 'user': 'admin', 'source_ip': '10.0.0.1'},
        {'log_type': 'ssh', 'status': 'success', 'user': 'john', 'source_ip': '192.168.1.5'},
    ]

    parser = SPLParser(sample_logs)

    print("=" * 60)
    print("SPL Query Engine Demo")
    print("=" * 60)

    # Example queries
    queries = [
        'search http | stats count by status_code',
        'search ssh | where status=failed',
        'stats count by log_type',
        'search http | top client_ip',
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = parser.execute(query)
        print(f"Result: {json.dumps(result, indent=2)}")


if __name__ == '__main__':
    demo()
