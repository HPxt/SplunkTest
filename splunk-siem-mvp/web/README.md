# Splunk SIEM Web Application

Uma aplicação web completa para o SIEM Splunk MVP com interface moderna e interativa.

## 🌟 Características

- **Dashboard em Tempo Real**: Visualize estatísticas e métricas de segurança
- **Navegação de Logs**: Browse e pesquise eventos de segurança
- **Gerenciamento de Alertas**: Visualize e filtre alertas por severidade
- **Console SPL**: Execute queries customizadas
- **Análise de Segurança**: Execute análises completas
- **Interface Responsiva**: Design moderno e adaptável

## 🏗️ Arquitetura

```
web/
├── backend/              # Backend Flask
│   ├── app.py           # Servidor principal
│   └── api/             # Endpoints REST
├── frontend/            # Frontend
│   ├── templates/       # HTML
│   ├── static/
│   │   ├── css/        # Estilos
│   │   └── js/         # JavaScript
└── requirements.txt     # Dependências Python
```

## 🚀 Início Rápido

### Opção 1: Script de Inicialização (Recomendado)

```bash
cd splunk-siem-mvp/web
chmod +x run_web_app.sh
./run_web_app.sh
```

### Opção 2: Manual

```bash
cd splunk-siem-mvp/web

# Instalar dependências
pip3 install -r requirements.txt

# Iniciar servidor
cd backend
python3 app.py
```

### Acessar a Aplicação

Abra o navegador e acesse: **http://localhost:5000**

## 📱 Páginas da Aplicação

### 1. Dashboard (Página Principal)
- Estatísticas gerais (eventos, alertas, log sources)
- Gráfico de distribuição de logs
- Top ameaças detectadas
- Alertas recentes

### 2. Logs
- Tabela de eventos com filtros
- Filtro por tipo de log (DNS, HTTP, SSH, FTP)
- Busca em tempo real
- Paginação

### 3. Alerts
- Grid de alertas de segurança
- Filtro por severidade
- Detalhes expandíveis
- Indicadores de comprometimento

### 4. Search (Console SPL)
- Editor de queries SPL
- Execução de queries customizadas
- Exemplos de queries
- Visualização de resultados

### 5. Analysis
- Execução de análise de segurança
- Visualização de resultados
- Estatísticas de ameaças
- Limpar dados

### 6. Settings
- Geração de logs
- Configuração de parâmetros
- Status do sistema
- Health check

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```

### Gerar Logs
```
POST /api/generate-logs
Body: {
  "count": 100,
  "types": ["dns", "http", "ssh", "ftp"]
}
```

### Executar Análise
```
POST /api/analyze
```

### Executar Query SPL
```
POST /api/query
Body: {
  "query": "search http | where status_code>400"
}
```

### Obter Logs
```
GET /api/logs?type=http&limit=100
```

### Obter Alertas
```
GET /api/alerts?severity=high&limit=50
```

### Obter Estatísticas
```
GET /api/stats
```

### Limpar Dados
```
POST /api/clear
```

## 🎨 Interface

### Design System

**Cores:**
- Primary: `#667eea` (Roxo)
- Danger: `#f56565` (Vermelho)
- Warning: `#ed8936` (Laranja)
- Success: `#48bb78` (Verde)

**Tema:** Dark Mode
- Background: `#0f0f1e`
- Cards: `#1a1a2e`, `#252538`
- Text: `#e0e0e0`

### Componentes

- **Stats Cards**: Cards com estatísticas principais
- **Charts**: Gráficos de barras horizontais
- **Alerts**: Cards de alertas com severidade
- **Tables**: Tabelas responsivas de dados
- **Forms**: Inputs e selects estilizados
- **Buttons**: Botões com gradiente e hover
- **Toast Notifications**: Notificações deslizantes
- **Loading Overlay**: Overlay com spinner

## 💻 Uso da Aplicação

### Workflow Típico

1. **Iniciar Aplicação**
   ```bash
   ./run_web_app.sh
   ```

2. **Gerar Logs** (Settings)
   - Acessar página Settings
   - Definir quantidade de logs
   - Selecionar tipos
   - Clicar em "Generate Logs"

3. **Executar Análise** (Analysis)
   - Acessar página Analysis
   - Clicar em "Run Analysis"
   - Visualizar resultados

4. **Visualizar Dashboard**
   - Retornar ao Dashboard
   - Ver estatísticas atualizadas
   - Explorar gráficos

5. **Investigar Alertas** (Alerts)
   - Acessar página Alerts
   - Filtrar por severidade
   - Expandir detalhes

6. **Executar Queries** (Search)
   - Acessar console SPL
   - Escrever ou usar exemplos
   - Executar query
   - Analisar resultados

## 🔧 Desenvolvimento

### Estrutura Backend (Flask)

```python
app.py                  # Servidor principal
├── @app.route('/')    # Dashboard
├── /api/health        # Health check
├── /api/generate-logs # Gerar logs
├── /api/analyze       # Executar análise
├── /api/query         # Executar query
├── /api/logs          # Obter logs
├── /api/alerts        # Obter alertas
├── /api/stats         # Estatísticas
└── /api/clear         # Limpar dados
```

### Estrutura Frontend

```javascript
app.js                          # App principal
├── Navigation                  # Sistema de navegação
├── API Functions               # Chamadas REST
├── Dashboard Functions         # Dashboard
├── Log Functions               # Logs
├── Alert Functions             # Alertas
├── Query Functions             # Queries SPL
├── Settings Functions          # Configurações
└── Utility Functions           # Helpers
```

## 📊 Demonstração

### Exemplo de Uso

```bash
# 1. Iniciar servidor
./run_web_app.sh

# 2. Em outro terminal, testar API
curl http://localhost:5000/api/health

# 3. Gerar logs via API
curl -X POST http://localhost:5000/api/generate-logs \
  -H "Content-Type: application/json" \
  -d '{"count": 500, "types": ["dns", "http", "ssh", "ftp"]}'

# 4. Executar análise
curl -X POST http://localhost:5000/api/analyze

# 5. Obter estatísticas
curl http://localhost:5000/api/stats
```

## 🐛 Troubleshooting

### Porta 5000 em uso
```bash
# Mudar porta no app.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Dependências não instaladas
```bash
pip3 install Flask Flask-CORS
```

### Erro ao importar módulos
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/splunk-siem-mvp"
```

### CORS Error no Browser
- O Flask-CORS já está configurado
- Verifique se o backend está rodando
- Acesse via http://localhost:5000 (não file://)

## 🚀 Deploy

### Desenvolvimento
```bash
python3 app.py
# Debug mode ativado
# Auto-reload em mudanças
```

### Produção
```bash
# Usar Gunicorn
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Futuro)
```bash
# Criar Dockerfile
# docker build -t splunk-siem-web .
# docker run -p 5000:5000 splunk-siem-web
```

## 🔐 Segurança

**IMPORTANTE**: Esta é uma aplicação de demonstração educacional.

Para produção, implementar:
- [ ] Autenticação (JWT, OAuth)
- [ ] HTTPS/SSL
- [ ] Rate limiting
- [ ] Input validation
- [ ] CSRF protection
- [ ] Session management
- [ ] API keys
- [ ] Logs de auditoria

## 📚 Recursos

- **Flask Documentation**: https://flask.palletsprojects.com/
- **REST API Design**: https://restfulapi.net/
- **Frontend JavaScript**: Vanilla JS (sem frameworks)
- **CSS Grid/Flexbox**: Layout responsivo

## 🎯 Próximos Passos

- [ ] Adicionar WebSocket para updates em tempo real
- [ ] Implementar filtros avançados
- [ ] Adicionar exportação de dados (CSV, JSON, PDF)
- [ ] Criar gráficos com Chart.js ou D3.js
- [ ] Implementar autenticação de usuários
- [ ] Adicionar tema claro/escuro toggle
- [ ] Criar mobile app (React Native/Flutter)
- [ ] Integração com Elasticsearch

## 📝 License

MIT License - Use livremente para aprendizado

---

**Desenvolvido para demonstração educacional de conceitos SIEM**

Para dúvidas ou sugestões, abra uma issue no GitHub!
