import zipfile
import pandas as pd
import logging
from crewai.tools import tool

logger = logging.getLogger(__name__)

@tool("ler_planilhas_zip")
def tool_ler_planilhas_zip(file_path: str) -> str:
    """Lê arquivos .xlsx dentro de um .zip e retorna amostra dos dados como string."""
    try:
        extracted_data = []
        
        with zipfile.ZipFile(file_path, "r") as z:
            excel_files = [f for f in z.namelist() if f.endswith(".xlsx")]
            
            if not excel_files:
                return "❌ Nenhum arquivo .xlsx encontrado no ZIP"
            
            logger.info(f"📦 Encontrados {len(excel_files)} arquivos Excel no ZIP")
            
            for file in excel_files:
                try:
                    with z.open(file) as excel_file:
                        df = pd.read_excel(excel_file, engine='openpyxl')
                        sample_data = df.head().to_string(index=False)
                        extracted_data.append(
                            f"📄 Arquivo: {file}\n"
                            f"📊 Linhas: {len(df)} | Colunas: {len(df.columns)}\n"
                            f"🏷️  Colunas: {list(df.columns)}\n"
                            f"📋 Amostra (5 primeiras linhas):\n{sample_data}"
                        )
                        logger.info(f"✅ Processado: {file} ({len(df)} linhas)")
                except Exception as e:
                    error_msg = f"❌ Erro ao ler {file}: {str(e)}"
                    extracted_data.append(error_msg)
                    logger.error(error_msg)
        
        return "\n\n" + "="*60 + "\n\n".join(extracted_data)
        
    except FileNotFoundError:
        error_msg = f"❌ Arquivo ZIP não encontrado: {file_path}"
        logger.error(error_msg)
        return error_msg
    except zipfile.BadZipFile:
        error_msg = f"❌ Arquivo inválido ou corrompido: {file_path}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Erro inesperado ao processar ZIP: {str(e)}"
        logger.error(error_msg)
        return error_msg