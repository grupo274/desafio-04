import zipfile
import pandas as pd
from crewai.tools import tool

@tool("excel_zip_tool")
def ler_planilhas_zip(path: str) -> str:
    """Lê arquivos .xlsx dentro de um .zip e retorna amostra dos dados como string."""
    extracted_data = []
    with zipfile.ZipFile(path, "r") as z:
        for file in z.namelist():
            if file.endswith(".xlsx"):
                try:
                    df = pd.read_excel(z.open(file))
                    extracted_data.append(f"Arquivo: {file}\n{df.head().to_string()}")
                except Exception as e:
                    extracted_data.append(f"Erro ao ler {file}: {str(e)}")
    return "\n\n".join(extracted_data) if extracted_data else "Nenhum arquivo .xlsx encontrado"

@tool("ler_planilhas_zip")
def tool_ler_planilhas_zip(file_path: str):
    """Lê planilhas de dentro de um arquivo zip e retorna DataFrames."""
    return ler_planilhas_zip(file_path)