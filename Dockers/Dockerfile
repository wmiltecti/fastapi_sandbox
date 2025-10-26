# Dockerfile
FROM python:3.11-slim

# Evita .pyc e buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema: psycopg (pgclient) e build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copia apenas requirements primeiro (para cache eficiente)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copia o restante do projeto
COPY . /app

# Porta default (pode ser sobrescrita por compose)
ENV PORT=8000

# Healthcheck simples (opcional)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:${PORT}/health || exit 1

EXPOSE 8000
# Executa via Uvicorn carregando "main:app"
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
