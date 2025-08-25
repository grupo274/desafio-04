import requests
import logging
from crewai.tools import tool

logger = logging.getLogger(__name__)
MCP_RULES_URL = "http://mcp-provider:8000/rules"

@tool("carregar_regras_api")
def tool_carregar_regras_api() -> str:
    """Busca regras trabalhistas e contábeis de um MCP Provider (API REST)."""
    try:
        logger.info(f"🔍 Consultando regras em: {MCP_RULES_URL}")
        response = requests.get(MCP_RULES_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        obrigatorias = data.get("obrigatorias", [])
        regras = data.get("regras", [])
        
        result = (
            "📋 REGRAS TRABALHISTAS E CONTÁBEIS\n"
            "=" * 50 + "\n\n"
            "🔴 COLUNAS OBRIGATÓRIAS:\n" +
            "\n".join([f"  • {col}" for col in obrigatorias]) + "\n\n" +
            "📏 REGRAS APLICÁVEIS:\n" +
            "\n".join([f"  • {regra}" for regra in regras])
        )
        
        logger.info("✅ Regras carregadas com sucesso")
        return result
        
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Erro de conexão: Não foi possível conectar ao MCP Provider"
        logger.error(error_msg)
        return error_msg
    except requests.exceptions.Timeout:
        error_msg = "❌ Timeout: MCP Provider não respondeu em tempo hábil"
        logger.error(error_msg)
        return error_msg
    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ Erro HTTP {e.response.status_code}: {e.response.reason}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Erro inesperado ao acessar MCP Provider: {str(e)}"
        logger.error(error_msg)
        return error_msg
