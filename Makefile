# ===================================
# Makefile para CrewAI + Ollama System
# ===================================

.PHONY: help build up down logs shell test dev clean

# Variáveis
COMPOSE_FILE=docker-compose.yml
PROJECT_NAME=crew-vr
MAIN_SERVICE=crew-app

# Comando padrão
help:
	@echo "🚀 Comandos disponíveis:"
	@echo ""
	@echo "📦 BUILD & DEPLOY:"
	@echo "  make build          - Construir todas as imagens"
	@echo "  make up             - Subir todos os serviços"
	@echo "  make up-dev         - Subir com perfil de desenvolvimento"
	@echo "  make down           - Parar todos os serviços"
	@echo "  make restart        - Reiniciar serviços principais"
	@echo ""
	@echo "📊 MONITORAMENTO:"
	@echo "  make logs           - Ver logs de todos os serviços"
	@echo "  make logs-app       - Ver logs apenas da aplicação"
	@echo "  make logs-ollama    - Ver logs apenas do Ollama"
	@echo "  make status         - Status dos containers"
	@echo ""
	@echo "🛠️ DESENVOLVIMENTO:"
	@echo "  make shell          - Acessar shell do container principal"
	@echo "  make shell-ollama   - Acessar shell do Ollama"
	@echo "  make test           - Executar testes"
	@echo "  make dev            - Modo desenvolvimento com reload"
	@echo ""
	@echo "🧹 LIMPEZA:"
	@echo "  make clean          - Limpar containers parados"
	@echo "  make clean-all      - Limpeza completa (cuidado!)"
	@echo "  make reset-ollama   - Reset completo do Ollama"
	@echo ""
	@echo "📋 UTILITÁRIOS:"
	@echo "  make models         - Listar modelos do Ollama"
	@echo "  make pull-model MODEL=llama3.2  - Baixar modelo específico"

# ===================================
# BUILD & DEPLOY
# ===================================

build:
	@echo "🔨 Construindo imagens..."
	docker compose -f $(COMPOSE_FILE) build --no-cache

up:
	@echo "🚀 Subindo serviços..."
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Serviços iniciados!"
	@echo "📱 App: http://localhost:8000"
	@echo "🤖 Ollama: http://localhost:11434"
	@echo "🔧 MCP: http://localhost:8001"

up-dev:
	@echo "🛠️ Subindo em modo desenvolvimento..."
	docker compose -f $(COMPOSE_FILE) --profile dev up -d
	@make logs-app

down:
	@echo "⏹️ Parando serviços..."
	docker compose -f $(COMPOSE_FILE) down

restart:
	@echo "🔄 Reiniciando serviços..."
	docker compose -f $(COMPOSE_FILE) restart $(MAIN_SERVICE) ollama

# ===================================
# MONITORAMENTO
# ===================================

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100

logs-app:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100 $(MAIN_SERVICE)

logs-ollama:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100 ollama

status:
	@echo "📊 Status dos containers:"
	docker compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "💾 Uso de espaço:"
	docker system df
	@echo ""
	@echo "🔧 Health checks:"
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# ===================================
# DESENVOLVIMENTO
# ===================================

shell:
	@echo "🐚 Acessando shell do container principal..."
	docker exec -it crew_app /bin/bash

shell-ollama:
	@echo "🤖 Acessando shell do Ollama..."
	docker exec -it ollama_service /bin/bash

test:
	@echo "🧪 Executando testes..."
	docker exec -it crew_app python main_dev.py

dev:
	@echo "🛠️ Modo desenvolvimento com reload..."
	docker compose -f $(COMPOSE_FILE) up --profile dev
	@make logs-app

# Executar comando específico no container
exec:
	@if [ -z "$(CMD)" ]; then \
		echo "❌ Uso: make exec CMD='seu comando aqui'"; \
	else \
		docker exec -it crew_app $(CMD); \
	fi

# ===================================
# UTILITÁRIOS OLLAMA
# ===================================

models:
	@echo "🤖 Modelos disponíveis no Ollama:"
	docker exec -it ollama_service ollama list

pull-model:
	@if [ -z "$(MODEL)" ]; then \
		echo "❌ Uso: make pull-model MODEL=nome_do_modelo"; \
		echo "📝 Exemplos: llama3.2, llama3.2:1b, codellama"; \
	else \
		echo "📥 Baixando modelo $(MODEL)..."; \
		docker exec -it ollama_service ollama pull $(MODEL); \
	fi

# Testar Ollama
test-ollama:
	@echo "🧪 Testando Ollama..."
	curl -X POST http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"Hello! Respond with just: OLLAMA OK","stream":false}' | jq -r '.response'

# ===================================
# LIMPEZA
# ===================================

clean:
	@echo "🧹 Limpando containers parados..."
	docker container prune -f
	docker image prune -f

clean-all:
	@echo "⚠️ ATENÇÃO: Limpeza completa (containers, imagens, volumes)!"
	@read -p "Tem certeza? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -af --volumes
	docker volume prune -f

reset-ollama:
	@echo "🔄 Resetando dados do Ollama..."
	@read -p "Isso apagará todos os modelos baixados. Continuar? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose -f $(COMPOSE_FILE) down
	docker volume rm $(PROJECT_NAME)_ollama_data
	docker compose -f $(COMPOSE_FILE) up -d ollama

# ===================================
# BACKUP & RESTORE
# ===================================

backup:
	@echo "💾 Fazendo backup dos dados..."
	mkdir -p backups
	docker run --rm -v $(PROJECT_NAME)_ollama_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/ollama-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	cp -r dados backups/dados-backup-$(shell date +%Y%m%d-%H%M%S)
	@echo "✅ Backup concluído em backups/"

restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "❌ Uso: make restore BACKUP=nome_do_arquivo.tar.gz"; \
		ls backups/; \
	else \
		echo "📥 Restaurando backup $(BACKUP)..."; \
		docker run --rm -v $(PROJECT_NAME)_ollama_data:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/$(BACKUP) -C /data; \
		echo "✅ Backup restaurado!"; \
	fi

# ===================================
# INFORMAÇÕES DO SISTEMA
# ===================================

info:
	@echo "ℹ️ Informações do sistema:"
	@echo "Docker version: $(shell docker --version)"
	@echo "Docker Compose version: $(shell docker compose version)"
	@echo "Containers ativos: $(shell docker ps -q | wc -l)"
	@echo "Images: $(shell docker images -q | wc -l)"
	@echo "Volumes: $(shell docker volume ls -q | wc -l)"
	@echo ""
	@echo "🔗 URLs importantes:"
	@echo "App Principal: http://localhost:8000"
	@echo "Ollama API: http://localhost:11434"
	@echo "MCP Provider: http://localhost:8001"

# Atualizar tudo
update:
	@echo "🔄 Atualizando sistema..."
	git pull
	docker compose -f $(COMPOSE_FILE) build --no-cache
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Sistema atualizado!"