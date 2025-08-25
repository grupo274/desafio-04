import yaml
import os
import logging
from pathlib import Path
from crewai import Crew, Agent, Task, Process

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

def safe_get_llm():
    """Obtém LLM com tratamento de erro."""
    try:
        return get_llm()
    except Exception as e:
        logger.error(f"❌ Erro ao obter LLM: {e}")
        logger.info("🔄 Usando configuração padrão...")
        
        # Tentar Groq que está funcionando
        os.environ["LLM_PROVIDER"] = "groq"
        try:
            return get_llm()
        except:
            # Fallback final - string simples
            return "groq/llama-3.1-8b-instant"

def create_safe_agent(name, cfg, tools_list):
    """Cria agente com tratamento de erro."""
    try:
        return Agent(
            role=cfg.get("role", f"Agente {name}"),
            goal=cfg.get("goal", f"Executar tarefas de {name}"),
            backstory=cfg.get("backstory", f"Especialista em {name}"),
            llm=safe_get_llm(),
            verbose=cfg.get("verbose", True),
            memory=cfg.get("memory", False),
            tools=tools_list,
            allow_delegation=False,
        )
    except Exception as e:
        logger.error(f"❌ Erro criando agente {name}: {e}")
        # Retornar agente básico
        return Agent(
            role=f"Agente {name}",
            goal=f"Executar {name}",
            backstory=f"Assistente {name}",
            llm="groq/mixtral-8x7b-32768",  # String direta que funciona
            verbose=True,
            tools=[],  # Sem tools em caso de erro
        )

# Carregar configurações com tratamento de erro
try:
    agents_cfg = load_yaml("agents.yaml")
    tasks_cfg = load_yaml("tasks.yaml")
    logger.info("✅ Configurações carregadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro carregando configurações: {e}")
    # Configuração de fallback
    agents_cfg = {
        "extrator": {
            "role": "Especialista em Extração de Dados",
            "goal": "Extrair dados de arquivos",
            "backstory": "Especialista em processamento de dados",
            "verbose": True
        },
        "normalizador": {
            "role": "Especialista em Normalização",
            "goal": "Normalizar dados",
            "backstory": "Especialista em padronização",
            "verbose": True
        }
    }
    tasks_cfg = {
        "extracao": {
            "description": "Extrair dados do arquivo fornecido",
            "expected_output": "Dados extraídos com sucesso",
            "agent": "extrator"
        },
        "normalizacao": {
            "description": "Normalizar dados extraídos",
            "expected_output": "Dados normalizados",
            "agent": "normalizador"
        }
    }

# Criar instâncias de Agent com tratamento de erro
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
    tools_list = tools_config.get(name, [])
    agents[name] = create_safe_agent(name, cfg, tools_list)

# Criar instâncias de Task com tratamento de erro
tasks = {}
for name, cfg in tasks_cfg.items():
    try:
        agent_name = cfg.get("agent")
        if agent_name in agents:
            tasks[name] = Task(
                description=cfg.get("description", f"Executar task {name}"),
                expected_output=cfg.get("expected_output", f"Resultado de {name}"),
                agent=agents[agent_name],
            )
        else:
            logger.warning(f"⚠️ Agente '{agent_name}' não encontrado para task '{name}'")
    except Exception as e:
        logger.error(f"❌ Erro criando task {name}: {e}")

# Criar o Crew com tratamento de erro
try:
    crew = Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        verbose=True,
    )
    logger.info("✅ Crew criado com sucesso!")
    
except Exception as e:
    logger.error(f"❌ Erro criando crew: {e}")
    # Crew mínimo de fallback
    fallback_agent = Agent(
        role="Assistente Básico",
        goal="Manter aplicação funcionando",
        backstory="Agente de emergência",
        llm="groq/mixtral-8x7b-32768",
        verbose=True,
    )
    
    fallback_task = Task(
        description="Executar em modo seguro",
        expected_output="Aplicação rodando",
        agent=fallback_agent,
    )
    
    crew = Crew(
        agents=[fallback_agent],
        tasks=[fallback_task],
        process=Process.sequential,
        verbose=True,
    )
    logger.info("🆘 Crew de fallback criado")

# Função para executar com retry
def run_crew_safe():
    """Executa o crew com tratamento de erro."""
    try:
        logger.info("🚀 Iniciando execução do crew...")
        result = crew.kickoff()
        logger.info("✅ Crew executado com sucesso!")
        return result
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        return f"Execução falhou: {str(e)[:100]}... (mas aplicação continua rodando)"

if __name__ == "__main__":
    # Teste local
    result = run_crew_safe()
    print(f"Resultado: {result}")