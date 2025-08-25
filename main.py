import os
import pandas as pd
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent

# Definição do LLM (o Docker vai passar a sua chave API)
llm = ChatOpenAI(model="gpt-4o")

# --- Dados de Exemplo para Simulação ---
# NOTA: Na implementação real, esta parte seria a leitura das tuas 5 planilhas.
base_ativa = pd.DataFrame([
    {'matricula': '101', 'nome': 'Ana Silva', 'cargo': 'Analista', 'sindicato': 'Sindicato A', 'dias_uteis_sind': 22, 'salario': 5000},
    {'matricula': '102', 'nome': 'Pedro Rocha', 'cargo': 'Diretor', 'sindicato': 'Sindicato B', 'dias_uteis_sind': 21, 'salario': 15000},
    {'matricula': '103', 'nome': 'Maria Lima', 'cargo': 'Gerente', 'sindicato': 'Sindicato A', 'dias_uteis_sind': 22, 'salario': 8000},
])

base_ferias = pd.DataFrame([
    {'matricula': '103', 'nome': 'Maria Lima', 'inicio_ferias': '2025-05-10', 'fim_ferias': '2025-05-20'},
])

base_desligados = pd.DataFrame([
    {'matricula': '101', 'nome': 'Ana Silva', 'desligamento': '2025-05-16', 'comunicado_ok': 'sim'},
])

base_sindicato_valor = pd.DataFrame([
    {'sindicato': 'Sindicato A', 'vr_valor': 30.00},
    {'sindicato': 'Sindicato B', 'vr_valor': 35.00},
])

# --- Agentes ---
agente_dados = Agent(
    role='Especialista em Tratamento de Dados e Consolidação',
    goal='Consolidar e limpar bases de dados, garantindo que estão prontas para o cálculo de benefícios.',
    backstory='Um analista meticuloso que domina a manipulação e a unificação de grandes volumes de dados de diferentes fontes.',
    verbose=True,
    llm=llm
)

analista_regras = Agent(
    role='Analista de Regras de Negócio e Benefícios',
    goal='Aplicar regras complexas de sindicato, férias, admissão/desligamento e exclusão para calcular os dias úteis.',
    backstory='Um especialista em RH que entende todas as regras de acordos coletivos e políticas internas para um cálculo preciso.',
    verbose=True,
    llm=llm
)

gerador_relatorios = Agent(
    role='Gerador de Relatórios e Formatos',
    goal='Compilar os dados finais e gerar um relatório em um formato específico para envio a fornecedores.',
    backstory='Um profissional focado em entregas, garantindo que o resultado final está perfeitamente formatado e pronto para ser usado.',
    verbose=True,
    llm=llm
)

# --- Tarefas ---
tarefa_consolidacao = Task(
    description=dedent(f"""
        1. Consolidar os seguintes dados em um único DataFrame Pandas:
           - Base de ativos: {base_ativa.to_string()}
           - Base de férias: {base_ferias.to_string()}
           - Base de desligados: {base_desligados.to_string()}
           - Base de sindicato x valor: {base_sindicato_valor.to_string()}
        2. Garantir que todas as informações (matrícula, nome, cargo, sindicato) estão alinhadas.
        3. A saída deve ser um DataFrame consolidado, pronto para o próximo passo.
    """),
    expected_output='Um DataFrame Pandas consolidado e limpo contendo todas as informações de todas as bases, pronto para processamento.',
    agent=agente_dados
)

tarefa_tratamento_regras = Task(
    description=dedent(f"""
        Com base no DataFrame consolidado, aplique as seguintes regras:
        - Remova da base profissionais com cargo de diretor.
        - Para desligamentos: se o comunicado de desligamento (2025-05-16) for posterior ao dia 15, o benefício é proporcional. Calcule os dias úteis para o mês de maio, considerando 22 dias úteis no total para o Sindicato A.
        - Considere as férias: para a matrícula 103, subtraia os dias de férias (2025-05-10 a 2025-05-20) dos dias úteis totais.
        - A saída deve ser um DataFrame com uma nova coluna chamada 'dias_uteis_liquidos', contendo o número correto de dias a serem pagos.
    """),
    expected_output='Um DataFrame Pandas com a coluna "dias_uteis_liquidos" calculada para cada profissional, após a aplicação de todas as regras.',
    context=[tarefa_consolidacao],
    agent=analista_regras
)

tarefa_calculo_financeiro = Task(
    description=dedent("""
        Com base no DataFrame com os dias úteis líquidos, calcule os valores finais:
        - Adicione uma coluna 'valor_total_vr', multiplicando os 'dias_uteis_liquidos' pelo 'vr_valor' de cada sindicato.
        - Adicione uma coluna 'custo_empresa', que corresponde a 80% do 'valor_total_vr'.
        - Adicione uma coluna 'custo_profissional', que corresponde a 20% do 'valor_total_vr'.
        A saída deve ser um DataFrame com todas as novas colunas de valores calculados.
    """),
    expected_output='Um DataFrame Pandas com as colunas "valor_total_vr", "custo_empresa" e "custo_profissional" preenchidas.',
    context=[tarefa_tratamento_regras],
    agent=gerador_relatorios
)

tarefa_relatorio_final = Task(
    description=dedent("""
        Com o DataFrame final, gere uma saída textual em formato de tabela, pronta para ser copiada.
        A tabela deve conter as colunas: 'matricula', 'nome', 'dias_uteis_liquidos', 'valor_total_vr', 'custo_empresa', 'custo_profissional'.
        A saída deve ser a tabela final formatada, sem incluir o DataFrame completo.
    """),
    expected_output='Uma tabela textual com os resultados finais de cálculo, pronta para ser copiada e usada para o envio ao fornecedor.',
    context=[tarefa_calculo_financeiro],
    agent=gerador_relatorios
)

# --- Criar a Crew e executar ---
crew = Crew(
    agents=[agente_dados, analista_regras, gerador_relatorios],
    tasks=[tarefa_consolidacao, tarefa_tratamento_regras, tarefa_calculo_financeiro, tarefa_relatorio_final],
    verbose=2,
    process=Process.sequential
)

print("### Iniciando a automação da compra de Vale Refeição...")
result = crew.kickoff()
print("\n\n### Relatório de Compra de VR/VA Final (para fornecedor) ###")
print(result)