# test_dataframe_tools.py
import pandas as pd
from crew_project.tools.dataframe_tool import (
    descompactar_arquivos, 
    preparar_amostras_para_agente,
    fazer_join_ou_concat
)

def test_dataframe_tools():
    # Criar DataFrames de teste
    df1 = pd.DataFrame({
        'id': [1, 2, 3],
        'nome': ['João', 'Maria', 'Pedro'],
        'valor': [100, 200, 150]
    })
    
    df2 = pd.DataFrame({
        'id': [1, 2, 4],
        'departamento': ['TI', 'RH', 'Vendas'],
        'salario': [5000, 4500, 3000]
    })
    
    # Teste: Join por coluna comum (id)
    print("=== Teste JOIN ===")
    try:
        df_joined = fazer_join_ou_concat([df1, df2], how='outer')
        print(f"✅ Join realizado: {len(df_joined)} linhas")
        print(df_joined.to_string())
        print()
    except Exception as e:
        print(f"❌ Erro no join: {e}")
    
    # Teste: Concat sem colunas comuns
    print("=== Teste CONCAT ===")
    df3 = pd.DataFrame({
        'produto': ['A', 'B', 'C'],
        'preco': [10, 20, 15]
    })
    
    try:
        df_concat = fazer_join_ou_concat([df1, df3])
        print(f"✅ Concat realizado: {len(df_concat)} linhas")
        print(df_concat.head().to_string())
    except Exception as e:
        print(f"❌ Erro no concat: {e}")
    
    # Teste: Preparar amostras
    print("\n=== Teste AMOSTRAS ===")
    dados_dict = [
        {"indice_dataframe": 0, "nome_arquivo": "teste1.xlsx", "dados": df1},
        {"indice_dataframe": 1, "nome_arquivo": "teste2.xlsx", "dados": df2}
    ]
    
    try:
        amostras = preparar_amostras_para_agente(dados_dict)
        print(f"✅ Amostras preparadas: {len(amostras)} itens")
        for amostra in amostras:
            print(f"  📄 {amostra['nome_arquivo']}: {amostra['total_linhas']} linhas")
    except Exception as e:
        print(f"❌ Erro nas amostras: {e}")

if __name__ == "__main__":
    test_dataframe_tools()