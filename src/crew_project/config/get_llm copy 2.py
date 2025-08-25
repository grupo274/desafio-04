import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatLlamaCpp
from langchain_groq import ChatGroq

def get_llm():
    """Retorna instância do LLM baseado na variável de ambiente LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    temperature = float(os.getenv("LLM_TEMPERATURE", 0))
    
    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),  # Removido prefixo
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
        )
    
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-exp"),  # Modelo correto
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=temperature,
        )
    
    elif provider == "llama":
        return ChatLlamaCpp(
            model_path=os.getenv("LLAMA_MODEL_PATH", "/models/llama-3.1-8b-instruct.Q4_K_M.gguf"),
            temperature=temperature,
        )
    
    elif provider == "groq":
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),  # Removido prefixo
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=temperature,
        )
    
    else:
        raise ValueError(
            f"Provider {provider} não suportado. Use: openai, gemini, llama, groq"
        )