from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def identificar_arquivos_funcionarios(chave,df):
    
    prompt_template = PromptTemplate(
        input_variables=["dados"],
        template="""
        Você é um agente identificador de arquivos.


        Você vai receber **uma amostra** de arquivos da empresa para pagamento de vale refeição dos funcionários. A amostra contém:
        - índice do dataframe
        - nome do arquivo
        - info do DataFrame
        - colunas
        - total de linhas
        - primeiras 10 linhas

        
        Você deverá odentificar os arquivos que contem os dados dos funcionários.
        Dentro da lista de arquivos você deve identiciar:
        - Qual arquivo esta a lista de funcionários ativos;
        - Qual arquivo esta a lista de funcionários que está de ferias;
        - Qual arquivo esta a lista de funcionários demitidos;
        - Qual arquivo esta a lista de funcionários afastados;
        - Qual arquivo esta a lista de funcionários que estão no exterior;
        - Qual arquivo esta a lista de estagiarios;
        - Qual arquivo esta a lista de aprendizers;
        - Qual arquivo esta a lista de admissês do mês;


        Você deverá me retornar obrigatoriamente:
        - indice do arquivo;
        - Nome do arquivo;
        - Qual coluna do arquivo identifica o funcionário;
        - Nome das colunas colunas que tem no arquivo;

        CUIDADO:
        - Dentro da lista pode ser que esteja o arquivo que a empresa usa para unir os arquivos. pode evitar esse arquivo.
        - Retorne somente o que foi solicitado;
        Aqui esta a amostra do conjunto de dados:

        {dados}


  
        """
        )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"dados": df})
  

    return resposta.content