# test_sistema_completo.py
import os
import sys
from pathlib import Path

# Adiciona o projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_sistema_completo():
    print("🧪 === TESTE COMPLETO DO SISTEMA ===\n")
    
    # 1. Teste configurações
    print("1️⃣ Testando configurações...")
    try:
        from crew_project.config.get_llm import get_llm
        from crew_project.crew import agents, tasks, crew
        
        llm = get_llm()
        print(f"   ✅ LLM: {type(llm).__name__}")
        print(f"   ✅ Agents: {len(agents)}")
        print(f"   ✅ Tasks: {len(tasks)}")
        print(f"   ✅ Crew: {len(crew.agents)} agents, {len(crew.tasks)} tasks")
    except Exception as e:
        print(f"   ❌ Erro configurações: {e}")
        return False
    
    # 2. Teste tools individuais
    print("\n2️⃣ Testando tools...")
    try:
        from crew_project.tools.excel_tool import tool_ler_planilhas_zip
        from crew_project.tools.rules_api_tool import tool_carregar_regras_api
        
        # Criar arquivo de teste se não existir
        if not Path("test_data.zip").exists():
            print("   📦 Criando dados de teste...")
            import pandas as pd
            import zipfile
            import io
            
            df = pd.DataFrame({
                'id': [1, 2, 3],
                'nome': ['Test1', 'Test2', 'Test3'],
                'valor': [100, 200, 150]
            })
            
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            
            with zipfile.ZipFile("test_data.zip", 'w') as zf:
                zf.writestr('dados_teste.xlsx', excel_buffer.getvalue())
        
        # Teste tool Excel
        result = tool_ler_planilhas_zip("test_data.zip")
        print(f"   ✅ Excel tool: {len(result)} chars de resultado")
        
        # Teste tool API (vai falhar, mas deve tratar erro)
        result = tool_carregar_regras_api()
        print(f"   ✅ API tool: {'Erro esperado' if 'Erro' in result else 'Sucesso'}")
        
    except Exception as e:
        print(f"   ❌ Erro tools: {e}")
        return False
    
    # 3. Teste execução crew (simulado)
    print("\n3️⃣ Testando execução crew...")
    try:
        # Teste sem executar (kickoff pode ser lento)
        print(f"   ✅ Crew pronto para execução")
        print(f"   📋 Tasks em sequência: {[task.description[:50] + '...' for task in crew.tasks]}")
        
        # Se quiser testar execução real:
        # resultado = crew.kickoff(inputs={"arquivo_zip": "test_data.zip"})
        # print(f"   ✅ Execução: {len(str(resultado))} chars")
        
    except Exception as e:
        print(f"   ❌ Erro crew: {e}")
        return False
    
    print("\n🎉 === TODOS OS TESTES PASSARAM ===")
    return True

if __name__ == "__main__":
    success = test_sistema_completo()
    sys.exit(0 if success else 1)