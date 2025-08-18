# Usa uma imagem base oficial do Python, baseada em Linux (Debian)
FROM python:3.12-slim-bullseye

# Define o diretório de trabalho no container
WORKDIR /app

# Instala as dependências de sistema necessárias para compilar bibliotecas nativas
# 'build-essential' inclui o compilador GCC, que é o equivalente ao Visual C++ no Linux
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copia o ficheiro de dependências e instala as bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o teu código Python para o container
COPY main.py .

# Define o comando que será executado quando o container iniciar
CMD ["python", "main.py"]