from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate


def agrupar_arquivos(chave,df,comando,erro):
    
    prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="""
    Você é um agente programador Python com experiência em sistemas de recursos humanos. 

    Você vai receber um **prompt** com um passo a passo para fazer um join dos arquivos com os dados necessários para pagamamento de vale refeição dos funcionários.
    
    VocÊ vai receberr uma amostra dos arquivos que constam na variável 'lista_df' com esses dados:
        - índice do dataframe
        - nome do arquivo
        - info do DataFrame
        - colunas
        - total de linhas
        - dados (somente as primeiras 10 linhas)
    
    Faça somente o que foi descrito no prompt
    Você vai usar a variavel 'lista_df' que é uma lista de dicionarios que esta com os dados.

    Você usará a variável 'lista_df' que tem essa estrutura:
        - índice do arquivo (`indice_dataframe`)
        - nome do arquivo (`nome_arquivo`)
        - informações gerais (`info`)
        - dados do DataFrame (`dados`)

    Siga obrigatoriamente as seguintes regras:
    - Não precisa simular dados, todos os dados que vocÊ precisa ja estão em 'lista_df'
    - Não é para criar funções.
    - Faça o passo a passo descrito no prompt;
    - O dataframe final tem que obrigatoriamente ficar na variável 'df'
    - Use a biblioteca pandas para fazer a junção dos arquivos.
    - Gere apenas o **código Python necessário** para executar a tarefa. Não inclua explicações ou comentários.
  
    
    IMPORTANTE:
    A variável é uma lista de dicionarios, é preciso fazer a conversao para dataframe
    Prompt:
    {prompt}


    Amostra dos dados:
    {amostra}

    Pode ser que você ja tenha gerado o codigo e tenha dado erro.
    - se não tiver nenhum erro abaixo é por que é a primeira vez que esta executando o codigo
    Refaça todo o código e tente evitar o erro.

    Erro:
    {erro}
    Atenção nos erros:
    - Pode acontecer do nome da coluna de indentificação do funcionário não esteja padronizado;
    - Cuidado para não usar a estrutura da amostra, a estrutura que tem que usar é da base original que esta em 'lista_df"
    - Faça códigos simples para evitar errados;
    """
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"prompt":comando, "amostra":df, "erro":erro})
  

    return resposta.content