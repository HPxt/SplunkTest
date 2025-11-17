# Splunk SIEM MVP - Use Cases

## Security Use Cases

### 1. Detecting SQL Injection Attacks

**Scenario**: Identify potential SQL injection attempts in HTTP logs

**Query**:
```
search http | where path contains "OR" OR path contains "UNION" OR path contains "DROP"
```

**Detection Method**:
- Pattern matching in request paths
- Looking for SQL keywords in URLs
- Status code analysis (500 errors often indicate SQL errors)

**Response Actions**:
1. Block offending IP addresses
2. Review application input validation
3. Update WAF rules
4. Investigate if any queries succeeded

---

### 2. SSH Brute Force Detection

**Scenario**: Detect brute force attacks against SSH service

**Query**:
```
search ssh | where status=failed | stats count by source_ip | where count>5
```

**Detection Method**:
- Count failed login attempts per IP
- Threshold-based alerting (>5 failures)
- Time window analysis

**Response Actions**:
1. Block attacking IPs via firewall
2. Implement fail2ban
3. Enable two-factor authentication
4. Review user accounts targeted

---

### 3. DNS Tunneling Detection

**Scenario**: Identify potential DNS tunneling for data exfiltration

**Query**:
```
search dns | where response_time_ms>100 | top query
```

**Detection Method**:
- Unusually long domain names
- High query frequency to single domain
- TXT record queries with large payloads
- Entropy analysis of domain names

**Response Actions**:
1. Investigate queried domains
2. Check for malware on source systems
3. Block suspicious domains
4. Monitor for C2 communications

---

### 4. Web Scanner Detection

**Scenario**: Detect automated security scanners

**Query**:
```
search http | where user_agent contains "sqlmap" OR user_agent contains "nikto"
```

**Detection Method**:
- Known scanner user agents
- Rapid sequential requests
- 404 errors for common vulnerability paths
- Pattern of requests to admin/config files

**Response Actions**:
1. Block scanner IPs
2. Review what was scanned
3. Patch identified vulnerabilities
4. Enhance rate limiting

---

### 5. Unauthorized File Access (FTP)

**Scenario**: Detect attempts to access sensitive files

**Query**:
```
search ftp | where file_path contains "passwd" OR file_path contains "shadow"
```

**Detection Method**:
- Monitor access to sensitive paths (/etc/, .ssh/)
- Unusual file transfers
- Access outside business hours
- Large file downloads

**Response Actions**:
1. Investigate user account
2. Review file permissions
3. Check for data exfiltration
4. Strengthen access controls

---

### 6. Failed Login Correlation

**Scenario**: Identify coordinated attacks across multiple services

**Query**:
```
search status=failed OR status_code=401 | stats count by source_ip
```

**Detection Method**:
- Failed logins across SSH, FTP, HTTP
- Same source IP attacking multiple services
- Distributed attacks from multiple IPs

**Response Actions**:
1. Implement network-wide IP blocking
2. Review authentication mechanisms
3. Consider implementing SSO
4. Enable account lockout policies

---

### 7. Anomalous DNS Activity

**Scenario**: Detect DGA (Domain Generation Algorithm) domains

**Query**:
```
search dns | where response_code=NXDOMAIN | stats count by query
```

**Detection Method**:
- High NXDOMAIN response rates
- Random-looking domain names
- Consonant clusters in domains
- Newly registered domains

**Response Actions**:
1. Check for malware infections
2. Analyze communication patterns
3. Block malicious domains
4. Investigate source systems

---

### 8. HTTP Path Traversal

**Scenario**: Detect directory traversal attempts

**Query**:
```
search http | where path contains "../" OR path contains "..\"
```

**Detection Method**:
- Presence of ../ or ..\ in paths
- Access attempts to /etc/, /windows/
- Multiple traversal attempts from same IP

**Response Actions**:
1. Block attacking IPs
2. Verify application input filtering
3. Review file permissions
4. Check for successful exploits

---

### 9. Command Injection Detection

**Scenario**: Identify command injection attempts

**Query**:
```
search http | where path contains ";" OR path contains "|" OR path contains "`"
```

**Detection Method**:
- Shell metacharacters in input
- Common command patterns (cat, wget, nc)
- Unusual parameter values
- Application error responses

**Response Actions**:
1. Block malicious IPs
2. Fix vulnerable code
3. Implement input sanitization
4. Review application logs

---

### 10. High-Risk User Activity

**Scenario**: Monitor privileged account usage

**Query**:
```
search user=root OR user=admin | fields timestamp, log_type, status, source_ip
```

**Detection Method**:
- Root/admin account activity
- Privileged operations
- Access from unusual locations
- After-hours activity

**Response Actions**:
1. Verify legitimacy of actions
2. Review privileged access policies
3. Implement session recording
4. Enhance audit logging

---

## Compliance Use Cases

### PCI DSS Compliance
- Monitor access to cardholder data
- Track authentication failures
- Log administrative access
- Monitor network security controls

### HIPAA Compliance
- Audit access to patient records
- Monitor data transfers
- Track user authentication
- Detect unauthorized access

### GDPR Compliance
- Monitor personal data access
- Track data exports
- Audit user consent
- Detect data breaches

---

## Performance Monitoring

### High Response Times
```
search http | where response_time_ms>1000 | stats avg(response_time_ms) by path
```

### Error Rate Analysis
```
search http | where status_code>=500 | stats count by status_code
```

### Traffic Patterns
```
search http | timechart count by status_code
```

---

## Incident Response Workflow

1. **Detection**: Automated alerts trigger on suspicious patterns
2. **Investigation**: Use SPL queries to gather context
3. **Containment**: Block IPs, disable accounts as needed
4. **Eradication**: Remove malware, patch vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Update detection rules, improve defenses

---

## Best Practices

1. **Regular Review**: Check alerts daily
2. **Tuning**: Adjust thresholds to reduce false positives
3. **Correlation**: Look for patterns across multiple log sources
4. **Automation**: Script common response actions
5. **Documentation**: Maintain runbooks for common scenarios
6. **Training**: Ensure team knows how to use SIEM effectively
7. **Testing**: Regularly test detection capabilities

---

## Integration with Other Tools

- **Firewall**: Automatic IP blocking
- **IDS/IPS**: Correlated alerts
- **Ticketing**: Auto-create incidents
- **SOAR**: Automated response playbooks
- **Threat Intel**: Enrich with IoC data
