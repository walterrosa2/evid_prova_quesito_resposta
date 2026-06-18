FROM python:3.11-slim

WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta do Streamlit
EXPOSE 8519

# Criação das pastas de dados esperadas pela aplicação
RUN mkdir -p /app/execucoes && chmod 777 /app/execucoes

HEALTHCHECK CMD curl --fail http://localhost:8519/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8519", "--server.address=0.0.0.0"]
