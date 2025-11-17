# Splunk SIEM MVP - Security Information and Event Management

![SIEM](https://img.shields.io/badge/SIEM-Security-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Um **MVP (Minimum Viable Product)** funcional de SIEM (Security Information and Event Management) inspirado no Splunk, construído em Python puro. Este projeto simula análise de logs de segurança, detecção de anomalias e visualização de ameaças.

## 🎯 Características

- **Geradores de Logs**: Simulação realista de logs DNS, HTTP, SSH e FTP com padrões normais e maliciosos
- **Parser Universal**: Extração automática de campos de múltiplos formatos de log
- **Detecção de Anomalias**: Identificação de ataques como SQL Injection, XSS, Brute Force, DNS Tunneling
- **SPL Query Engine**: Linguagem de consulta estilo Splunk (Search Processing Language)
- **Dashboard Interativo**: Visualização HTML com gráficos e métricas em tempo real
- **Alertas de Segurança**: Sistema de alertas com classificação por severidade

## 📁 Estrutura do Projeto

```
splunk-siem-mvp/
├── generators/          # Geradores de logs simulados
│   ├── dns_log_generator.py
│   ├── http_log_generator.py
│   ├── ssh_log_generator.py
│   ├── ftp_log_generator.py
│   └── generate_all_logs.py
├── parsers/            # Parsers de logs
│   └── log_parser.py
├── analyzers/          # Sistemas de análise
│   ├── anomaly_detector.py
│   └── spl_query_engine.py
├── dashboard/          # Visualização
│   └── generate_dashboard.py
├── examples/           # Exemplos e casos de uso
│   ├── example_queries.py
│   └── use_cases.md
├── data/              # Dados JSON (gerado)
├── logs/              # Logs em formato texto (gerado)
├── reports/           # Relatórios e alertas (gerado)
└── siem_main.py       # Aplicação principal
```

## 🚀 Quick Start

### Instalação

```bash
# Clone o repositório
git clone https://github.com/HPxt/SplunkTest.git
cd SplunkTest/splunk-siem-mvp

# Não há dependências externas! Python 3.8+ puro
python --version  # Verifique que tem Python 3.8+
```

### Uso Básico

#### 1. Pipeline Completo (Recomendado para primeira execução)

```bash
python siem_main.py --full --count 1000
```

Isto irá:
- ✅ Gerar 1000 logs de cada tipo (DNS, HTTP, SSH, FTP)
- ✅ Executar análise de segurança e detecção de anomalias
- ✅ Criar dashboard HTML interativo
- ✅ Gerar relatório de alertas JSON

#### 2. Apenas Gerar Logs

```bash
python siem_main.py --generate-logs --count 5000
```

#### 3. Executar Análise de Segurança

```bash
python siem_main.py --analyze
```

#### 4. Gerar Dashboard

```bash
python siem_main.py --dashboard
```

#### 5. Executar Queries SPL

```bash
# Contar eventos HTTP por status code
python siem_main.py --query "search http | stats count by status_code"

# Top IPs com falhas SSH
python siem_main.py --query "search ssh | where status=failed | top source_ip"

# Detectar ataques SQL Injection
python siem_main.py --query "search http | where path contains 'OR' | fields client_ip, path"
```

## 📊 Dashboard

Após executar com `--full` ou `--dashboard`, abra o dashboard no navegador:

```bash
# O caminho será mostrado no output, algo como:
file:///home/user/SplunkTest/splunk-siem-mvp/reports/dashboard.html
```

### Recursos do Dashboard:
- 📈 Estatísticas gerais de eventos e alertas
- 🚨 Alertas de segurança em tempo real com severidade
- 📊 Distribuição de logs por tipo
- ⚠️ Top tipos de ameaças detectadas
- 📋 Eventos recentes com status

## 🔍 Exemplos de Queries SPL

### Queries Básicas

```spl
# Buscar todos os logs HTTP
search http

# Buscar falhas de autenticação
search failed

# Buscar por IP específico
search 192.168.1.1
```

### Análise de Segurança

```spl
# Detectar ataques de força bruta SSH
search ssh | where status=failed | stats count by source_ip

# Identificar códigos de erro HTTP
search http | where status_code>=400 | top client_ip

# Analisar queries DNS suspeitas
search dns | where response_code=NXDOMAIN | top query

# Buscar tentativas de SQL Injection
search http | where path contains "OR" OR path contains "UNION"
```

### Queries Avançadas

```spl
# Top 5 IPs com mais erros HTTP
search http | where status_code>=400 | top limit=5 client_ip

# Média de tempo de resposta DNS
search dns | stats avg response_time_ms

# Usuários mais atacados via SSH
search ssh | where status=failed | top user
```

## 🛡️ Detecção de Ameaças

### Tipos de Ameaças Detectadas

1. **SQL Injection**: Padrões de injeção SQL em requisições HTTP
2. **XSS (Cross-Site Scripting)**: Scripts maliciosos em parâmetros
3. **Path Traversal**: Tentativas de acesso a arquivos do sistema
4. **Command Injection**: Injeção de comandos do sistema
5. **SSH Brute Force**: Múltiplas tentativas de login SSH falhadas
6. **DNS Tunneling**: Subdomínios suspeitos para exfiltração de dados
7. **DGA Domains**: Domínios gerados algoritmicamente (malware)
8. **Scanner Detection**: Ferramentas de scan (sqlmap, nikto, etc)
9. **FTP Brute Force**: Tentativas de login FTP
10. **Unauthorized Access**: Acesso não autorizado a arquivos sensíveis

### Níveis de Severidade

- 🔴 **CRITICAL**: Ameaças confirmadas de alta prioridade
- 🟠 **HIGH**: Atividade suspeita significativa
- 🟡 **MEDIUM**: Anomalias que requerem investigação
- 🟢 **LOW**: Eventos de baixo risco

## 📚 Casos de Uso

Veja o arquivo [examples/use_cases.md](examples/use_cases.md) para:

- 10+ cenários de segurança detalhados
- Workflows de resposta a incidentes
- Queries para compliance (PCI DSS, HIPAA, GDPR)
- Best practices de monitoramento
- Integração com outras ferramentas

## 🔧 Arquitetura

### 1. Geradores de Logs
Criam logs realistas com:
- Tráfego normal (80-90%)
- Atividade suspeita/maliciosa (10-20%)
- Timestamps realistas
- Múltiplos formatos (JSON, CSV, syslog)

### 2. Parsers
- Detecção automática de formato
- Extração de campos estruturados
- Normalização de dados
- Suporte para múltiplos formatos de log

### 3. Analyzers
**Anomaly Detector**:
- Detecção baseada em regras
- Análise de padrões
- Machine learning básico
- Correlação de eventos

**SPL Query Engine**:
- Sintaxe estilo Splunk
- Comandos: search, where, stats, top, sort, fields
- Agregações e estatísticas
- Pipeline de comandos

### 4. Dashboard
- HTML/CSS puro (sem frameworks)
- Visualizações interativas
- Atualização de métricas
- Exportação de dados

## 🎓 Aprendizado

Este projeto é ideal para:

- ✅ Aprender conceitos de SIEM
- ✅ Entender detecção de ameaças
- ✅ Praticar análise de logs
- ✅ Estudar padrões de ataque
- ✅ Desenvolver habilidades em Python
- ✅ Preparação para certificações de segurança

## 🔬 Casos de Uso Avançados

### Análise Forense

```python
# Carregar logs específicos
from parsers.log_parser import JSONLogParser

logs = JSONLogParser.parse_file('data/http_logs.json')

# Análise customizada
suspicious_ips = set()
for log in logs:
    if log.get('is_suspicious'):
        suspicious_ips.add(log.get('client_ip'))

print(f"IPs suspeitos: {suspicious_ips}")
```

### Detecção Customizada

```python
from analyzers.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()

# Adicionar regras customizadas
custom_pattern = r'your_pattern_here'
detector.malicious_patterns['custom_attack'] = [custom_pattern]

# Executar detecção
results = detector.analyze_all(your_logs)
```

## 📈 Estatísticas do Projeto

- **Linhas de Código**: ~2000+
- **Módulos**: 10+
- **Tipos de Logs**: 4 (DNS, HTTP, SSH, FTP)
- **Tipos de Ameaças**: 10+
- **Comandos SPL**: 15+

## 🤝 Contribuindo

Contribuições são bem-vindas! Áreas para melhoria:

- [ ] Mais tipos de logs (SMTP, DHCP, Tunnel)
- [ ] Machine Learning para detecção de anomalias
- [ ] API REST para integração
- [ ] Visualizações em tempo real (WebSocket)
- [ ] Exportação para formatos SIEM reais
- [ ] Integração com threat intelligence feeds
- [ ] Dockerização
- [ ] Testes unitários

## 📝 License

MIT License - veja LICENSE para detalhes

## 🔗 Recursos Relacionados

- [Splunk Documentation](https://docs.splunk.com/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Original Project Inspiration](https://github.com/0xrajneesh/Splunk-Projects-For-Beginners)

## 👨‍💻 Autor

Desenvolvido como MVP de SIEM para aprendizado e demonstração de conceitos de segurança.

## 🎯 Próximos Passos

Após explorar o MVP, considere:

1. **Splunk Free**: Instalar Splunk Free Edition para comparação
2. **ELK Stack**: Experimentar Elasticsearch, Logstash, Kibana
3. **Graylog**: Alternativa open-source de SIEM
4. **Security Onion**: Distribuição Linux para monitoramento de segurança
5. **Wazuh**: SIEM open-source com HIDS integrado

---

⭐ **Se este projeto foi útil, considere dar uma estrela!**

🐛 **Encontrou um bug? Abra uma issue!**

💡 **Tem uma ideia? Contribua com um PR!**
