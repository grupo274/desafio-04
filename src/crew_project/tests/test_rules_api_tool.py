# test_rules_api_tool.py
from unittest.mock import patch, Mock
from crew_project.tools.rules_api_tool import tool_carregar_regras_api

def test_rules_api_success():
    """Testa API com resposta simulada de sucesso."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "obrigatorias": ["funcionario_id", "valor_refeicao", "data"],
        "regras": ["Valor máximo R$ 25,00", "Apenas dias úteis"]
    }
    
    with patch('requests.get', return_value=mock_response):
        try:
            result = tool_carregar_regras_api()
            print("✅ Tool API (simulado) executado com sucesso!")
            print("📋 Resultado:")
            print(result)
            return True
        except Exception as e:
            print(f"❌ Erro no tool API: {e}")
            return False

def test_rules_api_failure():
    """Testa comportamento com falha de API."""
    with patch('requests.get', side_effect=Exception("Connection failed")):
        try:
            result = tool_carregar_regras_api()
            print("✅ Tratamento de erro da API funcionando:")
            print(result)
            return True
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

if __name__ == "__main__":
    print("=== Teste API Sucesso ===")
    test_rules_api_success()
    print("\n=== Teste API Falha ===")
    test_rules_api_failure()