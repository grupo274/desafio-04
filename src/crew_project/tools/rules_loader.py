import yaml
from crewai.tools import tool

@tool("rules_loader")
def carregar_regras(path: str = "src/crew_project/config/rules.yaml") -> str:
    """Carrega regras trabalhistas e contábeis de um arquivo YAML e retorna como string."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)
        obrigatorias = "\n".join(rules.get("obrigatorias", []))
        regras = "\n".join(rules.get("regras", []))
        return f"Colunas obrigatórias:\n{obrigatorias}\n\nRegras aplicáveis:\n{regras}"
    except Exception as e:
        return f"Erro ao carregar regras: {str(e)}"
