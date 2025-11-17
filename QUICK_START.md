# 🚀 Quick Start - Splunk SIEM MVP

## Instalação em 30 segundos

```bash
# 1. Clone o repositório (se ainda não clonou)
git clone https://github.com/HPxt/SplunkTest.git
cd SplunkTest/splunk-siem-mvp

# 2. Execute o pipeline completo
python3 siem_main.py --full --count 1000
```

Isso é tudo! Não há dependências para instalar. 🎉

## O que foi criado?

Após a execução, você terá:

### 📁 Dados Gerados
- **4000 logs** (1000 de cada tipo: DNS, HTTP, SSH, FTP)
- **~10% são ataques simulados** (SQL Injection, XSS, Brute Force, etc.)
- **Múltiplos formatos**: JSON, CSV, Apache, Syslog

### 🔍 Análises
- **Detecção automática de anomalias**
- **Classificação por severidade** (Critical, High, Medium, Low)
- **10+ tipos de ameaças** detectadas

### 📊 Dashboard
```bash
# Abra no navegador
firefox splunk-siem-mvp/reports/dashboard.html
# ou
google-chrome splunk-siem-mvp/reports/dashboard.html
```

## Comandos Essenciais

### 1. Gerar mais logs
```bash
python3 siem_main.py --generate-logs --count 5000
```

### 2. Executar queries SPL

**Detectar ataques SQL Injection:**
```bash
python3 siem_main.py --query "search http | where path contains 'OR'"
```

**Top IPs com falhas SSH:**
```bash
python3 siem_main.py --query "search ssh | where status=failed | stats count by source_ip"
```

**Análise de códigos HTTP:**
```bash
python3 siem_main.py --query "search http | stats count by status_code"
```

### 3. Apenas Dashboard
```bash
python3 siem_main.py --dashboard
```

### 4. Apenas Análise
```bash
python3 siem_main.py --analyze
```

## Estrutura de Arquivos Importante

```
splunk-siem-mvp/
├── siem_main.py           # ⭐ Aplicação principal
├── data/                  # 📊 Logs em JSON
│   ├── dns_logs.json
│   ├── http_logs.json
│   ├── ssh_logs.json
│   └── ftp_logs.json
├── logs/                  # 📝 Logs formato texto
│   ├── apache_access.log
│   ├── auth.log
│   ├── dns.log
│   └── vsftpd.log
└── reports/              # 📈 Relatórios gerados
    ├── dashboard.html         # ⭐ Dashboard interativo
    └── security_alerts.json   # ⭐ Alertas de segurança
```

## Exemplos de Queries Avançadas

### Threat Hunting
```bash
# Buscar todos eventos suspeitos
python3 siem_main.py --query "search is_suspicious=true"

# Tipos de ataques detectados
python3 siem_main.py --query "search attack_type | stats count by attack_type"
```

### Análise de DNS
```bash
# Queries DNS mais lentas
python3 siem_main.py --query "search dns | where response_time_ms>100 | top query"

# Domínios não encontrados (potencial C2)
python3 siem_main.py --query "search dns | where response_code=NXDOMAIN | top query"
```

### Análise HTTP
```bash
# Erros do servidor
python3 siem_main.py --query "search http | where status_code>=500"

# Scanners detectados
python3 siem_main.py --query "search http | where user_agent contains 'sqlmap'"
```

### SSH Security
```bash
# Tentativas de brute force
python3 siem_main.py --query "search ssh | where status=failed | stats count by source_ip | sort -count"

# Logins bem-sucedidos
python3 siem_main.py --query "search ssh | where status=success | fields timestamp, user, source_ip"
```

## Ver Exemplos de Queries

```bash
python3 examples/example_queries.py
```

Isso mostra 30+ queries prontas para usar!

## Casos de Uso

Veja exemplos detalhados de:
- 🎯 Detecção de SQL Injection
- 🔐 SSH Brute Force Detection
- 🌐 DNS Tunneling
- 🔍 Web Scanner Detection
- E muito mais...

```bash
cat examples/use_cases.md
```

## Próximos Passos

### Nível Iniciante
1. ✅ Execute o pipeline completo (`--full`)
2. ✅ Explore o dashboard HTML
3. ✅ Teste queries básicas
4. ✅ Leia os casos de uso

### Nível Intermediário
1. 🔧 Modifique os geradores para criar novos padrões
2. 📊 Customize o dashboard
3. 🔍 Crie novas regras de detecção
4. 📈 Analise os alertas gerados

### Nível Avançado
1. 🚀 Integre com ferramentas reais (fail2ban, iptables)
2. 🤖 Adicione Machine Learning
3. 🌐 Crie API REST
4. 📡 Implemente alertas em tempo real

## Troubleshooting

### Erro: "No module named..."
Você só precisa de Python 3.8+. Sem dependências externas!

```bash
python3 --version  # Deve ser >= 3.8
```

### Dashboard não abre
```bash
# Caminho completo do dashboard
realpath reports/dashboard.html

# Abra manualmente no navegador
```

### Sem logs gerados
```bash
# Verifique se os diretórios existem
ls -la data/ logs/ reports/

# Re-execute a geração
python3 siem_main.py --generate-logs --count 1000
```

## Performance

### Logs Recomendados por Execução
- **Teste rápido**: 100 logs/tipo (~400 total) - 5 segundos
- **Desenvolvimento**: 1000 logs/tipo (~4000 total) - 10 segundos
- **Demonstração**: 5000 logs/tipo (~20000 total) - 30 segundos
- **Produção simulada**: 10000+ logs/tipo - 1+ minuto

## Customização

### Ajustar taxa de ataques
Edite `config/siem_config.json`:
```json
{
  "suspicious_ratios": {
    "dns": 0.15,    // 15% malicioso
    "http": 0.20,   // 20% ataques
    "ssh": 0.25,    // 25% brute force
    "ftp": 0.15     // 15% suspeito
  }
}
```

### Adicionar novos padrões de ataque
Edite `analyzers/anomaly_detector.py` e adicione na seção `malicious_patterns`.

## Recursos de Aprendizado

- 📖 **README.md** - Documentação completa
- 📝 **use_cases.md** - 10+ cenários de segurança
- 💻 **example_queries.py** - 30+ queries prontas
- ⚙️ **siem_config.json** - Todas as configurações

## Comandos Úteis

```bash
# Ver estrutura do projeto
tree splunk-siem-mvp/

# Contar eventos por tipo
wc -l data/*.json

# Ver alertas de segurança
cat reports/security_alerts.json | python3 -m json.tool

# Buscar em logs texto
grep "failed" logs/auth.log

# Top 10 IPs em HTTP
grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' logs/apache_access.log | sort | uniq -c | sort -rn | head -10
```

## Ajuda

```bash
python3 siem_main.py --help
```

---

## 🎓 Aprendizado Progressivo

### Semana 1: Fundamentos
- [ ] Execute pipeline completo
- [ ] Explore todos os logs gerados
- [ ] Entenda o dashboard
- [ ] Execute 10 queries básicas

### Semana 2: Análise
- [ ] Identifique todos os tipos de ataques
- [ ] Analise os alertas gerados
- [ ] Crie queries customizadas
- [ ] Estude os padrões de detecção

### Semana 3: Customização
- [ ] Modifique geradores de logs
- [ ] Adicione novas regras de detecção
- [ ] Customize o dashboard
- [ ] Crie seus próprios casos de uso

### Semana 4: Integração
- [ ] Conecte com ferramentas reais
- [ ] Implemente automação de resposta
- [ ] Adicione novas fontes de logs
- [ ] Crie relatórios customizados

---

**Pronto para começar? Execute agora:**

```bash
cd splunk-siem-mvp
python3 siem_main.py --full --count 1000
```

**Tempo de execução:** ~15 segundos
**Resultado:** Sistema SIEM completo operacional! 🚀
