# check-project.ps1 - Verificar estrutura do projeto (CORRIGIDO)

Write-Host "🔍 Verificando estrutura do projeto..." -ForegroundColor Blue

# Verificar arquivos essenciais
$essentialFiles = @(
    "docker-compose.yml",
    "Dockerfile", 
    "requirements.txt",
    ".env.example",
    "startup.sh",
    "main.py",
    "main_dev.py"
)

$missingFiles = @()
$existingFiles = @()

foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        $existingFiles += $file
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        $missingFiles += $file  
        Write-Host "❌ $file (não encontrado)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📁 Estrutura atual:" -ForegroundColor Blue
Get-ChildItem -Name | Where-Object { $_ -notlike ".*" } | Sort-Object

Write-Host ""
Write-Host "📊 Resumo:" -ForegroundColor Yellow
Write-Host "Arquivos encontrados: $($existingFiles.Count)" -ForegroundColor Green
Write-Host "Arquivos faltando: $($missingFiles.Count)" -ForegroundColor Red

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "🛠️ Criando arquivos faltantes..." -ForegroundColor Blue
    
    # Criar main.py se não existir
    if ("main.py" -in $missingFiles) {
        $mainPyContent = @'
#!/usr/bin/env python3
"""
Main application entry point
"""

print("🚀 CrewAI Application Starting...")
print("⚠️ Este é um arquivo temporário - substitua pelo seu código real")

def main():
    print("💡 Implementar sua lógica principal aqui")
    print("📁 Verificar se dados estão em /app/dados/")
    print("🤖 Configurar LLM provider")
    
    # Exemplo básico de teste
    import os
    print(f"📂 Diretório atual: {os.getcwd()}")
    print(f"📋 Arquivos disponíveis: {os.listdir('.')}")
    
    if os.path.exists("dados"):
        print(f"📊 Dados encontrados: {os.listdir('dados')}")
    else:
        print("⚠️ Pasta 'dados' não encontrada")
        os.makedirs("dados", exist_ok=True)
        print("📁 Pasta 'dados' criada")

if __name__ == "__main__":
    main()
'@
        $mainPyContent | Out-File -FilePath "main.py" -Encoding UTF8
        Write-Host "✅ main.py criado" -ForegroundColor Green
    }
    
    # Criar main_dev.py se não existir
    if ("main_dev.py" -in $missingFiles) {
        $mainDevContent = @'
#!/usr/bin/env python3
"""
Development and testing utilities
"""

import os
from pathlib import Path

def test_tools_directly():
    """Testa as ferramentas diretamente sem usar o CrewAI"""
    print("🧪 Testando ferramentas diretamente...")
    
    try:
        # Teste básico de importação
        print("📦 Testando importações...")
        
        # Verificar se dados existem
        dados_path = Path("dados")
        if dados_path.exists():
            arquivos = list(dados_path.glob("*.zip"))
            print(f"📁 Arquivos ZIP encontrados: {len(arquivos)}")
            for arquivo in arquivos:
                print(f"  - {arquivo.name}")
        else:
            print("⚠️ Pasta dados não encontrada, criando...")
            dados_path.mkdir(exist_ok=True)
            
        print("✅ Teste básico concluído")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_with_mock_crew():
    """Testa com CrewAI mas usando Mock LLM"""
    print("🧪 Testando com Mock LLM...")
    
    # Forçar uso do Mock LLM
    os.environ['FORCE_MOCK_LLM'] = 'true'
    
    try:
        print("🤖 Mock LLM configurado")
        print("✅ Teste com Mock concluído")
        
    except Exception as e:
        print(f"❌ Erro no teste com Mock: {e}")

if __name__ == "__main__":
    print("=== MODO DE DESENVOLVIMENTO ===\n")
    
    # Escolher o que testar
    print("Escolha:")
    print("(1) Testar ferramentas diretamente")
    print("(2) Testar com Mock LLM")
    
    try:
        modo = input("Digite 1 ou 2: ").strip()
        
        if modo == "1":
            test_tools_directly()
        elif modo == "2":
            test_with_mock_crew()
        else:
            print("❌ Opção inválida")
            test_tools_directly()  # Default
            
    except KeyboardInterrupt:
        print("\n👋 Teste interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")
        test_tools_directly()  # Fallback
'@
        $mainDevContent | Out-File -FilePath "main_dev.py" -Encoding UTF8
        Write-Host "✅ main_dev.py criado" -ForegroundColor Green
    }
    
    # Criar startup.sh se não existir
    if ("startup.sh" -in $missingFiles) {
        $startupContent = @'
#!/bin/bash

set -e  # Parar em qualquer erro

echo "🚀 Iniciando CrewAI Application..."

# Verificar Python
python --version

# Verificar estrutura
echo "📁 Estrutura atual:"
ls -la

# Verificar dados  
if [ -d "dados" ]; then
    echo "📊 Arquivos de dados:"
    ls -la dados/
else
    echo "⚠️ Pasta dados não encontrada, criando..."
    mkdir -p dados
fi

# Criar arquivo README se não existir
if [ ! -f "dados/README.md" ]; then
    cat > dados/README.md << 'EOF'
# Pasta de Dados

Coloque aqui seus arquivos ZIP com as planilhas para processamento.

Exemplo: vales_refeicao.zip
EOF
fi

# Executar aplicação
echo "🎯 Executando aplicação principal..."
python main.py

# Se falhar, manter container ativo para debug
echo "🔧 Aplicação finalizada. Container ficará ativo para debug."
tail -f /dev/null
'@
        $startupContent | Out-File -FilePath "startup.sh" -Encoding UTF8
        Write-Host "✅ startup.sh criado" -ForegroundColor Green
    }
    
    # Criar requirements.txt se não existir
    if ("requirements.txt" -in $missingFiles) {
        $requirementsContent = @'
# Core dependencies
crewai>=0.28.0
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.31.0

# Optional LLM providers
openai>=1.0.0
google-generativeai>=0.4.0
anthropic>=0.18.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.0

# Development
pytest>=7.0.0
'@
        $requirementsContent | Out-File -FilePath "requirements.txt" -Encoding UTF8
        Write-Host "✅ requirements.txt criado" -ForegroundColor Green
    }
    
    # Criar .env.example se não existir
    if (".env.example" -in $missingFiles) {
        $envContent = @'
# ===========================================
# CONFIGURAÇÃO DE AMBIENTE - CrewAI System  
# ===========================================

# Modo de operação
DEBUG=false
LOG_LEVEL=INFO

# Configuração de LLM
LLM_PROVIDER=ollama
DEFAULT_MODEL=llama3.2
FORCE_MOCK_LLM=false

# URLs de serviços
OLLAMA_BASE_URL=http://ollama:11434

# Chaves de API (opcionais)
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
'@
        $envContent | Out-File -FilePath ".env.example" -Encoding UTF8
        Write-Host "✅ .env.example criado" -ForegroundColor Green
    }
}

# Verificar se pasta dados existe
if (-not (Test-Path "dados")) {
    New-Item -ItemType Directory -Name "dados" -Force | Out-Null
    Write-Host "✅ Pasta 'dados' criada" -ForegroundColor Green
}

Write-Host ""
if ($missingFiles.Count -eq 0) {
    Write-Host "🎉 Projeto está completo!" -ForegroundColor Green
} else {
    Write-Host "🛠️ Arquivos faltantes foram criados!" -ForegroundColor Yellow
    Write-Host "📝 Revise os arquivos criados e substitua pelo seu código real" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Blue
Write-Host "1. Coloque seus dados em dados/vales_refeicao.zip" -ForegroundColor White
Write-Host "2. Execute: docker compose build" -ForegroundColor White  
Write-Host "3. Execute: docker compose up -d" -ForegroundColor White
Write-Host "4. Verifique: docker compose ps" -ForegroundColor White

Write-Host ""
Write-Host "🔧 Comandos úteis:" -ForegroundColor Cyan
Write-Host "docker compose build --no-cache" -ForegroundColor White
Write-Host "docker compose up -d" -ForegroundColor White
Write-Host "docker compose logs -f crew-app" -ForegroundColor White
Write-Host "docker exec -it crew_app python main_dev.py" -ForegroundColor White