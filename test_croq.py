#!/usr/bin/env python3
"""
Teste manual da API do Groq
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_groq_direct():
    """Teste direto da API Groq com curl-like request."""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY não encontrada no .env")
        #print("📋 Adicione no .env: GROQ_API_KEY")
        return False
    
    print(f"🔑 Testando key: {api_key[:15]}...{api_key[-5:]}")
    print(f"📏 Tamanho da key: {len(api_key)} caracteres")
    
    # Headers para a requisição
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Python-Test-Script"
    }
    
    # Payload mínimo
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello"}
        ],
        "model": "llama-3.1-8b-instant",
        "temperature": 0,
        "max_tokens": 10
    }
    
    print("\n🌐 Fazendo requisição para Groq API...")
    print(f"🎯 Endpoint: https://api.groq.com/openai/v1/chat/completions")
    print(f"📝 Model: {payload['model']}")
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO!")
            print(f"💬 Resposta: {data['choices'][0]['message']['content']}")
            print(f"🏷️ Modelo usado: {data.get('model', 'N/A')}")
            print(f"🔢 Tokens: {data.get('usage', {})}")
            return True
            
        elif response.status_code == 401:
            print("❌ ERRO 401: API Key inválida")
            print("🔧 Soluções:")
            print("   1. Verifique se a key está correta")
            print("   2. Gere uma nova key em https://console.groq.com/keys")
            print("   3. Verifique se não há espaços em branco na key")
            return False
            
        elif response.status_code == 429:
            print("❌ ERRO 429: Rate limit excedido")
            print("⏱️ Aguarde um pouco e tente novamente")
            return False
            
        else:
            print(f"❌ ERRO {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Requisição demorou muito")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO: Não foi possível conectar à API")
        return False
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

def validate_key_format():
    """Valida o formato da chave."""
    api_key = os.getenv("GROQ_API_KEY", "")
    
    print("🔍 Validando formato da chave...")
    
    if not api_key:
        print("❌ Chave não encontrada")
        return False
    
    # Groq keys geralmente começam com "gsk_"
    if not api_key.startswith("gsk_"):
        print(f"⚠️ Chave não parece ser do Groq (não começa com 'gsk_')")
        print(f"📋 Chave atual começa com: {api_key[:10]}...")
    else:
        print("✅ Formato da chave parece correto")
    
    # Verificar tamanho (Groq keys têm ~56 caracteres)
    if len(api_key) < 40:
        print(f"⚠️ Chave muito curta ({len(api_key)} chars). Groq keys têm ~56 chars")
    elif len(api_key) > 70:
        print(f"⚠️ Chave muito longa ({len(api_key)} chars). Groq keys têm ~56 chars")
    else:
        print(f"✅ Tamanho da chave OK ({len(api_key)} chars)")
    
    # Verificar caracteres especiais
    if ' ' in api_key:
        print("❌ Chave contém espaços!")
        return False
    
    if api_key != api_key.strip():
        print("❌ Chave tem espaços no início/fim!")
        return False
    
    return True

def main():
    print("🧪 TESTE DA API GROQ")
    print("=" * 50)
    
    # Verificar arquivo .env
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
    else:
        print("❌ Arquivo .env não encontrado na raiz do projeto")
        return
    
    # Validar formato
    if not validate_key_format():
        print("\n🔧 Corrija o formato da chave antes de continuar")
        return
    
    print("\n" + "=" * 50)
    
    # Testar API
    success = test_groq_direct()
    
    print("\n" + "=" * 50)
    print("RESULTADO FINAL")
    print("=" * 50)
    
    if success:
        print("🎉 Groq API está funcionando!")
        print("✅ Pode usar: LLM_PROVIDER=groq")
    else:
        print("❌ Groq API não está funcionando")
        print("🔧 Soluções:")
        print("   1. Gere nova chave em: https://console.groq.com/keys")
        print("   2. Verifique se tem créditos/cota disponível")
        print("   3. Tente outro modelo: llama-3.1-8b-instant")

if __name__ == "__main__":
    main()