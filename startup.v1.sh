#!/bin/bash

echo "🚀 Iniciando ambiente de desenvolvimento..."

# Função para verificar se Ollama está rodando
check_ollama() {
    curl -s http://localhost:11434/api/version > /dev/null 2>&1
    return $?
}

# Função para verificar se um modelo existe
check_model() {
    local model=$1
    ollama list | grep -q "$model"
    return $?
}

# 1. Iniciar Ollama se não estiver rodando
if ! check_ollama; then
    echo "🔄 Iniciando Ollama..."
    ollama serve > /dev/null 2>&1 &
    
    # Aguardar Ollama iniciar
    echo "⏳ Aguardando Ollama inicializar..."
    for i in {1..30}; do
        if check_ollama; then
            echo "✅ Ollama iniciado!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo "❌ Timeout: Ollama não iniciou"
            exit 1
        fi
    done
else
    echo "✅ Ollama já está rodando"
fi

# 2. Verificar/baixar modelo necessário
REQUIRED_MODEL="llama3.2"

echo "🔍 Verificando modelos disponíveis..."
ollama list

if ! check_model "$REQUIRED_MODEL"; then
    echo "📥 Baixando modelo $REQUIRED_MODEL (pode demorar alguns minutos)..."
    ollama pull $REQUIRED_MODEL
    
    if [ $? -eq 0 ]; then
        echo "✅ Modelo $REQUIRED_MODEL baixado com sucesso!"
    else
        echo "❌ Erro ao baixar modelo. Tentando modelo menor..."
        ollama pull llama3.2:1b
        if [ $? -eq 0 ]; then
            echo "✅ Modelo llama3.2:1b baixado com sucesso!"
        else
            echo "⚠️ Não foi possível baixar modelo. Usando Mock LLM."
        fi
    fi
else
    echo "✅ Modelo $REQUIRED_MODEL já disponível"
fi

# 3. Verificar estrutura de arquivos
echo "📁 Verificando arquivos necessários..."

if [ ! -f "dados/vales_refeicao.zip" ]; then
    echo "⚠️ Arquivo dados/vales_refeicao.zip não encontrado"
    echo "📝 Criando arquivo de exemplo..."
    mkdir -p dados
    echo "# Arquivo de exemplo - substitua pelo arquivo real" > dados/README.txt
fi

# 4. Verificar dependências Python
echo "🐍 Verificando dependências Python..."
python -c "import crewai, pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependências..."
    pip install -q crewai pandas openpyxl requests
fi

# 5. Executar a aplicação
echo "🎉 Ambiente configurado!"
echo ""
echo "🔧 Status final do sistema:"
echo "   Ollama: $(check_ollama && echo '✅ Rodando' || echo '❌ Parado')"
echo "   Modelos: $(ollama list 2>/dev/null | grep -v "NAME" | wc -l) disponíveis"
echo ""

echo "🚀 Executando aplicação..."
echo pwd 
python main.py

echo "📋 Aplicação finalizada. Para reiniciar, execute: python main.py"

# Manter container rodando para debug
echo "🔧 Container ficará ativo para debug. Use: docker exec -it <container> /bin/bash"
tail -f /dev/null
