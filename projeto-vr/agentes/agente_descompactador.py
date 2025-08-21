'''
Este agente é responsável por baixar contedo do .zip a partir de uma URL, descompactar os arquivos e carregar os CSVs em DataFrames do Pandas.
Ler o conteúdo dos arquivos CSV em memória, sem salvar no disco, e retornar uma lista de DataFrames.
Decompactar os arquivos CSV de dentro do .zip e carregar os dados em DataFrames.
Retorna uma lista de DataFrames contendo os dados dos arquivos CSV encontrados.
'''
import os
import io
import zipfile
import tarfile
import requests
import pandas as pd
from io import BytesIO # Para ler dados binários em memória como um arquivo
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from pathlib import Path


def descompactar_arquivos(file_path: str):
    """
    Lê um arquivo .zip de uma URL ou de um caminho local,
    descompacta os arquivos XLSX em memória e retorna como lista de dicionários:
        - 'indice_dataframe': índice do arquivo no ZIP
        - 'nome_arquivo': nome do arquivo
        - 'info': informações do DataFrame (como df.info())
        - 'dados': o DataFrame em si
    """
    dataframes_xlsx = []

    print(f"📥 Buscando arquivo ZIP em: {file_path}")

    try:
        # Detecta se é URL ou caminho local
        if file_path.startswith("http://") or file_path.startswith("https://"):
            response = requests.get(file_path)
            response.raise_for_status()
            zip_file = BytesIO(response.content)
        else:
            zip_file = Path(file_path)

        # Abre o ZIP
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            arquivos_xlsx = [info for info in zip_ref.infolist()
                             if info.filename.lower().endswith('.xlsx') and not info.is_dir()]

            print(f"📊 Encontrados {len(arquivos_xlsx)} arquivos XLSX no ZIP.")

            for idx, info in enumerate(arquivos_xlsx):
                print(f"  ✅ Carregando: {info.filename}")
                with zip_ref.open(info.filename) as file:
                    df = pd.read_excel(file, engine="openpyxl")
                    
                    # Captura info do DataFrame como string
                    buffer = io.StringIO()
                    df.info(buf=buffer)
                    df_info = buffer.getvalue()
                    
                    # Adiciona ao dicionário
                    dataframes_xlsx.append({
                        'indice_dataframe': idx,
                        'nome_arquivo': info.filename,
                        'info': df_info,
                        'dados': df
                    })
                    
                    print(f"    - Linhas carregadas: {len(df)}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar o arquivo da URL: {e}")
        return []
    except FileNotFoundError:
        print(f"❌ Arquivo local não encontrado: {file_path}")
        return []
    except zipfile.BadZipFile:
        print("❌ O arquivo não é um ZIP válido ou está corrompido.")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return []

    return dataframes_xlsx



def preparar_amostras_para_agente(lista_de_dataframes_dict):
    """
    Prepara amostras dos DataFrames para envio a um agente.
    Recebe uma lista de dicionários com 'nome_arquivo', 'info' e 'dados' (DataFrame).
    Retorna uma lista de resumos contendo:
        - índice do dataframe
        - nome do arquivo
        - info do DataFrame
        - colunas
        - total de linhas
        - primeiras 10 linhas como string
    """
    amostras_para_agente = []
    
    for i, item in enumerate(lista_de_dataframes_dict):
        df = item['dados']  # pega o DataFrame real
        primeiras_linhas_str = df.head(10).to_string(index=False)
        
        amostra_info = {
            'indice_dataframe': i,
            'nome_arquivo': item['nome_arquivo'],
            'info': item['info'],  # info do DataFrame em string
            'colunas': df.columns.tolist(),
            'total_linhas': len(df),
            'primeiras_10_linhas': primeiras_linhas_str
        }
        
        amostras_para_agente.append(amostra_info)
    
    return amostras_para_agente



def agrupar_arquivos(chave,df):
 
    prompt_template = PromptTemplate(
        input_variables=["dados"],
        template="""
        Você é um agente agrupador de arquivos.

        Vai receber algumas uma lista das primeiras linhas de um conjunto de dados.
        Você vai desenvolver o codigo python para fazer um join entre os arquivos.
        Na coluna indice_dataframe tem o indice de cada dataframe
        Se não achar colunas iguais em todos arquivos para fazer o join voce pode só concatenar eles.
        
        O codigo deve necessariamente retornar um dataframe com o resultado do join ou do concant.
        
        Aqui esta os  dataframes:

        {dados}

        O nome da variavel da lista de datafremes é: lista_df


        """
        )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"dados": df})
  

    return resposta.content


def processar_arquivo_upload(lista_de_arquivos_upload):
    """
    Processa uma lista de arquivos CSV ou ZIP carregados pelo usuário.
    
    Args:
        lista_de_arquivos_upload (list): Lista de arquivos carregados pelo usuário.
        
    Returns:
        list: Uma lista de DataFrames do Pandas, um para cada arquivo CSV encontrado.
    """
    dataframes_csv = []
    if not lista_de_arquivos_upload:
        print("Nenhum arquivo carregado.")
        return []

    for uploaded_file in lista_de_arquivos_upload:
        file_name = uploaded_file.name
        print(f"Processando arquivo: {file_name}")
        
        try:
            # Verifica se o arquivo é um ZIP
            if file_name.lower().endswith('.zip'):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    for info in zip_ref.infolist():
                        # Pega todos os .csv em pastas e subpastas
                        if info.filename.lower().endswith('.csv') and not info.is_dir():
                            print(f" ✅ Encontrado CSV no ZIP: {info.filename}")
                            with zip_ref.open(info.filename) as file_in_zip:
                                df = pd.read_csv(file_in_zip)
                                dataframes_csv.append(df)
                                print(f"    - Carregando {info.filename} (linhas: {len(df)})")
            elif file_name.lower().endswith('.csv'):
                print(f"    ✅ Lendo arquivo CSV: {file_name}")
                df=pd.read_csv(uploaded_file)
                dataframes_csv.append(df)
                print(f"    - Carregado {file_name} (linhas: {len(df)})")
        except Exception as e:
            print(f"❌ Erro ao processar o arquivo {file_name}: {e}")
            raise e
        
    return dataframes_csv