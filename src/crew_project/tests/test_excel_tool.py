# test_excel_tool.py
import pandas as pd
import zipfile
import io
from crew_project.tools.excel_tool import tool_ler_planilhas_zip

def create_test_zip():
    """Cria um ZIP de teste com arquivo Excel."""
    # Criar DataFrame de exemplo
    df = pd.DataFrame({
        'funcionario_id': [1, 2, 3, 4, 5],
        'nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos'],
        'valor_refeicao': [15.50, 18.00, 16.75, 17.25, 15.80]
    })
    
    # Salvar em Excel na memória
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    # Criar ZIP na memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('vales_teste.xlsx', excel_buffer.getvalue())
    
    # Salvar arquivo de teste
    with open('test_data.zip', 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print("✅ Arquivo de teste criado: test_data.zip")

def test_excel_tool():
    create_test_zip()
    
    try:
        result = tool_ler_planilhas_zip("test_data.zip")
        print("✅ Tool Excel executado com sucesso!")
        print("📄 Resultado:")
        print(result[:500] + "..." if len(result) > 500 else result)
        return True
    except Exception as e:
        print(f"❌ Erro no tool Excel: {e}")
        return False

if __name__ == "__main__":
    test_excel_tool()