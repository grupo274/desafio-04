import os
import io
import pandas as pd

import traceback
# from agentes import agente_prompt as prompt,agente_programador as programador, agente_descompactador as descompactador, agente_validador as validador

from agentes import agente_descompactador as descompactador
from agentes import agente_programador as programador
from agentes import agente_prompt as prompt
from agentes import agente_identificador as identificador

class Agente:
    def __init__(self):
        self.chave=''
        self.df=None

    def carrega_arquivos(self, chave, url=None, arquivos_carregados=None):
        # 👉 Coloque sua chave da API Gemini aqui:
        os.environ["GOOGLE_API_KEY"] = chave

        arquivos = []
        if url: 
            print(f"Iniciando download da URL: {url}")
            arquivos=descompactador.descompactar_arquivos(url)
        elif arquivos_carregados:
            print(f"Iniciando processamento de arquivos carregados.")
            arquivos = arquivos = descompactador.processar_arquivo_upload(arquivos_carregados)

        if not arquivos:
            raise ValueError("Nenhum arquivo CSV válido foi encontrado. Verifique a fonte dos dados e tente novamente.")
        
        #print(type(arquivos))
               
        amostras=descompactador.preparar_amostras_para_agente(arquivos)
        #print(amostras)

        arquivos_identificados= identificador.identificar_arquivos_funcionarios(chave=chave,df=amostras)
        #print(arquivos_identificados)
        
        comando=prompt.gerar_prompt_join_arquivos(chave=chave,df=amostras,arquivos_identificados=arquivos_identificados)
        print(comando)
        
        tentativas = 10
        self.df = None
        erro=''
        for tentativa in range(tentativas):
            try:
                # 1. Agente programador gera o código
                rest = programador.agrupar_arquivos(chave=os.environ["GOOGLE_API_KEY"], df=amostras, comando=comando, erro=erro)
                codigo_limpo = rest.strip("```").replace("python", "").strip()

                # 2. Agente revisor tenta rodar
                exec_globals = {"pd": pd}
                exec_locals = {"lista_df": arquivos}

                exec(codigo_limpo, exec_globals, exec_locals)

                self.df = exec_locals.get("df")

                if self.df is not None:
                    print("✅ Código funcionou")
                    break

            except Exception as e:
                erro = traceback.format_exc()
                print(f"⚠️ Erro detectado pelo revisor! tentando novamente!")

    
        else:
            print("❌ Nenhuma tentativa funcionou")


        print (rest)




        print ("#### dataset final")
        print(self.df.head())

        print (self.df.info())

        self.df.to_excel("resultado_funcionarios.xlsx", index=False)
        print("Arquivo 'resultado_funcionarios.xlsx' gerado com sucesso!")

        