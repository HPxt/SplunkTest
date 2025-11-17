#!/usr/bin/env python3
"""
Example SPL Queries
Demonstrates various SIEM query capabilities
"""

# Common SPL queries for security analysis

EXAMPLE_QUERIES = {
    "Basic Search": [
        "search http",
        "search ssh",
        "search 192.168.1.1",
        "search failed",
    ],

    "HTTP Security Analysis": [
        "search http | where status_code>400",
        "search http | stats count by status_code",
        "search http | top client_ip",
        "search http | where status_code=500 | fields timestamp, client_ip, path",
    ],

    "SSH Security Analysis": [
        "search ssh | where status=failed",
        "search ssh | stats count by source_ip",
        "search ssh | where status=failed | top user",
        "search ssh | where status=failed | stats count by source_ip",
    ],

    "DNS Analysis": [
        "search dns | top query",
        "search dns | where response_code=NXDOMAIN",
        "search dns | stats count by query_type",
        "search dns | where response_time_ms>100",
    ],

    "FTP Analysis": [
        "search ftp | where status=failed",
        "search ftp | top user",
        "search ftp | stats count by action",
        "search ftp | where action=download",
    ],

    "Threat Hunting": [
        "search is_suspicious=True",
        "search attack_type | stats count by attack_type",
        "search sql_injection",
        "search brute_force",
        "search path_traversal",
    ],

    "Advanced Queries": [
        "search http | where status_code>=400 | top limit=5 client_ip",
        "search ssh | where status=failed | stats count by user | sort -count",
        "search dns | where response_time_ms>50 | fields query, response_time_ms, source_ip",
    ]
}


def print_example_queries():
    """Print all example queries"""
    print("="*70)
    print("SPLUNK SIEM - EXAMPLE SPL QUERIES")
    print("="*70)

    for category, queries in EXAMPLE_QUERIES.items():
        print(f"\n📊 {category}:")
        print("-" * 70)
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")

    print("\n" + "="*70)
    print("Usage:")
    print("  python siem_main.py --query 'YOUR_QUERY_HERE'")
    print("="*70)


if __name__ == '__main__':
    print_example_queries()
