# Company News Article API

FastAPI and SQLite service that stores company news, then classifies and summarizes it in a background task using deterministic Python rules. No AI or ML integration is used.

## Run

```powershell
workon test
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open Swagger UI at <http://127.0.0.1:8000/docs>.

## Test

```powershell
workon test
pytest -v
```

The default database is `articles.db`. Set `DATABASE_URL` to use a different SQLAlchemy database URL.
