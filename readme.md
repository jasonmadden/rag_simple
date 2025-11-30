# RAG Simple

Lightweight Retrieval-Augmented Generation (RAG) playground using LlamaIndex with a Postgres + pgvector backend. It provides two main scripts:

- `app/ingest.py` — chunks and ingests documents from a local `docs/` folder into a Postgres vector store.
- `app/query.py` — loads the index from Postgres and lets you query it using an LLM (defaults to local Ollama `llama3`).

## Stack

- Language: Python (scripts, no package/module)
- Framework/Libraries: LlamaIndex, sentence-transformers/HuggingFace, optional OpenAI embeddings, optional Ollama LLM
- Vector DB: Postgres with `pgvector`
- Orchestration: Docker Compose (brings up Postgres and a dev container for the app)
- Package manager: `pip` via `requirements.txt`

## Requirements

Choose one of the two paths below.

### A) With Docker (recommended)
- Docker and Docker Compose

### B) Local (without Docker)
- Python 3.10+ (3.11 recommended)
  - TODO: Verify exact Python version used in CI/dev
- A running Postgres instance with the `pgvector` extension installed and enabled
- Ability to create a database (default name `vectordb`)

## Environment Variables

These are read primarily by `app/ingest.py` and reused by `app/query.py`:

- `PGDATABASE` — default: `vectordb`
- `PGUSER` — default: `postgres`
- `PGPASSWORD` — default: `password`
- `PGHOST` — default: `localhost`
- `PGPORT` — default: `5432`
- `TABLE_NAME` — default: `documents`

Embeddings provider (toggle inside `app/ingest.py`):

- `USE_OPENAI` is coded as a constant in `ingest.py` (set `True` to use OpenAI embeddings). If `True`, the following are used for Azure OpenAI embeddings:
  - `AZURE_OPENAI_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_VERSION` — default in code: `2023-05-15`

LLM:

- `query.py` uses Ollama with `model="llama3"` hardcoded.
  - Optional: set `OLLAMA_HOST` if your Ollama server is remote.
  - TODO: Consider making the Ollama model configurable via env var.

Use a `.env` file at the project root to set these; both scripts call `dotenv.load_dotenv()`.

## Setup and Run

### Option A: Docker Compose

This repository contains a `docker-compose.yml` that defines two services:

- `db` — Postgres with pgvector (built from `.docker/pgvector/Dockerfile`)
- `app` — a Python dev container (built from `.docker/app/Dockerfile`) mounting the repo into `/app`

Commands:

```bash
# Build and start containers
docker compose up --build -d

# Attach an interactive shell to the app container
docker compose exec app bash

# Inside the container, ensure venv is active per docker command (it sources /app/.venv)
# Install deps (if not pre-baked in the image)
pip install -r app/requirements.txt

# Create a docs folder and put your files there
mkdir -p docs
cp /path/to/your/files/* docs/

# Ingest
python app/ingest.py

# Query
python app/query.py
```

Notes:

- The compose file exposes Postgres on `localhost:5432` and persists data to a named volume `.db_data`.
- The app service runs an interactive shell by default (via `command: ["/bin/bash", "-lc", "source /app/.venv/bin/activate && exec bash"]`).
- TODO: Verify that `.docker/app/Dockerfile` and `.docker/pgvector/Dockerfile` exist in the checked-in repo; `docker-compose.yml` references them.

### Option B: Local (no Docker)

1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2) Install dependencies

```bash
pip install -r app/requirements.txt
```

3) Ensure Postgres with pgvector is running and accessible. Create database `vectordb` (or set `PGDATABASE`). Example psql session:

```sql
CREATE DATABASE vectordb;
\c vectordb
CREATE EXTENSION IF NOT EXISTS vector;
```

4) Create `docs/` and add files to ingest

```bash
mkdir -p docs
cp /path/to/your/files/* docs/
```

5) Ingest and query

```bash
python app/ingest.py
python app/query.py
```

## Scripts and Entry Points

- `python app/ingest.py`
  - Loads files from `docs/`, chunks them, embeds them (HuggingFace by default; switch to OpenAI by toggling `USE_OPENAI` in the file), and writes to Postgres via `PGVectorStore`.

- `python app/query.py`
  - Connects to the same Postgres vector store, constructs an index, and opens an interactive prompt. Uses Ollama `llama3` for responses. Type `exit` to quit.

- `python app/test.py`
  - Simple smoke test: verifies the sentence-transformers model loads and tests a Postgres connection using `psycopg2`.

There is no `setup.py`/`pyproject.toml`; scripts are executed directly with Python.

## Tests

No formal unit tests are included. For a quick health check:

```bash
python app/test.py
```

TODO:
- Add pytest and minimal unit tests for ingestion and query pipeline.

## Project Structure

```
.
├── app/
│   ├── ingest.py          # Ingest documents into Postgres/pgvector
│   ├── query.py           # Interactive querying via Ollama + LlamaIndex
│   ├── requirements.txt   # Python dependencies
│   └── test.py            # Simple connectivity smoke test
├── docker-compose.yml     # Dev orchestration (Postgres + app container)
├── readme.md              # This file
├── LICENSE                # Project license
└── docs/                  # Your source documents to ingest (create this)
```

Related but not listed above (referenced by compose):

- `.docker/pgvector/Dockerfile`  
- `.docker/app/Dockerfile`  
TODO: Confirm these files are present and correct.

## Configuration Notes

- Chunking in `ingest.py` uses `SimpleNodeParser(chunk_size=200, chunk_overlap=20)`.
- Default HuggingFace embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).
  - If `USE_OPENAI=True`, uses Azure OpenAI `text-embedding-3-small` (1536-dim) — ensure Azure credentials are set.
- Table name defaults to `documents`; change via `TABLE_NAME`.

## Troubleshooting

- Postgres connection errors: confirm credentials/env vars and that `vector` extension is installed.
- Embedding model errors: ensure the model can be downloaded (internet access) or cached, and that CUDA/CPU is appropriate for your setup.
- Ollama not responding: make sure the Ollama service is running and the `llama3` model is pulled: `ollama run llama3`.

## License

This project is licensed under the terms of the license found in `LICENSE`.
