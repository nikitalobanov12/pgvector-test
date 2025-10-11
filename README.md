# Embedding Demo Service

This project demonstrates how to generate text embeddings with Sentence Transformers, store them in PostgreSQL using the `pgvector` extension, and expose the functionality via a FastAPI service. You can run it locally or with Docker Compose to stand up both the API and the backing database.

![Vector demo](demo.png)

## Requirements

- Python 3.13 (a virtual environment is recommended)
- Docker (optional, for containerized setup)
- Access to download the `sentence-transformers` model `all-MiniLM-L6-v2`

## Configuration

The service reads configuration from environment variables with sane defaults:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://dev:dev@localhost:5432/vecdb` |
| `MODEL_NAME` | Sentence Transformers model id | `all-MiniLM-L6-v2` |
| `EMBEDDING_DIMENSIONS` | Expected embedding size | `384` |

## Running with Docker Compose

```bash
docker compose up --build
```

This starts:
- `db`: PostgreSQL with `pgvector`
- `api`: FastAPI application served by Uvicorn on port `8000`

Once the containers are running, initialize the database schema (run once):

```bash
docker compose exec api python setup_db.py
```

The API is now available at `http://localhost:8000`. Swagger docs live at `http://localhost:8000/docs`.

## Running Locally (without Docker)

1. Start PostgreSQL with pgvector (for example using the provided compose file):
   ```bash
   docker compose up -d db
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies and set up the database:
   ```bash
   pip install -r requirements.txt
   python setup_db.py
   ```
4. Launch the API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## API Endpoints

- `POST /documents` – add a single document.
  ```bash
  curl -X POST http://localhost:8000/documents \
       -H "Content-Type: application/json" \
       -d '{"content": "FastAPI makes API development fast"}'
  ```
- `POST /documents/batch` – add multiple documents at once.
- `GET /documents` – list the most recent documents.
- `GET /search?query=...&limit=...` – semantic search across stored documents.
- `POST /documents/clear` – remove all stored documents.
- `GET /healthz` – basic health probe.

## Tests

Run the pytest suite:

```bash
venv/bin/pytest
```

## Legacy Script Example

The original `example.py` script still works for quick experiments:

```bash
python example.py
```

It now respects the same `DATABASE_URL` environment variable so it can talk to either the Dockerized or local database instance.

## Further Reading

- [pgvector docs](https://github.com/pgvector/pgvector)
- [pgvector psycopg adapter](https://github.com/pgvector/pgvector-python?tab=readme-ov-file#psycopg-3)
- [Sentence Transformers](https://sbert.net/)
