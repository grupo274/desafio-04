# crew_project/config/get_llm.py
import os
from crewai import LLM

def get_llm():
    """
    Retorna configuração de LLM com fallback para desenvolvimento
    """
    
    # Opção 1: Tentar usar OpenAI se tiver API key
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            return LLM(
                model="gpt-4o-mini",  # Modelo mais barato
                api_key=openai_key
            )
        except Exception as e:
            print(f"⚠️ Erro ao configurar OpenAI: {e}")
    """
    # Opção 1.5: Tentar Groq (gratuito com limites)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            return LLM(
                model="groq/llama3-8b-8192",
                api_key=groq_key
            )
        except Exception as e:
            print(f"⚠️ Erro ao configurar Groq: {e}")
    
    # Opção 2: Usar Ollama local (RECOMENDADO para desenvolvimento)
    """
    try:
        model_name = os.getenv("LLAMA_MODEL", "custom-llama")
        return LLM(
            model=f"ollama/{model_name}",
            base_url="http://ollama:11434"
        )
    except Exception:
        print("⚠️ Ollama não disponível")
    """
    # Opção 3: Mock LLM para testes (último recurso)
    return MockLLM()

class MockLLM:
    """LLM simulado para desenvolvimento sem API externa"""
    
    def __call__(self, prompt, **kwargs):
        return f"[MOCK RESPONSE] Processado: {prompt[:100]}..."
    
    def invoke(self, messages, **kwargs):
        if isinstance(messages, list):
            content = messages[-1].get('content', 'No content') if messages else 'Empty'
        else:
            content = str(messages)[:100]
        
        return f"[MOCK] Resposta simulada para: {content}..."