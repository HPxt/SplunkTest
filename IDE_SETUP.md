# 🖥️ Como Rodar na sua IDE

Guia completo para executar o Splunk SIEM MVP na sua IDE favorita.

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno (Chrome, Firefox, Edge)

## 🎯 Opções de Execução

### Opção 1: Aplicação Web Integrada (RECOMENDADO)

A aplicação web já vem com backend e frontend integrados. O Flask serve tanto a API quanto os arquivos estáticos.

### Opção 2: Backend e Frontend Separados

Para desenvolvimento, você pode rodar o backend sozinho e acessar a API via ferramentas como Postman, Insomnia ou curl.

---

## 🚀 Método 1: Execução Rápida (1 Comando)

### Terminal / Command Line

```bash
# Navegar até o diretório web
cd splunk-siem-mvp/web

# Executar script de inicialização
./run_web_app.sh
```

**Acesse:** http://localhost:5000

---

## 🔧 Método 2: Execução Manual (Passo a Passo)

### 1. Instalar Dependências

```bash
cd splunk-siem-mvp/web

# Instalar dependências Python
pip3 install -r requirements.txt

# Ou usando pip
pip install -r requirements.txt
```

**Dependências instaladas:**
- Flask==3.0.0
- Flask-CORS==4.0.0
- Werkzeug==3.0.1

### 2. Rodar o Backend (Flask)

```bash
cd backend
python3 app.py

# Ou
python app.py
```

**Servidor iniciará em:**
- 🌐 Frontend: http://localhost:5000
- 📡 API: http://localhost:5000/api

---

## 💻 VSCode (Visual Studio Code)

### Setup Completo

#### 1. Abrir Projeto

```bash
# Abrir VSCode no diretório raiz
code /path/to/SplunkTest
```

#### 2. Instalar Extensões Recomendadas

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Python Debugger** (Microsoft)

#### 3. Configurar Ambiente Virtual (Opcional)

```bash
# Criar virtual environment
cd splunk-siem-mvp/web
python3 -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

#### 4. Configuração de Debug (launch.json)

Criar arquivo `.vscode/launch.json` na raiz do projeto:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask: Backend",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--host=0.0.0.0",
                "--port=5000"
            ],
            "cwd": "${workspaceFolder}/splunk-siem-mvp/web/backend",
            "jinja": true,
            "justMyCode": true
        },
        {
            "name": "Python: SIEM Main (CLI)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/splunk-siem-mvp/siem_main.py",
            "args": [
                "--full",
                "--count",
                "100"
            ],
            "cwd": "${workspaceFolder}/splunk-siem-mvp",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

#### 5. Executar com Debug

1. Pressione `F5` ou vá em `Run > Start Debugging`
2. Selecione "Flask: Backend"
3. Servidor iniciará em modo debug
4. Acesse http://localhost:5000

#### 6. Configurar Tasks (tasks.json)

Criar `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Web App",
            "type": "shell",
            "command": "cd splunk-siem-mvp/web && ./run_web_app.sh",
            "problemMatcher": [],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Install Dependencies",
            "type": "shell",
            "command": "pip3 install -r requirements.txt",
            "options": {
                "cwd": "${workspaceFolder}/splunk-siem-mvp/web"
            },
            "problemMatcher": []
        }
    ]
}
```

**Executar task:** `Ctrl+Shift+B` (Windows/Linux) ou `Cmd+Shift+B` (Mac)

---

## 🐍 PyCharm / IntelliJ IDEA

### Setup Completo

#### 1. Abrir Projeto

- `File > Open` → Selecionar pasta `SplunkTest`

#### 2. Configurar Interpretador Python

1. `File > Settings > Project > Python Interpreter`
2. Clicar em ⚙️ > Add
3. Escolher:
   - **System Interpreter** (usar Python do sistema)
   - **Virtualenv** (criar ambiente virtual)
4. Selecionar Python 3.8+

#### 3. Instalar Dependências

PyCharm detectará automaticamente `requirements.txt`:
- Clique no banner amarelo: "Install requirements"
- Ou manualmente: `Terminal > pip install -r requirements.txt`

#### 4. Configurar Run Configuration

##### Para o Backend (Flask):

1. `Run > Edit Configurations...`
2. Clicar `+` > Python
3. Configurar:

```
Name: Flask Backend
Script path: [vazio]
Module name: flask
Parameters: run --host=0.0.0.0 --port=5000
Environment variables:
  FLASK_APP=app.py
  FLASK_ENV=development
  FLASK_DEBUG=1
Python interpreter: [seu interpretador]
Working directory: /path/to/SplunkTest/splunk-siem-mvp/web/backend
```

4. Clicar OK

##### Para o CLI:

1. `Run > Edit Configurations...`
2. Clicar `+` > Python
3. Configurar:

```
Name: SIEM CLI Full
Script path: /path/to/SplunkTest/splunk-siem-mvp/siem_main.py
Parameters: --full --count 100
Working directory: /path/to/SplunkTest/splunk-siem-mvp
```

#### 5. Executar

- Selecionar configuração no dropdown (topo direito)
- Clicar ▶️ Run ou 🐛 Debug
- Acesse http://localhost:5000

---

## 🪟 Windows

### PowerShell

```powershell
# Navegar
cd splunk-siem-mvp\web

# Instalar dependências
pip install -r requirements.txt

# Rodar backend
cd backend
python app.py
```

### Command Prompt (CMD)

```cmd
cd splunk-siem-mvp\web
pip install -r requirements.txt
cd backend
python app.py
```

### Windows Terminal

Recomendado para melhor experiência:

```powershell
# Instalar Windows Terminal da Microsoft Store
# Depois executar:
cd splunk-siem-mvp\web
.\run_web_app.sh
```

---

## 🐧 Linux

```bash
cd splunk-siem-mvp/web

# Opção 1: Script
chmod +x run_web_app.sh
./run_web_app.sh

# Opção 2: Manual
pip3 install -r requirements.txt
cd backend
python3 app.py
```

---

## 🍎 macOS

```bash
cd splunk-siem-mvp/web

# Instalar dependências
pip3 install -r requirements.txt

# Rodar
./run_web_app.sh
```

---

## 🐳 Docker (Futuro)

### Criar Dockerfile

Criar `splunk-siem-mvp/web/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copiar código
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "backend/app.py"]
```

### Docker Compose

Criar `docker-compose.yml`:

```yaml
version: '3.8'

services:
  siem-web:
    build: ./splunk-siem-mvp/web
    ports:
      - "5000:5000"
    volumes:
      - ./splunk-siem-mvp:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
```

**Executar:**
```bash
docker-compose up
```

---

## 🧪 Desenvolvimento e Testing

### Hot Reload

O Flask já vem configurado com auto-reload:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

Qualquer mudança no código Python reinicia automaticamente o servidor.

### Frontend (HTML/CSS/JS)

Basta dar refresh no navegador (F5) para ver mudanças:
- HTML: `frontend/templates/index.html`
- CSS: `frontend/static/css/styles.css`
- JS: `frontend/static/js/app.js`

### Testar API

#### Usando curl

```bash
# Health check
curl http://localhost:5000/api/health

# Gerar logs
curl -X POST http://localhost:5000/api/generate-logs \
  -H "Content-Type: application/json" \
  -d '{"count": 100, "types": ["dns", "http"]}'

# Estatísticas
curl http://localhost:5000/api/stats

# Executar query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "search http"}'
```

#### Usando Python

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Gerar logs
response = requests.post('http://localhost:5000/api/generate-logs',
    json={"count": 100, "types": ["dns", "http"]})
print(response.json())
```

---

## 🔍 Debugging

### Backend Python

#### VSCode
1. Colocar breakpoints clicando na margem esquerda
2. F5 para iniciar debug
3. Fazer requisição HTTP
4. Debugger para no breakpoint

#### PyCharm
1. Clicar na margem para breakpoint
2. Debug (🐛) ao invés de Run
3. Fazer requisição
4. Inspecionar variáveis

### Frontend JavaScript

1. Abrir DevTools (F12)
2. Aba "Sources"
3. Abrir `app.js`
4. Colocar breakpoints
5. Executar ação na interface
6. Debugger para no breakpoint

**Console útil:**
```javascript
// Ver dados atuais
console.log(currentData);

// Testar API diretamente
fetch('/api/stats').then(r => r.json()).then(console.log);
```

---

## 📝 Logs e Monitoring

### Ver Logs do Backend

O servidor Flask imprime logs no terminal:

```
 * Running on http://0.0.0.0:5000
 * Restarting with stat
 * Debugger is active!
127.0.0.1 - - [17/Nov/2025 10:30:45] "GET /api/stats HTTP/1.1" 200 -
127.0.0.1 - - [17/Nov/2025 10:30:46] "POST /api/analyze HTTP/1.1" 200 -
```

### Adicionar Logging Personalizado

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# No seu código
logger.info('Gerando logs...')
logger.debug(f'Total: {total}')
logger.error('Erro ao processar')
```

---

## ⚙️ Configurações Avançadas

### Mudar Porta

Editar `backend/app.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Adicionar HTTPS (Desenvolvimento)

```python
# Gerar certificado self-signed
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

app.run(
    host='0.0.0.0',
    port=5000,
    ssl_context=('cert.pem', 'key.pem'),
    debug=True
)
```

### Environment Variables

Criar `.env` file:

```bash
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
```

Usar `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🚨 Troubleshooting

### Porta 5000 já em uso

```bash
# Descobrir processo usando porta 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Matar processo
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Ou mudar porta no app.py
```

### Módulo não encontrado

```bash
# Verificar se está no diretório correto
pwd

# Reinstalar dependências
pip3 install -r requirements.txt

# Verificar Python path
python3 -c "import sys; print(sys.path)"
```

### CORS Error

Já está configurado no `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

Se persistir, verificar se Flask-CORS está instalado:
```bash
pip3 install Flask-CORS
```

### Frontend não carrega

1. Verificar se servidor está rodando
2. Acessar `http://localhost:5000` (não `file://`)
3. Ver console do navegador (F12)
4. Verificar caminho dos arquivos estáticos

---

## 📚 Estrutura de Desenvolvimento

```
SplunkTest/
├── .vscode/              # Configurações VSCode
│   ├── launch.json
│   └── tasks.json
├── splunk-siem-mvp/
│   └── web/
│       ├── backend/
│       │   └── app.py    # ← Seu código backend
│       ├── frontend/
│       │   ├── templates/
│       │   │   └── index.html  # ← HTML
│       │   └── static/
│       │       ├── css/
│       │       │   └── styles.css  # ← CSS
│       │       └── js/
│       │           └── app.js  # ← JavaScript
│       └── requirements.txt
```

---

## 🎯 Quick Commands

```bash
# Setup inicial
cd splunk-siem-mvp/web
pip3 install -r requirements.txt

# Rodar aplicação
./run_web_app.sh

# Ou manualmente
cd backend && python3 app.py

# Acessar
open http://localhost:5000  # Mac
xdg-open http://localhost:5000  # Linux
start http://localhost:5000  # Windows
```

---

## 💡 Dicas

1. **Use ambiente virtual** para isolar dependências
2. **VSCode** tem melhor integração com Python
3. **PyCharm** tem debugging mais robusto
4. **Browser DevTools** (F12) é essencial para frontend
5. **Hot reload** já está ativado no Flask
6. **CORS** já está configurado
7. Backend serve **tanto API quanto frontend**

---

**Pronto!** Agora você pode desenvolver confortavelmente na sua IDE favorita! 🚀
