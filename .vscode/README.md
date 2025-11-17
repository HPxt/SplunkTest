# 🔧 Configurações VSCode

Configurações otimizadas para desenvolvimento do Splunk SIEM MVP.

## 📋 Arquivos de Configuração

### 1. `launch.json` - Configurações de Debug

**5 configurações de debug prontas:**

1. **🌐 Flask: Backend Web**
   - Inicia o servidor Flask com debug
   - Porta: 5000
   - Hot reload ativado
   - **Como usar:** F5 > Selecionar "Flask: Backend Web"

2. **🖥️ SIEM: CLI Full Pipeline**
   - Executa pipeline completo
   - Gera 100 logs de cada tipo
   - **Como usar:** F5 > Selecionar "SIEM: CLI Full Pipeline"

3. **🔍 SIEM: Query SPL**
   - Executa query SPL de exemplo
   - **Como usar:** F5 > Selecionar "SIEM: Query SPL"
   - **Edite a query** em `args` para testar outras

4. **📊 SIEM: Generate Logs Only**
   - Apenas gera logs (500 de cada)
   - **Como usar:** F5 > Selecionar "SIEM: Generate Logs Only"

5. **🔬 SIEM: Analyze Only**
   - Apenas executa análise de segurança
   - **Como usar:** F5 > Selecionar "SIEM: Analyze Only"

### 2. `tasks.json` - Tasks Automatizadas

**5 tasks úteis:**

1. **🌐 Run Web App** (Default - Ctrl+Shift+B)
   - Inicia aplicação web completa
   - Executa `run_web_app.sh`

2. **📦 Install Web Dependencies**
   - Instala dependências do pip
   - Usa `requirements.txt`

3. **🧪 Run SIEM Full Test**
   - Testa sistema completo
   - Gera 100 logs e analisa

4. **🗑️ Clear Generated Data**
   - Limpa dados gerados
   - Remove logs, reports, etc

5. **🔧 Setup Virtual Environment**
   - Cria venv
   - Instala dependências

**Como executar tasks:**
- `Ctrl+Shift+B` (Windows/Linux)
- `Cmd+Shift+B` (Mac)
- Ou: `Terminal > Run Task...`

### 3. `settings.json` - Configurações do Editor

**Features ativadas:**
- ✅ Auto-format ao salvar
- ✅ Organize imports ao salvar
- ✅ Python type checking
- ✅ Flake8 linting
- ✅ Minimap habilitado
- ✅ Rulers em 80 e 120 chars
- ✅ Esconder __pycache__
- ✅ Tab size = 4 espaços

### 4. `extensions.json` - Extensões Recomendadas

**Extensões essenciais:**
- Python (Microsoft)
- Pylance (Microsoft)
- Python Debugger (Microsoft)

**Extensões úteis:**
- Auto Close Tag
- Auto Rename Tag
- Path IntelliSense
- Error Lens
- Todo Tree
- Indent Rainbow

**Instalação:**
VSCode sugerirá instalar quando abrir o projeto.

## 🚀 Como Usar

### Primeira Vez

1. **Abrir Projeto**
   ```bash
   code /path/to/SplunkTest
   ```

2. **Instalar Extensões**
   - VSCode mostrará popup
   - Clicar "Install All"

3. **Instalar Dependências**
   - `Ctrl+Shift+P` > "Run Task"
   - Selecionar "Install Web Dependencies"

4. **Rodar Aplicação Web**
   - `F5` > "Flask: Backend Web"
   - Ou `Ctrl+Shift+B`

### Desenvolvimento

#### Rodar Backend com Debug

```
F5 > Flask: Backend Web
```

- Coloque breakpoints clicando na margem esquerda
- Servidor para nos breakpoints
- Inspecione variáveis
- Use Debug Console

#### Executar CLI

```
F5 > SIEM: CLI Full Pipeline
```

- Executa pipeline completo
- Output no Terminal Integrado

#### Executar Tasks

```
Ctrl+Shift+B > Escolher task
```

## 🔍 Debug

### Backend (Python)

1. **Colocar Breakpoint**
   - Clicar na margem esquerda da linha
   - Aparece um ponto vermelho

2. **Iniciar Debug**
   - `F5` > "Flask: Backend Web"

3. **Fazer Requisição**
   - Acessar http://localhost:5000
   - Ou usar curl/Postman

4. **Debug Para**
   - Variáveis na sidebar esquerda
   - Watch expressions
   - Call stack
   - Debug console

**Comandos úteis:**
- `F5` - Continue
- `F10` - Step Over
- `F11` - Step Into
- `Shift+F11` - Step Out
- `Shift+F5` - Stop

### Frontend (JavaScript)

1. **Abrir DevTools**
   - F12 no navegador

2. **Sources Tab**
   - Localizar `app.js`
   - Colocar breakpoints

3. **Console**
   ```javascript
   // Ver dados
   console.log(currentData);

   // Testar API
   fetch('/api/stats').then(r => r.json()).then(console.log);
   ```

## 📝 Atalhos Úteis

### VSCode

| Atalho | Ação |
|--------|------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+P` | Quick Open File |
| `Ctrl+Shift+F` | Find in Files |
| `Ctrl+Shift+B` | Run Build Task |
| `F5` | Start Debugging |
| `Ctrl+F5` | Run Without Debugging |
| `Ctrl+`` | Toggle Terminal |
| `Ctrl+Shift+E` | Explorer |
| `Ctrl+Shift+G` | Source Control |
| `Ctrl+Shift+D` | Run and Debug |

### Python

| Atalho | Ação |
|--------|------|
| `Shift+Alt+F` | Format Document |
| `F2` | Rename Symbol |
| `F12` | Go to Definition |
| `Alt+F12` | Peek Definition |
| `Shift+F12` | Find All References |

## 🛠️ Customização

### Mudar Porta do Flask

Editar `launch.json`:

```json
"args": [
    "run",
    "--host=0.0.0.0",
    "--port=8080"  // ← Mudar aqui
]
```

### Adicionar Nova Query SPL

Duplicar config em `launch.json`:

```json
{
    "name": "🔍 SIEM: Minha Query",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/splunk-siem-mvp/siem_main.py",
    "args": [
        "--query",
        "search ssh | where status=failed"  // ← Sua query
    ],
    "cwd": "${workspaceFolder}/splunk-siem-mvp",
    "console": "integratedTerminal"
}
```

### Adicionar Task

Em `tasks.json`:

```json
{
    "label": "Minha Task",
    "type": "shell",
    "command": "seu comando aqui",
    "problemMatcher": []
}
```

## 🐛 Troubleshooting

### Python não encontrado

1. `Ctrl+Shift+P` > "Python: Select Interpreter"
2. Escolher Python 3.8+

### Extensões não instalam

1. Verificar conexão internet
2. `Ctrl+Shift+P` > "Extensions: Install Extensions"
3. Buscar manualmente: "Python"

### Debug não inicia

1. Verificar se está no workspace correto
2. Verificar paths em `launch.json`
3. Verificar Python interpreter

### Tasks não aparecem

1. Reload window: `Ctrl+Shift+P` > "Developer: Reload Window"
2. Verificar `tasks.json` está correto

## 💡 Dicas

1. **Use Workspace** - Abra a pasta raiz (SplunkTest)
2. **Terminal Integrado** - Mais conveniente
3. **Multi-root Workspace** - Para múltiplos projetos
4. **Settings Sync** - Sincronize configs entre máquinas
5. **Snippets** - Crie snippets para código repetitivo
6. **IntelliSense** - Use Ctrl+Space para autocomplete
7. **Problems Panel** - Veja erros em tempo real
8. **Git Integration** - Já vem integrado

## 📚 Recursos

- [VSCode Docs](https://code.visualstudio.com/docs)
- [Python in VSCode](https://code.visualstudio.com/docs/python/python-tutorial)
- [Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [Tasks](https://code.visualstudio.com/docs/editor/tasks)

---

**Enjoy coding! 🚀**
