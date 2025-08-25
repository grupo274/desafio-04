#!/bin/bash

set -e  # Parar em qualquer erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando ambiente CrewAI + Ollama...${NC}"

# Função para log com timestamp
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função para verificar se Ollama está rodando
check_ollama() {
    curl -s http://localhost:11434/api/version > /dev/null 2>&1
    return $?
}

# Função para verificar se Ollama remoto está rodando
check_ollama_remote() {
    if [ -n "$OLLAMA_BASE_URL" ]; then
        curl -s "${OLLAMA_BASE_URL}/api/version" > /dev/null 2>&1
        return $?
    fi
    return 1
}

# Função para verificar se um modelo existe
check_model() {
    local model=$1
    ollama list 2>/dev/null | grep -q "$model"
    return $?
}

# Função para baixar modelo com retry
download_model() {
    local model=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "${YELLOW}📥 Tentativa $attempt/$max_attempts: Baixando modelo $model...${NC}"
        
        if ollama pull "$model"; then
            log "${GREEN}✅ Modelo $model baixado com sucesso!${NC}"
            return 0
        else
            log "${RED}❌ Falha na tentativa $attempt${NC}"
            attempt=$((attempt + 1))
            [ $attempt -le $max_attempts ] && sleep 5
        fi
    done
    
    return 1
}

# 1. Verificar se deve usar Ollama local ou remoto
USE_LOCAL_OLLAMA=false

if [ "$FORCE_MOCK_LLM" = "true" ]; then
    log "${YELLOW}🔧 FORCE_MOCK_LLM ativado, pulando configuração do Ollama${NC}"
elif check_ollama_remote; then
    log "${GREEN}✅ Ollama remoto disponível em $OLLAMA_BASE_URL${NC}"
else
    USE_LOCAL_OLLAMA=true
    log "${BLUE}🔄 Configurando Ollama local...${NC}"
fi

# 2. Configurar Ollama local se necessário
if [ "$USE_LOCAL_OLLAMA" = "true" ]; then
    if ! check_ollama; then
        log "${BLUE}🔄 Iniciando Ollama local...${NC}"
        ollama serve > /tmp/ollama.log 2>&1 &
        OLLAMA_PID=$!
        
        # Aguardar Ollama iniciar
        log "${YELLOW}⏳ Aguardando Ollama inicializar...${NC}"
        for i in {1..60}; do
            if check_ollama; then
                log "${GREEN}✅ Ollama local iniciado! (PID: $OLLAMA_PID)${NC}"
                break
            fi
            sleep 1
            if [ $i -eq 60 ]; then
                log "${RED}❌ Timeout: Ollama não iniciou em 60 segundos${NC}"
                log "${RED}Log do Ollama:${NC}"
                cat /tmp/ollama.log
                exit 1
            fi
        done
    else
        log "${GREEN}✅ Ollama local já está rodando${NC}"
    fi
fi

# 3. Configurar modelos (só se Ollama estiver disponível)
if [ "$FORCE_MOCK_LLM" != "true" ] && (check_ollama || check_ollama_remote); then
    REQUIRED_MODELS=("${DEFAULT_MODEL:-llama3.2}" "llama3.2:1b")
    
    log "${BLUE}🔍 Verificando modelos disponíveis...${NC}"
    ollama list 2>/dev/null || true
    
    MODEL_AVAILABLE=false
    for model in "${REQUIRED_MODELS[@]}"; do
        if check_model "$model"; then
            log "${GREEN}✅ Modelo $model já disponível${NC}"
            MODEL_AVAILABLE=true
            break
        fi
    done
    
    # Baixar modelo se necessário
    if [ "$MODEL_AVAILABLE" = "false" ]; then
        for model in "${REQUIRED_MODELS[@]}"; do
            if download_model "$model"; then
                MODEL_AVAILABLE=true
                break
            fi
        done
        
        if [ "$MODEL_AVAILABLE" = "false" ]; then
            log "${YELLOW}⚠️ Nenhum modelo disponível. Usando Mock LLM como fallback.${NC}"
            export FORCE_MOCK_LLM=true
        fi
    fi
fi

# 4. Verificar estrutura de arquivos
log "${BLUE}📁 Verificando estrutura de arquivos...${NC}"

# Criar diretórios necessários
mkdir -p dados logs models temp

# Verificar arquivo de dados principal
if [ ! -f "dados/vales_refeicao.zip" ]; then
    log "${YELLOW}⚠️ dados/vales_refeicao.zip não encontrado${NC}"
    log "${BLUE}📝 Criando estrutura de exemplo...${NC}"
    
    # Criar arquivo README
    cat > dados/README.md << 'EOF'
# Dados para Processamento

## Arquivos Esperados

- `vales_refeicao.zip`: Arquivo principal com planilhas Excel
- Outros arquivos ZIP com dados estruturados

## Formato Esperado

As planilhas devem conter colunas como:
- Data, Valor, Descrição, Categoria, etc.

## Como Usar

1. Coloque seus arquivos ZIP na pasta `dados/`
2. Execute o sistema
3. Os resultados aparecerão em `logs/` e `temp/`
EOF
fi

# 5. Verificar dependências Python
log "${BLUE}🐍 Verificando dependências Python...${NC}"
python -c "
try:
    import crewai, pandas, openpyxl, requests
    print('✅ Dependências principais OK')
except ImportError as e:
    print(f'❌ Dependência faltando: {e}')
    exit(1)
" || {
    log "${YELLOW}📦 Instalando dependências faltantes...${NC}"
    pip install -q crewai pandas openpyxl requests
}

# 6. Status final do sistema
log "${GREEN}🎉 Ambiente configurado com sucesso!${NC}"
echo
log "${BLUE}🔧 Status final do sistema:${NC}"

if [ "$FORCE_MOCK_LLM" = "true" ]; then
    echo "   LLM: 🤖 Mock LLM (modo de desenvolvimento)"
elif check_ollama_remote; then
    echo "   LLM: 🌐 Ollama remoto ($OLLAMA_BASE_URL)"
    echo "   Modelos: $(curl -s "${OLLAMA_BASE_URL}/api/tags" | grep -o '"name"' | wc -l 2>/dev/null || echo '?') disponíveis"
elif check_ollama; then
    echo "   LLM: 🏠 Ollama local"
    echo "   Modelos: $(ollama list 2>/dev/null | grep -v "NAME" | wc -l) disponíveis"
else
    echo "   LLM: ❌ Nenhum disponível"
fi

echo "   Dados: $(ls dados/ 2>/dev/null | wc -l) arquivos"
echo "   Python: ✅ $(python --version)"

# 7. Executar aplicação
echo
if [ "$1" = "dev" ]; then
    log "${BLUE}🛠️ Executando em modo desenvolvimento...${NC}"
    python main_dev.py
else
    log "${BLUE}🚀 Executando aplicação principal...${NC}"
    python main.py
fi

# Capturar código de saída
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "${GREEN}✅ Aplicação finalizada com sucesso${NC}"
else
    log "${RED}❌ Aplicação finalizada com erro (código: $EXIT_CODE)${NC}"
fi

# 8. Manter container ativo para debug se em modo desenvolvimento
if [ "$DEBUG" = "true" ] || [ "$1" = "dev" ]; then
    log "${YELLOW}🔧 Modo debug ativo. Container ficará rodando...${NC}"
    log "${BLUE}Para acessar: docker exec -it crew_app /bin/bash${NC}"
    
    # Criar um servidor HTTP simples para health check
    python3 -c "
import http.server
import socketserver
import threading

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{\"status\":\"ok\",\"mode\":\"debug\"}')
        else:
            self.send_response(404)
            self.end_headers()

httpd = socketserver.TCPServer(('', 8000), HealthHandler)
print('Health server rodando na porta 8000...')
httpd.serve_forever()
" &
    
    # Manter container vivo
    tail -f /dev/null
fi

exit $EXIT_CODE