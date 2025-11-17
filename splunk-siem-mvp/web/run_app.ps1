# Script para rodar a aplicação Splunk SIEM Web
# Atualiza o PATH e inicia o servidor Flask

# Atualiza o PATH com as variáveis do sistema
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verifica se Python está disponível
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado no PATH!" -ForegroundColor Red
    Write-Host "Tente executar: `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')" -ForegroundColor Yellow
    exit 1
}

# Navega para o diretório do backend
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Verifica se as dependências estão instaladas
Write-Host "Verificando dependências..." -ForegroundColor Cyan
try {
    python -m pip show Flask | Out-Null
    Write-Host "Dependências OK!" -ForegroundColor Green
} catch {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

# Inicia o servidor
Write-Host "`nIniciando servidor Flask..." -ForegroundColor Cyan
Write-Host "Acesse: http://localhost:5000`n" -ForegroundColor Green
python backend\app.py

