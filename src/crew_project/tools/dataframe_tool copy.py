# src/crew_project/tools/dataframe_tool.py
# -*- coding: utf-8 -*-
"""
Ferramentas de dados para uso com CrewAI/LangChain:
- descompactar_arquivos: lê ZIP (local ou URL) e carrega .xlsx/.csv em DataFrames
- preparar_amostras_para_agente: cria resumos (colunas, info, head) para LLM
- fazer_join_ou_concat: tenta join por colunas comuns; se não houver, concat
- sugerir_codigo_agrupamento: pede a um LLM um código Python de join/concat
- processar_arquivo_upload: lê arquivos enviados (csv/zip com csv)

As funções podem ser usadas diretamente ou via wrappers @tool_* (LangChain).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd
import requests

# Decorator opcional: se LangChain não estiver presente, o decorator vira no-op
try:
    from langchain.tools import tool as _lc_tool
except Exception:  # pragma: no cover
    def _lc_tool(*args, **kwargs):  # type: ignore
        def dec(f):
            return f
        return dec


# ---------------------------
# Funções "puras" (recomendado)
# ---------------------------

def descompactar_arquivos(file_path: str) -> List[Dict[str, Any]]:
    """
    Lê um ZIP (URL http(s) ou caminho local), extrai .xlsx e .csv em memória,
    retornando uma lista de dicionários:
      - indice_dataframe: índice incremental
      - nome_arquivo: nome dentro do zip
      - info: df.info() como string
      - dados: o DataFrame
    """
    resultados: List[Dict[str, Any]] = []
    print(f"📥 Abrindo ZIP: {file_path}")

    # Abre origem (URL -> bytes; local -> Path)
    if file_path.startswith("http://") or file_path.startswith("https://"):
        resp = requests.get(file_path, timeout=60)
        resp.raise_for_status()
        zip_stream: Union[bytes, Path] = io.BytesIO(resp.content)
    else:
        zip_stream = Path(file_path)
        if not Path(zip_stream).exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    with zipfile.ZipFile(zip_stream, "r") as zf:
        entradas = [i for i in zf.infolist() if not i.is_dir()
                    and (i.filename.lower().endswith(".xlsx") or i.filename.lower().endswith(".csv"))]

        print(f"📦 Itens lidos no ZIP: {len(entradas)} (.xlsx/.csv)")
        for idx, info in enumerate(entradas):
            with zf.open(info.filename) as f:
                if info.filename.lower().endswith(".xlsx"):
                    try:
                        df = pd.read_excel(f, engine="openpyxl")
                    except Exception:
                        # fallback sem engine explícito
                        df = pd.read_excel(f)
                else:
                    # CSV
                    df = pd.read_csv(f)

            buf = io.StringIO()
            df.info(buf=buf)
            resultados.append({
                "indice_dataframe": idx,
                "nome_arquivo": info.filename,
                "info": buf.getvalue(),
                "dados": df,
            })
            print(f"  ✅ {info.filename} | linhas: {len(df)}")

    return resultados


def preparar_amostras_para_agente(lista_de_dataframes_dict: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gera amostras/resumos dos DataFrames para enviar a LLM.
    Retorna itens com: indice_dataframe, nome_arquivo, info, colunas, total_linhas, primeiras_10_linhas.
    """
    saida: List[Dict[str, Any]] = []
    for i, item in enumerate(lista_de_dataframes_dict):
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
    return saida


def _colunas_comuns(lista_df: Sequence[pd.DataFrame]) -> List[str]:
    if not lista_df:
        return []
    comuns = set(lista_df[0].columns)
    for df in lista_df[1:]:
        comuns &= set(df.columns)
    # remove colunas completamente vazias em algum DF (opcional)
    return [c for c in sorted(comuns)]


def fazer_join_ou_concat(lista_df: Sequence[pd.DataFrame], how: str = "outer") -> pd.DataFrame:
    """
    Heurística:
      - Se existir pelo menos 1 coluna comum entre TODOS os DFs, faz merge sequencial nessas colunas (how=outer por padrão).
      - Caso contrário, concatena verticalmente (ignore_index=True).
    """
    if not lista_df:
        raise ValueError("lista_df vazia")

    if len(lista_df) == 1:
        return lista_df[0].copy()

    comuns = _colunas_comuns(lista_df)
    if comuns:
        print(f"🔗 Fazendo JOIN por colunas comuns: {comuns}")
        merged = lista_df[0].copy()
        for df in lista_df[1:]:
            merged = pd.merge(merged, df, on=comuns, how=how)
        return merged

    print("➕ Nenhuma coluna comum encontrada em todos os DFs, concatenando.")
    return pd.concat(lista_df, ignore_index=True, sort=False)


def sugerir_codigo_agrupamento(dados_resumo: Union[str, Sequence[Dict[str, Any]]]) -> str:
    """
    Usa o LLM configurado (get_llm) para SUGERIR um código Python que:
      - Recebe lista_df (list[pd.DataFrame])
      - Tenta join por colunas comuns; fallback concat
      - Retorna df_final
    OBS: Esta função NÃO executa o código; apenas retorna o texto sugerido.
    """
    try:
        # Import tardio para não forçar dependências quando não usado
        from crew_project.config.get_llm import get_llm
    except Exception as e:
        raise RuntimeError("get_llm() não encontrado. Crie crew_project/config/get_llm.py") from e

    llm = get_llm()

    if not isinstance(dados_resumo, str):
        # Compacta o resumo para enviar ao prompt
        partes = []
        for it in dados_resumo:
            nome = it.get("nome_arquivo", "")
            cols = it.get("colunas", [])
            linhas = it.get("primeiras_10_linhas", "")
            partes.append(f"- {nome}\n  colunas: {cols}\n  amostra:\n{linhas}")
        dados_txt = "\n\n".join(partes)
    else:
        dados_txt = dados_resumo

    prompt = (
        "Você é um assistente de engenharia de dados. Gere um código Python auto-contido que:\n"
        "1) Recebe 'lista_df' (list[pandas.DataFrame]) já carregada.\n"
        "2) Identifica colunas comuns em TODOS os DFs; se existir, faz merge sequencial (how='outer').\n"
        "3) Se não existir coluna comum, faz concat vertical (ignore_index=True).\n"
        "4) Retorna 'df_final'.\n\n"
        "Dados de referência (resumo dos DFs):\n"
        f"{dados_txt}\n\n"
        "# Gere apenas o código, sem explicações."
    )

    # Algumas implementações do LLM aceitam .invoke({"input": ...}), outras .invoke(prompt) direto
    try:
        resp = llm.invoke(prompt)  # LangChain chat models
    except TypeError:
        resp = llm.invoke({"input": prompt})

    # Normaliza para string
    content = getattr(resp, "content", None) or getattr(resp, "text", None) or str(resp)
    return content


def processar_arquivo_upload(lista_de_arquivos_upload: Sequence[Any]) -> List[pd.DataFrame]:
    """
    Lê arquivos enviados (csv ou zip contendo csv) de streams/UploadFile-like objects.
    Retorna lista de DataFrames.
    """
    saida: List[pd.DataFrame] = []
    if not lista_de_arquivos_upload:
        return saida

    for uploaded in lista_de_arquivos_upload:
        nome = getattr(uploaded, "name", "arquivo")
        print(f"📄 Processando upload: {nome}")
        try:
            if str(nome).lower().endswith(".zip"):
                with zipfile.ZipFile(uploaded, "r") as zf:
                    for info in zf.infolist():
                        if not info.is_dir() and info.filename.lower().endswith(".csv"):
                            with zf.open(info.filename) as f:
                                df = pd.read_csv(f)
                                saida.append(df)
                                print(f"  ✅ CSV no ZIP: {info.filename} (linhas: {len(df)})")
            elif str(nome).lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
                saida.append(df)
                print(f"  ✅ CSV: {nome} (linhas: {len(df)})")
        except Exception as e:
            print(f"❌ Erro ao processar {nome}: {e}")
            raise
    return saida


# -------------------------------------
# Wrappers opcionais no formato LangChain
# -------------------------------------

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

@_lc_tool("sugerir_codigo_agrupamento")
def tool_sugerir_codigo_agrupamento(dados_resumo: Union[str, List[Dict[str, Any]]]) -> str:
    """Pede a um LLM para sugerir um código Python de join/concat baseado no resumo."""
    return sugerir_codigo_agrupamento(dados_resumo)    