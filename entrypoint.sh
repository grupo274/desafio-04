#!/bin/bash

echo "🐳 Iniciando container com Ollama + CrewAI..."

# Função para cleanup ao sair
cleanup() {
    echo "🧹 Finalizando processos..."
    pkill -f ollama || true
    exit 0
}
trap cleanup SIGTERM SIGINT

# Função para verificar se Ollama está rodando
check_ollama() {
    curl -s http://localhost:11434/api/version > /dev/null 2>&1
    return $?
}

# 1. Iniciar Ollama em background
echo "🚀 Iniciando Ollama server..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

# 2. Aguardar Ollama ficar disponível
echo "⏳ Aguardando Ollama inicializar..."
for i in {1..60}; do
    if check_ollama; then
        echo "✅ Ollama rodando na porta 11434"
        break
    fi
    sleep 2
    if [ $i -eq 60 ]; then
        echo "❌ Timeout: Ollama não iniciou em 2 minutos"
        echo "📋 Log do Ollama:"
        cat /tmp/ollama.log
        exit 1
    fi
    echo "   Tentativa $i/60..."
done

# 3. Verificar se temos modelos, senão baixar um pequeno
echo "🔍 Verificando modelos disponíveis..."
MODELS=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)

if [ "$MODELS" -eq 0 ]; then
    echo "📥 Nenhum modelo encontrado. Baixando modelo pequeno..."
    echo "   Isso pode levar alguns minutos na primeira execução..."
    
    # Tentar modelos em ordem de preferência (menor para maior)
    for model in "llama3.2:1b" "llama3.2" "mistral:7b" "llama3.1:8b"; do
        echo "🔄 Tentando baixar $model..."
        if timeout 300 ollama pull $model; then
            echo "✅ Modelo $model baixado com sucesso!"
            break
        else
            echo "❌ Falha ao baixar $model, tentando próximo..."
        fi
    done
    
    # Verificar se conseguiu baixar algum modelo
    NEW_MODELS=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)
    if [ "$NEW_MODELS" -eq 0 ]; then
        echo "⚠️ Não foi possível baixar nenhum modelo"
        echo "🎭 A aplicação usará Mock LLM"
    fi
else
    echo "✅ Encontrados $MODELS modelo(s) já instalado(s)"
fi

# 4. Mostrar status atual
echo ""
echo "📊 Status do sistema:"
echo "   Ollama PID: $OLLAMA_PID"
echo "   Status: $(check_ollama && echo '🟢 Rodando' || echo '🔴 Parado')"
echo "   Modelos disponíveis:"
ollama list 2>/dev/null || echo "   (Nenhum modelo listado)"
echo ""

# 5. Executar a aplicação
echo "🚀 Executando aplicação CrewAI..."
python main.py

# 6. Se a aplicação terminou, mostrar opções
echo ""
echo "📋 Aplicação finalizada."
echo "🔧 Para debug, conecte no container:"
echo "   docker exec -it \$(docker ps -q) /bin/bash"
echo ""
echo "🔄 Para executar novamente:"
echo "   python main.py"
echo ""

# 7. Manter container ativo para investigação
echo "⏸️ Container ficará ativo. Pressione Ctrl+C para sair."
wait