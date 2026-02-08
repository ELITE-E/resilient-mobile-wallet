# Mobile Wallet API

FastAPI-based service for a resilient mobile wallet. Includes Postgres, TigerBeetle, and async SQLAlchemy.

## Prerequisites
- Python 3.11+
- Docker + Docker Compose (for running services)

## Setup (local, virtualenv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env  # adjust values as needed
```

## Run locally (uvicorn)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run with Docker Compose (app + Postgres + TigerBeetle)
```bash
docker compose up --build
```
- API: http://localhost:8000
- Health: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

## Lint, format, type-check, test
```bash
ruff check .
black --check .
mypy app
pytest -v
```

## Notes
- Runtime deps live in `requirements.txt`; dev/test tools in `requirements-dev.txt`.
- Docker image installs only runtime deps to stay slim.
- TigerBeetle data is stored in the `tb-data` volume when using Compose.
