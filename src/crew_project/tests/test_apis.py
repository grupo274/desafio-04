#!/usr/bin/env python3
"""
Script para testar API Keys dos diferentes provedores LLM
"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_openai_key():
    """Testa a API Key do OpenAI."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada no .env")
            return False
            
        print(f"🔑 Testando OpenAI key: {api_key[:10]}...")
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI key válida!")
        return True
        
    except Exception as e:
        print(f"❌ Erro OpenAI: {e}")
        return False


def test_groq_key():
    """Testa a API Key do Groq."""
    try:
        import requests
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY não encontrada no .env")
            return False
            
        print(f"🔑 Testando Groq key: {api_key[:10]}...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "mixtral-8x7b-32768",
            "max_tokens": 5
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Groq key válida!")
            return True
        else:
            print(f"❌ Groq erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro Groq: {e}")
        return False


def test_gemini_key():
    """Testa a API Key do Google Gemini."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY não encontrada no .env")
            return False
            
        print(f"🔑 Testando Gemini key: {api_key[:10]}...")
        
        genai.configure(api_key=api_key)
        
        # Lista modelos disponíveis para testar a key
        models = list(genai.list_models())
        if models:
            print("✅ Gemini key válida!")
            print(f"📋 Modelos disponíveis: {len(models)}")
            return True
        else:
            print("❌ Gemini key inválida ou sem modelos")
            return False
            
    except Exception as e:
        print(f"❌ Erro Gemini: {e}")
        return False


def test_litellm_integration():
    """Testa integração com LiteLLM."""
    try:
        import litellm
        
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        print(f"🧪 Testando LiteLLM com provider: {provider}")
        
        if provider == "openai":
            model = "gpt-3.5-turbo"
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider == "groq":
            model = "groq/mixtral-8x7b-32768"
            api_key = os.getenv("GROQ_API_KEY")
        elif provider == "gemini":
            model = "gemini/gemini-pro"
            api_key = os.getenv("GOOGLE_API_KEY")
        else:
            print(f"❌ Provider {provider} não suportado no teste")
            return False
            
        if not api_key:
            print(f"❌ API key não encontrada para {provider}")
            return False
            
        # Configurar variável de ambiente para o provider
        if provider == "groq":
            os.environ["GROQ_API_KEY"] = api_key
        elif provider == "gemini":
            os.environ["GOOGLE_API_KEY"] = api_key
        elif provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
            
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ LiteLLM integração funcionando!")
        print(f"📝 Resposta: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Erro LiteLLM: {e}")
        return False


def main():
    """Executa todos os testes de API."""
    print("🚀 Testando API Keys...\n")
    
    # Mostrar configuração atual
    provider = os.getenv("LLM_PROVIDER", "openai")
    print(f"📋 Provider configurado: {provider}")
    print(f"📋 Arquivo .env carregado: {os.path.exists('.env')}\n")
    
    results = {}
    
    # Testar todas as keys
    print("=" * 50)
    print("TESTANDO APIS INDIVIDUAIS")
    print("=" * 50)
    
    results['openai'] = test_openai_key()
    print()
    
    results['groq'] = test_groq_key()
    print()
    
    results['gemini'] = test_gemini_key()
    print()
    
    print("=" * 50)
    print("TESTANDO INTEGRAÇÃO LITELLM")
    print("=" * 50)
    
    results['litellm'] = test_litellm_integration()
    print()
    
    # Resumo
    print("=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    for service, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {service.upper()}: {'OK' if status else 'FALHA'}")
    
    # Sugestões
    print("\n" + "=" * 50)
    print("SUGESTÕES")
    print("=" * 50)
    
    if not any(results.values()):
        print("⚠️  Nenhuma API key está funcionando!")
        print("1. Verifique se o arquivo .env está na raiz do projeto")
        print("2. Verifique se as keys estão corretas")
        print("3. Teste com curl/postman para confirmar")
    
    working_apis = [api for api, status in results.items() if status and api != 'litellm']
    if working_apis:
        print(f"💡 APIs funcionando: {', '.join(working_apis)}")
        print(f"💡 Configure LLM_PROVIDER para: {working_apis[0]}")
    
    return results


if __name__ == "__main__":
    main()