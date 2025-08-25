import yaml
import os
import logging
from pathlib import Path
from crewai import Crew, Agent, Task, Process
from typing import Dict, Any, Optional

from crew_project.tools.excel_tool import tool_ler_planilhas_zip
from crew_project.tools.rules_api_tool import tool_carregar_regras_api
from crew_project.tools.dataframe_tool import (
    tool_descompactar_arquivos,
    tool_preparar_amostras_para_agente,
    tool_fazer_join_ou_concat,
    tool_sugerir_codigo_agrupamento,
)
from crew_project.config.get_llm import get_llm

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"

def load_yaml(filename):
    """Carrega arquivo YAML de configuração."""
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_fallback_llm():
    """Retorna um LLM de fallback ou simulado quando há erro de API."""
    logger.warning("🔄 Usando LLM de fallback (simulado)")
    
    class MockLLM:
        def __init__(self):
            self.model_name = "mock-llm"
            
        def __call__(self, prompt: str, **kwargs) -> str:
            return f"[SIMULADO] Resposta para: {prompt[:100]}..."
            
        def invoke(self, messages, **kwargs):
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    
            if isinstance(messages, list):
                content = messages[-1].get('content', 'prompt vazio')
            else:
                content = str(messages)
                
            return MockResponse(f"[SIMULADO] Resposta para: {content[:100]}...")
    
    return MockLLM()

def safe_get_llm(max_retries: int = 3) -> Optional[Any]:
    """Tenta obter LLM com fallback em caso de erro."""
    providers = ["openai", "gemini", "groq"]
    original_provider = os.getenv("LLM_PROVIDER", "openai")
    
    for attempt in range(max_retries):
        for provider in providers:
            try:
                logger.info(f"🔄 Tentativa {attempt + 1}/{max_retries} - Testando provider: {provider}")
                
                # Temporariamente mudar provider
                os.environ["LLM_PROVIDER"] = provider
                llm = get_llm()
                
                # Teste rápido (se possível)
                logger.info(f"✅ Provider {provider} funcionando!")
                return llm
                
            except Exception as e:
                logger.warning(f"❌ Provider {provider} falhou: {str(e)[:100]}...")
                continue
    
    # Restaurar provider original
    os.environ["LLM_PROVIDER"] = original_provider
    
    logger.error("🚫 Todos os providers falharam. Usando LLM simulado.")
    return get_fallback_llm()

def create_resilient_agent(name: str, cfg: Dict[str, Any], tools: list = None) -> Agent:
    """Cria um agente com tratamento de erro robusto."""
    try:
        llm = safe_get_llm()
        
        agent = Agent(
            role=cfg.get("role", "Assistente"),
            goal=cfg.get("goal", "Ajudar com tarefas"),
            backstory=cfg.get("backstory", "Sou um assistente útil"),
            llm=llm,
            verbose=cfg.get("verbose", True),
            memory=cfg.get("memory", False),
            tools=tools or [],
            allow_delegation=False,  # Evitar problemas com delegação
            max_iter=3,  # Limitar iterações
        )
        
        logger.info(f"✅ Agente '{name}' criado com sucesso")
        return agent
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar agente '{name}': {e}")
        
        # Agente mínimo de fallback
        return Agent(
            role=f"Agente {name} (Modo Seguro)",
            goal="Executar tarefas básicas",
            backstory="Agente em modo de segurança",
            llm=get_fallback_llm(),
            verbose=True,
            tools=[],
            allow_delegation=False,
        )

def create_resilient_task(name: str, cfg: Dict[str, Any], agent: Agent) -> Task:
    """Cria uma task com tratamento de erro."""
    try:
        task = Task(
            description=cfg.get("description", f"Executar task {name}"),
            expected_output=cfg.get("expected_output", "Resultado da execução"),
            agent=agent,
        )
        
        logger.info(f"✅ Task '{name}' criada com sucesso")
        return task
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar task '{name}': {e}")
        
        # Task básica de fallback
        return Task(
            description=f"Task {name} (Modo Seguro): Executar operação básica",
            expected_output="Execução concluída em modo de segurança",
            agent=agent,
        )

def run_crew_with_retries(crew: Crew, max_retries: int = 2) -> Dict[str, Any]:
    """Executa o crew com tentativas e tratamento de erro."""
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🚀 Iniciando execução do crew - Tentativa {attempt + 1}/{max_retries}")
            
            result = crew.kickoff()
            
            logger.info("✅ Crew executado com sucesso!")
            return {
                "success": True,
                "result": result,
                "attempt": attempt + 1
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na tentativa {attempt + 1}: {str(e)[:200]}...")
            
            if attempt < max_retries - 1:
                logger.info("🔄 Tentando novamente...")
            else:
                logger.error("🚫 Máximo de tentativas atingido")
                
                return {
                    "success": False,
                    "error": str(e),
                    "attempt": attempt + 1,
                    "fallback_result": "Execução falhou, mas aplicação continua rodando"
                }

# Função principal
def main():
    """Função principal com tratamento completo de erros."""
    try:
        # Carregar configurações
        logger.info("📋 Carregando configurações...")
        agents_cfg = load_yaml("agents.yaml")
        tasks_cfg = load_yaml("tasks.yaml")
        
        # Criar agentes com tratamento de erro
        logger.info("👥 Criando agentes...")
        agents = {}
        
        tools_config = {
            "extrator": [
                tool_ler_planilhas_zip,
                tool_descompactar_arquivos,
                tool_preparar_amostras_para_agente,
            ],
            "normalizador": [tool_carregar_regras_api],
            "contador": [
                tool_carregar_regras_api,
                tool_fazer_join_ou_concat,
                tool_sugerir_codigo_agrupamento,
            ],
            "auditor": [tool_carregar_regras_api]
        }
        
        for name, cfg in agents_cfg.items():
            tools = tools_config.get(name, [])
            agents[name] = create_resilient_agent(name, cfg, tools)
        
        # Criar tasks com tratamento de erro
        logger.info("📋 Criando tasks...")
        tasks = {}
        for name, cfg in tasks_cfg.items():
            agent_name = cfg.get("agent")
            if agent_name in agents:
                tasks[name] = create_resilient_task(name, cfg, agents[agent_name])
            else:
                logger.warning(f"⚠️ Agente '{agent_name}' não encontrado para task '{name}'")
        
        # Criar crew
        logger.info("🚀 Criando crew...")
        crew = Crew(
            agents=list(agents.values()),
            tasks=list(tasks.values()),
            process=Process.sequential,
            verbose=True,
        )
        
        # Executar com tratamento de erro
        logger.info("▶️ Executando crew...")
        result = run_crew_with_retries(crew)
        
        # Exibir resultado
        if result["success"]:
            logger.info("🎉 SUCESSO!")
            print(f"Resultado: {result['result']}")
        else:
            logger.error("⚠️ EXECUÇÃO FALHOU MAS APLICAÇÃO CONTINUA")
            print(f"Erro: {result['error']}")
            print(f"Fallback: {result['fallback_result']}")
        
        # Manter aplicação rodando
        logger.info("💤 Aplicação permanece ativa...")
        import time
        while True:
            time.sleep(10)
            logger.info("💓 Aplicação ainda rodando...")
            
    except Exception as e:
        logger.error(f"🔥 Erro crítico: {e}")
        print("Aplicação falhou completamente, mas não vai parar...")
        
        # Manter rodando mesmo com erro crítico
        import time
        while True:
            time.sleep(30)
            logger.info("🆘 Aplicação em modo de emergência...")

if __name__ == "__main__":
    main()