# Company News Article API

FastAPI and SQLite service that stores company news, then uses Celery to classify and summarize it with deterministic Python rules. No AI or ML integration is used.

## Run

```powershell
workon test
pip install -r requirements-dev.txt

# Terminal 1: start Redis (or use an existing Redis server)
docker run --name company-news-redis -p 6379:6379 redis:7-alpine

# Terminal 2: start the worker (the solo pool is required on Windows)
celery -A app.task:celery_app worker --loglevel=info --pool=solo

# Terminal 3: start the API
uvicorn app.main:app --reload
```

Open Swagger UI at <http://127.0.0.1:8000/docs>.

## Test

```powershell
workon test
pytest -v
```

The default database is `articles.db`. Set `DATABASE_URL` to use a different SQLAlchemy database URL. Celery uses `redis://localhost:6379/0` by default; set `REDIS_URL` for another broker. The API and worker must use the same working directory or the same absolute `DATABASE_URL`.
