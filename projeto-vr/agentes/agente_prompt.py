from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def gerar_prompt_join_arquivos(chave,df,arquivos_identificados):
    
    prompt_template = PromptTemplate(
        input_variables=["dados"],
        template="""
        Você é um engenheiro de prompt, especializado em prompt para sistemas de recursos humanos.


        Você vai receber **uma amostra** de arquivos da empresa para pagamento de vale refeição dos funcionários. A amostra contém:
        - índice do dataframe
        - nome do arquivo
        - info do DataFrame
        - colunas
        - total de linhas
        - primeiras 10 linhas

        E vai receber a lista dos arquivos dos funcionários que foram identifados, essa lista vai contar:
        - indice do arquivo;
        - nome do arquivo;
        - coluna de identificação do funcionário;
        - Nome das colunas que tem no arquivo;
        
        O prompt deverá obrigatoriamente ter o passo a passo para o agente desenvolvedor fazer um join nos arquivos:
        - Unir somente os arquivos identificados;
        - Usar a coluna de identificação que identifica os funcionários em cada arquivo;
        - Deverá obrigatoriamente utilizar o indice do arquivo para encontrar o arquivo;
        - Tomar os devidos cuidados para não repetir a matricula do funcionário;
        - Na admissão se ja tiver a matricula nos dados gerais somente atualize os dados do cargo e coloca a data da admissão
        - Cuidado no join pois sempre tem que prevalecer a lista completa dos funcionários que vão receber o VR;
        Deverá seguir as seguintes regras:
        - Excluir os funcionários de férias;
        - Excluir os funcionários suspensos;
        - Excluir os funcionários demitidos;
        - Excluir os funcionários estagiarios;
        - Excluir os funcionários aprendizes;


        Preciso obrigatoriamente das seguintes colunas:
        - Matricula do funcionário;
        - codigo da empresa;
        - Cargo do funcionario;
        - Data de admissao;
        - Situação do funcionario;
        - sindicato
        Não precisa criar funçoes e nem outros dados.
        Precisa somente unir os arquivos.
        

        IMPORTANTE:
        
        - Você não vai criar nenhum codigo.

        - Vai só criar o melhor prompt para resolver a tarefa.

        - O prompt vai ser enviado para um agente programador python para fazer um codigo python.

        - O agente programador deve ser capaz de elabora um codigo com o prompt que voce descreveu.

      
        Aqui esta a amostra do conjunto de dados:

        {dados}


        Lista dos arquivos identificados:
        {arquivos_identificados}
        """
        )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"dados": df, "arquivos_identificados":arquivos_identificados})
  

    return resposta.content