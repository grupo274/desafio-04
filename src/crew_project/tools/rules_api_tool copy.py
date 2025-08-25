import requests
from crewai.tools import tool

MCP_RULES_URL = "http://mcp-provider:8000/rules"

@tool("rules_api_tool")
def carregar_regras_api() -> str:
    """Busca regras trabalhistas e contábeis de um MCP Provider (API REST)."""
    try:
        response = requests.get(MCP_RULES_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        obrigatorias = "\n".join(data.get("obrigatorias", []))
        regras = "\n".join(data.get("regras", []))
        return f"Colunas obrigatórias:\n{obrigatorias}\n\nRegras aplicáveis:\n{regras}"
    except Exception as e:
        return f"Erro ao acessar MCP Provider: {str(e)}"

@tool("carregar_regras_api")
def tool_carregar_regras_api(url: str = None):
    """Carrega regras de normalização a partir de uma API externa."""
    return carregar_regras_api(url)