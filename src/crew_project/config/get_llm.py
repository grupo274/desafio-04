import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatLlamaCpp
from langchain_groq import ChatGroq
from litellm import completion


def get_llm_litellm():
    """Retorna configuração para LiteLLM (usado pelo CrewAI)."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", 0))
        }
    elif provider == "gemini":
        return {
            "model": "gemini/gemini-2.0-flash",  # Formato LiteLLM correto
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", 0))
        }
    elif provider == "groq":
        return {
            "model": "groq/mixtral-8x7b-32768",
            "api_key": os.getenv("GROQ_API_KEY"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", 0))
        }
    else:
        raise ValueError(f"Provider {provider} não suportado para LiteLLM")


def get_llm():
    """Retorna instância do LLM baseado na variável de ambiente LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    temperature = float(os.getenv("LLM_TEMPERATURE", 0))
    
    # Para CrewAI, usar string do modelo no formato LiteLLM
    if provider == "openai":
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
        return "gpt-4o-mini"
        
    elif provider == "gemini":
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
        return "gemini/gemini-2.0-flash-exp"
        
    elif provider == "groq":
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
        return "groq/mixtral-8x7b-32768"
        
    else:
        raise ValueError(f"Provider {provider} não suportado")