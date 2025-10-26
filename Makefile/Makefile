# Makefile
PY=python
PIP=pip

# Alvos principais
.PHONY: help setup run run-dev test docker-build docker-up docker-down docker-logs format lint

help:
	@echo "Alvos disponíveis:"
	@echo "  setup        - cria venv e instala deps"
	@echo "  run          - roda a API local (uvicorn)"
	@echo "  run-dev      - roda com --reload"
	@echo "  test         - executa testes (pytest)"
	@echo "  docker-build - build da imagem"
	@echo "  docker-up    - sobe com docker-compose"
	@echo "  docker-down  - desce containers"
	@echo "  docker-logs  - logs em follow"
	@echo "  format       - formata com black"
	@echo "  lint         - lints simples (ruff se estiver no req)"

setup:
	$(PY) -m venv .venv
	. .venv/bin/activate; $(PIP) install --upgrade pip
	. .venv/bin/activate; $(PIP) install -r requirements.txt
	# Dependências de dev (opcional): pytest/httpx
	- . .venv/bin/activate; $(PIP) install pytest httpx

run:
	. .venv/bin/activate; uvicorn main:app --host 0.0.0.0 --port $${PORT:-8000}

run-dev:
	. .venv/bin/activate; uvicorn main:app --host 0.0.0.0 --port $${PORT:-8000} --reload

test:
	. .venv/bin/activate; pytest -q

docker-build:
	docker build -t fastapi_sandbox:latest .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

format:
	- . .venv/bin/activate; black .

lint:
	- . .venv/bin/activate; ruff check . || true
