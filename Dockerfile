# Usa uma versão leve do Python 3.12 oficial
FROM python:3.12-slim

# Evita que o Python grave arquivos inúteis (.pyc) e força a exibição dos logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta principal dentro do container
WORKDIR /app

# Instala dependências do Linux necessárias para compilar o psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN pip install poetry

# Copia APENAS os arquivos do Poetry primeiro.
# (Isso é um truque: se você mudar o código fonte, o Docker não vai instalar as 50 dependências tudo de novo)
COPY pyproject.toml poetry.lock ./

# Desativa a criação de ambiente virtual (pois o container já é isolado) e instala as dependências
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copia todo o restante do código (pastas src, db, etc) para dentro do container
COPY . .