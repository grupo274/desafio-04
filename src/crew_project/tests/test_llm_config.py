# test_llm_config.py
from crew_project.config.get_llm import get_llm

def test_llm_config():
    try:
        llm = get_llm()
        print(f"✅ LLM configurado: {type(llm).__name__}")
        
        # Teste básico de resposta
        response = llm.invoke("Responda apenas: OK")
        content = getattr(response, 'content', str(response))
        print(f"✅ Resposta LLM: {content}")
        return True
    except Exception as e:
        print(f"❌ Erro LLM: {e}")
        return False

if __name__ == "__main__":
    test_llm_config()