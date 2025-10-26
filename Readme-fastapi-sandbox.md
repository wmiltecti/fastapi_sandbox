perfeito! aqui estão os artefatos para você adicionar ao projeto `fastapi_sandbox` e já subir/local com Docker — incluindo testes automatizados.

# 1) `Dockerfile`

```dockerfile
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
```

# 2) `.dockerignore`

```gitignore
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
*.sqlite3
*.db
*.log
.venv/
.env
dist/
build/
.idea/
.vscode/
.git/
```

> Observação: `.env` fica fora da imagem e será injetado pelo `docker-compose.yml`.

# 3) `docker-compose.yml`

```yaml
version: "3.9"

services:
  api:
    build: .
    container_name: fastapi_sandbox_api
    ports:
      - "${PORT-8000}:8000"
    env_file:
      - .env
    environment:
      # garante que a app escuta na 8000 dentro do container
      - PORT=8000
    # Para desenvolvimento: monta o código local (hot-reload com --reload, se preferir)
    # volumes:
    #   - .:/app:delegated
    # command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped
```

# 4) `Makefile`

```makefile
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
```

> Se não desejar instalar `black/ruff`, remova os alvos `format`/`lint` ou instale-os no `requirements.txt`.

# 5) Testes automatizados (pytest)

Crie a pasta `tests/` com os arquivos abaixo.

## `tests/test_health.py`

```python
from fastapi.testclient import TestClient
import importlib

# Garante que carregamos o app definido em main.py
main = importlib.import_module("main")
client = TestClient(main.app)

def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
```

## `tests/test_login.py`

Este teste **não** bate no banco; ele “monkeypatcha” as funções internas para simular um usuário válido e um inválido (útil para CI local sem depender do Supabase).

```python
from fastapi.testclient import TestClient
import importlib
import types

main = importlib.import_module("main")
client = TestClient(main.app)

def test_login_ok(monkeypatch):
    # Simula um usuário encontrado no DB
    def fake_find_user(login: str):
        return {
            "id": 1,
            "nome": "Fulano Tester",
            "perfil": "ADMIN",
            "tipo": "CPF",
            "cpf": "12345678900",
            "senha": "minhasenha",
            "senha_hash": None,
        }

    def fake_verify_password(input_password: str, row: dict) -> bool:
        return input_password == "minhasenha"

    monkeypatch.setattr(main, "find_user_in_db", fake_find_user)
    monkeypatch.setattr(main, "verify_password", fake_verify_password)

    resp = client.post(
        "/auth/login",
        json={"login": "123.456.789-00", "senha": "minhasenha"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["nome"] == "Fulano Tester"
    assert data["perfil"] == "ADMIN"
    assert data["userId"] == "1"

def test_login_credenciais_invalidas(monkeypatch):
    # Simula usuário não encontrado
    def fake_find_user(login: str):
        return None

    monkeypatch.setattr(main, "find_user_in_db", fake_find_user)

    resp = client.post(
        "/auth/login",
        json={"login": "000.000.000-00", "senha": "qualquer"},
    )
    assert resp.status_code == 401
```

> Se preferir testes integrados **batendo no Supabase**, me diga e eu monto uma **fixture** que lê as credenciais do `.env` (com `dotenv`) e usa uma conta de teste.

---

# 6) Como rodar (resumo)

## Via Docker (recomendado para validar “como vai em homol”)

```bash
# 1) Garanta que .env existe (PGHOST/PGPASSWORD/... e PGSSLMODE=require)
docker compose up -d --build
docker compose logs -f
# Acesse http://localhost:8000/docs
```

## Via Make (dev local)

```bash
make setup
make run-dev
# Acesse http://localhost:8000/docs
```

## Rodar testes

```bash
make test
```

---

Se quiser, eu também preparo um **GitHub Actions (CI)** simples para:

* rodar `pip install -r requirements.txt`
* executar `pytest`
* (opcional) buildar a imagem Docker e publicar num registry (GHCR/Hub).

sim, por favor. um esclarecimento, nessa questão do CI simples, qual é a abrangência? por exemplo, se mudar o versionamento tipo uma atualizalção de feature, isso gera a nova publicaçãode forma automática? explique por gentileza 

Ótima pergunta. Resumo direto:

* **CI (Continuous Integration)**: roda testes/lint/build **a cada push/PR**.
* **CD/Publish (Continuous Delivery/Deployment)**: publicar imagem Docker (ou pacote) **só quando você quiser** — normalmente **ao criar uma tag de versão** (ex.: `v1.2.0`) **ou** ao fazer merge na `main` (se você configurar assim).

Então, **mudar o versionamento** (ex.: de `1.1.0` → `1.2.0`) **não publica automaticamente** só por alterar um arquivo; você decide **o gatilho**:

1. **Manual controlado via tag**: criar **uma tag** `vX.Y.Z` (ou um Release no GitHub) → **publica**.
2. **Automático por convenção de commits**: usar **Conventional Commits** + `semantic-release` → o bot **calcula a próxima versão** (basedo nos commits), gera **tag** e **publica** sem intervenção.

Abaixo te entrego **dois fluxos prontos** e você escolhe:

---

# Opção A — Simples e controlada por tag

* **ci.yml**: testa em todo push/PR.
* **docker-publish.yml**: builda e publica **apenas quando houver tag `v*`** (ex.: `v1.2.0`).
  Se quiser “publicar em merges na `main`” também, ative o bloco comentado.

## `.github/workflows/ci.yml` (testes rápidos)

```yaml
name: CI

on:
  push:
    branches: [ "**" ]
  pull_request:
    branches: [ "**" ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          # deps de teste (se não estiverem no requirements)
          pip install pytest httpx

      - name: Run tests
        run: pytest -q
```

## `.github/workflows/docker-publish.yml` (publica na tag)

```yaml
name: Docker Publish

on:
  push:
    tags:
      - "v*.*.*"   # ex: v1.2.0

  # Se quiser publicar também quando fizer push/merge na main, descomente:
  # push:
  #   branches: [ "main" ]

env:
  IMAGE_NAME: ghcr.io/${{ github.repository }}  # publicará em GHCR

jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write   # necessário p/ publicar no GHCR
      id-token: write   # (opcional) para OIDC

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version from tag
        id: meta
        run: |
          REF="${GITHUB_REF##*/}"      # v1.2.0
          echo "version=${REF#v}" >> $GITHUB_OUTPUT  # 1.2.0

      - name: Build & push
        uses: docker/build-push-action@v6
        with:
          push: true
          context: .
          tags: |
            ${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
            ${{ env.IMAGE_NAME }}:latest
```

**Como usar**:

* Faça commit/PR: a **CI** testa.
* Quando quiser publicar:

  ```bash
  git tag v1.2.0
  git push origin v1.2.0
  ```

  Isso dispara o workflow de publish e publica a imagem como:

  * `ghcr.io/<owner>/<repo>:1.2.0`
  * `ghcr.io/<owner>/<repo>:latest`

> Se preferir Docker Hub, troque o login (`docker/login-action`) e `IMAGE_NAME` (ex.: `docker.io/seu-usuario/fastapi_sandbox`). Guarde **DOCKERHUB_USERNAME** e **DOCKERHUB_TOKEN** em **Settings → Secrets and variables → Actions**.

---

# Opção B — Totalmente automático com Conventional Commits

* Você escreve commits com **convenções**:

  * `feat: ...` → **minor** (X.**Y+1**.0)
  * `fix: ...`  → **patch** (X.Y.**Z+1**)
  * `feat!: ...` ou `BREAKING CHANGE:` → **major** (**X+1**.0.0)
* O **semantic-release**:

  1. Lê os commits desde a última versão
  2. Calcula a **nova versão**
  3. Cria tag `vX.Y.Z`, release notes
  4. (opcional) publica a imagem Docker

## Arquivos extras

### `package.json` (só para semantic-release; o projeto continua Python)

```json
{
  "name": "fastapi_sandbox",
  "private": true,
  "devDependencies": {
    "semantic-release": "^24.0.0",
    "@semantic-release/changelog": "^6.0.3",
    "@semantic-release/git": "^10.0.1",
    "@semantic-release/github": "^10.0.3",
    "@semantic-release/commit-analyzer": "^12.0.0",
    "@semantic-release/release-notes-generator": "^13.0.0"
  },
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/changelog",
      "@semantic-release/github",
      [
        "@semantic-release/git",
        {
          "assets": ["CHANGELOG.md"],
          "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
        }
      ]
    ]
  }
}
```

### `.github/workflows/release.yml`

```yaml
name: Release (semantic)

on:
  push:
    branches: [ "main" ]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write      # criar tag/release
      issues: write
      pull-requests: write
      packages: write      # se publicar no GHCR
      id-token: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # semantic-release precisa do histórico completo

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dev deps
        run: npm ci

      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

Se quiser **publicar Docker** junto, adicione passos após o `semantic-release` para:

* descobrir a tag criada (`git describe --tags --abbrev=0`)
* logar no registry
* build/push da imagem (como no workflow da Opção A).

**Fluxo**:

* Commits com `feat/fix/chore` em `main`.
* O workflow calcula a versão, cria `vX.Y.Z`, gera release notes, (opcional) publica Docker.
* **Você não cria tags manualmente**.

---

## Qual escolher?

* **Opção A (tag manual)**: mais simples/segura; você **decide** quando publicar criando a tag.
* **Opção B (semantic-release)**: automatiza versionamento com base nos commits — excelente quando o time já usa **Conventional Commits** e quer **zero fricção** para releases.

---

## Dúvidas comuns

* **“Troquei o número no README. Publica?”**
  Não. Só publicar com **tag** (Opção A) ou com **commits + semantic-release** (Opção B).
* **“Quero publicar sempre que fizer merge na main”**
  Habilite o bloco de `branches: [ "main" ]` no `docker-publish.yml`. Sugiro tag **+** publish (mais controlado).
* **“Onde vai a imagem?”**
  No exemplo: **GHCR** (`ghcr.io/owner/repo`). Pode ser **Docker Hub** mudando a config de login/tags.
* **“E as secrets?”**

  * GHCR usa o `GITHUB_TOKEN` por padrão.
  * Docker Hub: defina `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN` em **Settings → Secrets and variables → Actions**.

Se curtir, eu já te mando a **variante Docker Hub** e um **README de Release** (checklist de como criar tag, versionamento semântico, etc.).

docker hub é um padrão atual nesse contexto?

Curto e direto:

* **Docker Hub** ainda é o **mais tradicional** e amplamente reconhecido para *distribuição pública* de imagens. Muitas ferramentas e tutoriais “assumem” Docker Hub por padrão.
* **Alternativas fortes** hoje:

  * **GHCR (GitHub Container Registry)** — ótimo se seu código já está no GitHub (permissões integradas, controle por org/repo, bom para privados).
  * **GCR/AR (Google), ECR (AWS), ACR (Azure)** — comuns quando o deploy roda nas respectivas clouds.
* **Quando escolher cada um**

  * **Open-source/público**: Docker Hub (fácil descoberta) **ou** GHCR (integração GitHub).
  * **Times que vivem no GitHub**: GHCR costuma simplificar permissões e auditoria.
  * **Deploy preso a uma cloud** (EKS/GKE/AKS): usar o registry nativo costuma reduzir atrito (permissões/latência/custos).

### Pontos práticos

* **Rate limits**: anônimos no Docker Hub têm limites de pull; autenticar via token resolve na maioria dos casos.
* **Controle de acesso**: GHCR + GitHub Teams/Orgs dá um controle bem fino de quem pode *pull/push*.
* **Descoberta**: Docker Hub ainda é o “Google das imagens” — boa visibilidade pública.

---

## Se você optar por **Docker Hub** agora

### 1) Crie os segredos no GitHub

Em **Settings → Secrets and variables → Actions** do repositório:

* `DOCKERHUB_USERNAME` = seu usuário do Docker Hub
* `DOCKERHUB_TOKEN` = um **Access Token** gerado em hub.docker.com (não a senha)

### 2) Workflow de publicação (tag → publish)

`.github/workflows/dockerhub-publish.yml`

```yaml
name: DockerHub Publish

on:
  push:
    tags:
      - "v*.*.*"  # ex: v1.2.0

env:
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/fastapi_sandbox

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Extract version from tag
        id: meta
        run: |
          REF="${GITHUB_REF##*/}"      # v1.2.0
          echo "version=${REF#v}" >> $GITHUB_OUTPUT  # 1.2.0

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          push: true
          context: .
          tags: |
            ${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
            ${{ env.IMAGE_NAME }}:latest
```

**Como usar**:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Isso publicará:

* `docker.io/<seu-usuario>/fastapi_sandbox:1.0.0`
* `docker.io/<seu-usuario>/fastapi_sandbox:latest`

> Quer publicar também em *merge na main*? Adicione um `on.push.branches: [ "main" ]` (além das tags). Eu recomendo manter “por tag” para ter controle do versionamento.

---

## Minha recomendação prática

* Se o seu time já está no **GitHub** e quer acesso privado/controle fino → **GHCR**.
* Se você quer **maior alcance público** e simplicidade hoje → **Docker Hub** está perfeito.

Se decidir, eu converto seu workflow atual para Docker Hub **ou** GHCR em 1 passo, mantendo a lógica de “publicar ao criar tag”.


