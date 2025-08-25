"""
Ferramentas de dados para uso com CrewAI/LangChain:
- descompactar_arquivos: lê ZIP (local ou URL) e carrega .xlsx/.csv em DataFrames
- preparar_amostras_para_agente: cria resumos (colunas, info, head) para LLM
- fazer_join_ou_concat: tenta join por colunas comuns; se não houver, concat
- sugerir_codigo_agrupamento: pede a um LLM um código Python de join/concat
- processar_arquivo_upload: lê arquivos enviados (csv/zip com csv)
"""

from __future__ import annotations

import io
import zipfile
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd
import requests

# Decorator para LangChain tools
try:
    from crewai.tools import tool as _lc_tool
except ImportError:
    def _lc_tool(*args, **kwargs):
        def dec(f):
            return f
        return dec

logger = logging.getLogger(__name__)

# ---------------------------
# Funções principais
# ---------------------------

def descompactar_arquivos(file_path: str) -> List[Dict[str, Any]]:
    """
    Lê um ZIP (URL http(s) ou caminho local), extrai .xlsx e .csv em memória,
    retornando uma lista de dicionários com metadados e DataFrames.
    """
    resultados: List[Dict[str, Any]] = []
    logger.info(f"📥 Abrindo ZIP: {file_path}")

    try:
        # Determina se é URL ou arquivo local
        if file_path.startswith("http://") or file_path.startswith("https://"):
            logger.info("🌐 Baixando ZIP da URL...")
            resp = requests.get(file_path, timeout=60)
            resp.raise_for_status()
            zip_stream: Union[bytes, Path] = io.BytesIO(resp.content)
        else:
            zip_stream = Path(file_path)
            if not zip_stream.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with zipfile.ZipFile(zip_stream, "r") as zf:
            # Filtra apenas arquivos .xlsx e .csv
            entradas = [
                i for i in zf.infolist() 
                if not i.is_dir() and (
                    i.filename.lower().endswith(".xlsx") or 
                    i.filename.lower().endswith(".csv")
                )
            ]

            logger.info(f"📦 Arquivos encontrados: {len(entradas)} (.xlsx/.csv)")
            
            for idx, info in enumerate(entradas):
                try:
                    with zf.open(info.filename) as f:
                        if info.filename.lower().endswith(".xlsx"):
                            df = pd.read_excel(f, engine="openpyxl")
                        else:
                            df = pd.read_csv(f)

                    # Gera informações do DataFrame
                    buf = io.StringIO()
                    df.info(buf=buf)
                    
                    resultado = {
                        "indice_dataframe": idx,
                        "nome_arquivo": info.filename,
                        "info": buf.getvalue(),
                        "dados": df,
                    }
                    resultados.append(resultado)
                    logger.info(f"  ✅ {info.filename} | {len(df)} linhas x {len(df.columns)} colunas")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar {info.filename}: {e}")
                    raise

        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro ao descompactar arquivo: {e}")
        raise

def preparar_amostras_para_agente(lista_de_dataframes_dict: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gera amostras/resumos dos DataFrames para enviar a LLM.
    """
    if not lista_de_dataframes_dict:
        return []
        
    saida: List[Dict[str, Any]] = []
    
    for i, item in enumerate(lista_de_dataframes_dict):
        if "dados" not in item:
            logger.warning(f"Item {i} não possui chave 'dados', pulando...")
            continue
            
        df: pd.DataFrame = item["dados"]
        
        amostra = {
            "indice_dataframe": item.get("indice_dataframe", i),
            "nome_arquivo": item.get("nome_arquivo", f"df_{i}.csv"),
            "info": item.get("info", ""),
            "colunas": list(df.columns),
            "total_linhas": int(len(df)),
            "primeiras_10_linhas": df.head(10).to_string(index=False),
        }
        saida.append(amostra)
        
    logger.info(f"📊 Preparadas {len(saida)} amostras para análise")
    return saida

def _colunas_comuns(lista_df: Sequence[pd.DataFrame]) -> List[str]:
    """Encontra colunas comuns entre todos os DataFrames."""
    if not lista_df:
        return []
    
    comuns = set(lista_df[0].columns)
    for df in lista_df[1:]:
        comuns &= set(df.columns)
    
    return sorted(list(comuns))

def fazer_join_ou_concat(lista_df: Sequence[pd.DataFrame], how: str = "outer") -> pd.DataFrame:
    """
    Heurística de união de DataFrames:
    - Se existir pelo menos 1 coluna comum, faz merge sequencial
    - Caso contrário, concatena verticalmente
    """
    if not lista_df:
        raise ValueError("Lista de DataFrames não pode estar vazia")
    
    if len(lista_df) == 1:
        return lista_df[0].copy()
    
    # Valida parâmetro 'how'
    valid_how = ["inner", "outer", "left", "right"]
    if how not in valid_how:
        raise ValueError(f"Parâmetro 'how' deve ser um de: {valid_how}")
    
    comuns = _colunas_comuns(lista_df)
    
    if comuns:
        logger.info(f"🔗 Fazendo JOIN por colunas comuns: {comuns} (how={how})")
        merged = lista_df[0].copy()
        
        for i, df in enumerate(lista_df[1:], 1):
            try:
                merged = pd.merge(merged, df, on=comuns, how=how)
                logger.info(f"  ✅ Merged DataFrame {i+1}: {len(merged)} linhas resultantes")
            except Exception as e:
                logger.error(f"❌ Erro no merge com DataFrame {i+1}: {e}")
                raise
                
        return merged
    else:
        logger.info("➕ Nenhuma coluna comum encontrada, concatenando verticalmente")
        try:
            result = pd.concat(lista_df, ignore_index=True, sort=False)
            logger.info(f"  ✅ Concatenação: {len(result)} linhas totais")
            return result
        except Exception as e:
            logger.error(f"❌ Erro na concatenação: {e}")
            raise

def sugerir_codigo_agrupamento(dados_resumo: Union[str, Sequence[Dict[str, Any]]]) -> str:
    """
    Usa o LLM para SUGERIR código Python de agrupamento/união de DataFrames.
    NÃO executa o código, apenas retorna a sugestão.
    """
    try:
        from crew_project.config.get_llm import get_llm
    except ImportError as e:
        error_msg = "get_llm() não encontrado. Verifique se crew_vr_project/config/get_llm.py existe"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    llm = get_llm()

    # Prepara dados para o prompt
    if isinstance(dados_resumo, str):
        dados_txt = dados_resumo
    else:
        partes = []
        for item in dados_resumo:
            nome = item.get("nome_arquivo", "arquivo_sem_nome")
            cols = item.get("colunas", [])
            linhas_amostra = item.get("primeiras_10_linhas", "")
            total_linhas = item.get("total_linhas", 0)
            
            partes.append(
                f"📄 {nome} ({total_linhas} linhas)\n"
                f"   Colunas: {cols}\n"
                f"   Amostra:\n{linhas_amostra}"
            )
        dados_txt = "\n\n".join(partes)

    prompt = f"""
Você é um especialista em Pandas. Analise os DataFrames abaixo e gere um código Python que:

1. Recebe uma variável 'lista_df' (List[pd.DataFrame]) já carregada
2. Identifica colunas comuns em TODOS os DataFrames
3. Se houver colunas comuns, faz merge sequencial (how='outer')
4. Se NÃO houver colunas comuns, faz concatenação vertical (ignore_index=True)
5. Retorna o resultado como 'df_final'

DADOS PARA ANÁLISE:
{dados_txt}

IMPORTANTE:
- Gere apenas o código Python, sem explicações
- Use apenas pandas (pd) e funções nativas do Python
- Inclua print() para mostrar informações do processo
- Trate possíveis erros com try/except

Código:
"""

    try:
        # Invoca LLM
        if hasattr(llm, 'invoke'):
            resp = llm.invoke(prompt)
        else:
            resp = llm(prompt)
            
        # Extrai conteúdo da resposta
        if hasattr(resp, 'content'):
            content = resp.content
        elif hasattr(resp, 'text'):
            content = resp.text
        else:
            content = str(resp)
            
        logger.info("🤖 Código de agrupamento gerado pelo LLM")
        return content
        
    except Exception as e:
        error_msg = f"Erro ao gerar código com LLM: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

def processar_arquivo_upload(lista_de_arquivos_upload: Sequence[Any]) -> List[pd.DataFrame]:
    """
    Processa arquivos enviados (CSV ou ZIP contendo CSVs).
    Retorna lista de DataFrames.
    """
    saida: List[pd.DataFrame] = []
    
    if not lista_de_arquivos_upload:
        logger.warning("Nenhum arquivo para processar")
        return saida

    for uploaded in lista_de_arquivos_upload:
        nome = getattr(uploaded, "name", "arquivo_sem_nome")
        logger.info(f"📄 Processando upload: {nome}")
        
        try:
            if str(nome).lower().endswith(".zip"):
                with zipfile.ZipFile(uploaded, "r") as zf:
                    csv_files = [
                        info for info in zf.infolist() 
                        if not info.is_dir() and info.filename.lower().endswith(".csv")
                    ]
                    
                    for info in csv_files:
                        with zf.open(info.filename) as f:
                            df = pd.read_csv(f)
                            saida.append(df)
                            logger.info(f"  ✅ CSV no ZIP: {info.filename} ({len(df)} linhas)")
                            
            elif str(nome).lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
                saida.append(df)
                logger.info(f"  ✅ CSV: {nome} ({len(df)} linhas)")
            else:
                logger.warning(f"  ⚠️  Tipo de arquivo não suportado: {nome}")
                
        except Exception as e:
            error_msg = f"Erro ao processar {nome}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    logger.info(f"📊 Total de DataFrames processados: {len(saida)}")
    return saida

# ---------------------------
# Wrappers para LangChain Tools
# ---------------------------

@_lc_tool("descompactar_arquivos")
def tool_descompactar_arquivos(file_path: str) -> List[Dict[str, Any]]:
    """Lê ZIP (URL/local) e retorna metadados + DataFrames em memória."""
    return descompactar_arquivos(file_path)

@_lc_tool("preparar_amostras_para_agente")
def tool_preparar_amostras_para_agente(lista_de_dataframes_dict: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gera resumos dos DataFrames para consumo por LLM."""
    return preparar_amostras_para_agente(lista_de_dataframes_dict)

@_lc_tool("fazer_join_ou_concat")
def tool_fazer_join_ou_concat(lista_df: List[pd.DataFrame], how: str = "outer") -> pd.DataFrame:
    """Faz merge por colunas comuns; se não houver, concatena."""
    return fazer_join_ou_concat(lista_df, how)

@_lc_tool("sugerir_codigo_agrupamento")
def tool_sugerir_codigo_agrupamento(dados_resumo: Union[str, List[Dict[str, Any]]]) -> str:
    """Pede a um LLM para sugerir código Python de join/concat baseado no resumo."""
    return sugerir_codigo_agrupamento(dados_resumo)