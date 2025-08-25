import yaml
import os
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

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"

def load_yaml(filename):
    """Carrega arquivo YAML de configuração."""
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Carregar configurações
try:
    agents_cfg = load_yaml("agents.yaml")
    tasks_cfg = load_yaml("tasks.yaml")
except FileNotFoundError as e:
    raise RuntimeError(f"Erro ao carregar configurações: {e}")

# Criar instâncias de Agent
agents = {}
for name, cfg in agents_cfg.items():
    """
    agents[name] = Agent(
        role=cfg.get("role"),
        goal=cfg.get("goal"),
        backstory=cfg.get("backstory"),
        llm=get_llm(),
        verbose=cfg.get("verbose", False),
        memory=cfg.get("memory", False),
        tools=[],  # configurado abaixo
    )
    """
    print(f"LLM Provider: {os.getenv('LLM_PROVIDER')}")
    print(f"LLM retornado: {get_llm()}")

    # Criar o Agent com debug
    agents[name] = Agent(
        role=cfg.get("role"),
        goal=cfg.get("goal"),
        backstory=cfg.get("backstory"),
        llm=get_llm(),
        verbose=True,  # Ativar verbose para debug
        memory=cfg.get("memory", False),
        tools=[],
    )



# Configurar tools por agente
tools_config = {
    "extrator": [
        tool_ler_planilhas_zip,
        tool_descompactar_arquivos,
        tool_preparar_amostras_para_agente,
    ],
    "normalizador": [
        tool_carregar_regras_api
    ],
    "contador": [
        tool_carregar_regras_api,
        tool_fazer_join_ou_concat,
        tool_sugerir_codigo_agrupamento,
    ],
    "auditor": [
        tool_carregar_regras_api
    ]
}

for agent_name, tools_list in tools_config.items():
    if agent_name in agents:
        agents[agent_name].tools = tools_list

# Criar instâncias de Task
tasks = {}
for name, cfg in tasks_cfg.items():
    if cfg.get("agent") not in agents:
        raise ValueError(f"Agente '{cfg.get('agent')}' não encontrado para task '{name}'")
    
    tasks[name] = Task(
        description=cfg.get("description"),
        expected_output=cfg.get("expected_output"),
        agent=agents[cfg.get("agent")],
    )

# Criar o Crew
crew = Crew(
    agents=list(agents.values()),
    tasks=list(tasks.values()),
    process=Process.sequential,
)