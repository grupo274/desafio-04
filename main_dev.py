# main_dev.py - Versão para testar sem LLM
import os
from pathlib import Path

def test_tools_directly():
    """Testa as ferramentas diretamente sem usar o CrewAI"""
    
    from crew_project.tools.excel_tool import tool_ler_planilhas_zip
    from crew_project.tools.dataframe_tool import tool_descompactar_arquivos
    
    arquivo_zip = "dados/vales_refeicao.zip"
    
    print("🧪 Testando ferramentas diretamente...")
    
    # Testar ferramenta de leitura de ZIP
    try:
        print("\n1. Testando leitura do ZIP...")
        resultado_zip = tool_ler_planilhas_zip.run(arquivo_zip)
        print(f"✅ ZIP lido com sucesso: {len(resultado_zip)} caracteres")
        print(f"Primeiros 200 caracteres: {resultado_zip[:200]}...")
        
    except Exception as e:
        print(f"❌ Erro ao ler ZIP: {e}")
        return
    
    # Testar descompactação
    try:
        print("\n2. Testando descompactação...")
        resultado_descomp = tool_descompactar_arquivos.run(arquivo_zip)
        print(f"✅ Descompactação ok: {len(resultado_descomp)} caracteres")
        
    except Exception as e:
        print(f"❌ Erro na descompactação: {e}")
        return
    
    print("\n🎉 Ferramentas funcionando! Agora você pode configurar o LLM.")

def test_with_mock_crew():
    """Testa com CrewAI mas usando Mock LLM"""
    
    # Forçar uso do Mock LLM
    os.environ['FORCE_MOCK_LLM'] = 'true'
    
    from crew_project.crew import crew
    
    try:
        print("🧪 Testando com Mock LLM...")
        resultado = crew.kickoff(inputs={"arquivo_zip": "dados/vales_refeicao.zip"})
        print(f"✅ Crew executou com sucesso!")
        print(f"Resultado: {resultado}")
        
    except Exception as e:
        print(f"❌ Erro no Crew: {e}")

if __name__ == "__main__":
    print("=== MODO DE DESENVOLVIMENTO ===\n")
    
    # Escolher o que testar
    modo = input("Escolha: (1) Testar ferramentas diretamente (2) Testar com Mock LLM: ")
    
    if modo == "1":
        test_tools_directly()
    elif modo == "2":
        test_with_mock_crew()
    else:
        print("Opção inválida")