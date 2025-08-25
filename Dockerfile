FROM python:3.11-slim

# Instala compiladores, CMake e libs matemáticas
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements primeiro (cache de build mais eficiente)
COPY requirements.txt .

# Atualiza pip e instala requirements

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Instala o llama-cpp-python (compila dentro do container)
RUN pip install llama-cpp-python

# Copia o código
# Copiar código
COPY src/ ./src/

# Comando padrão (ajuste conforme necessário)
# Rodar app
CMD ["python", "-m", "crew_project.main"]
