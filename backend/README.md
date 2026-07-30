# Synapse AI Backend

FastAPI server.

## Run

```bash
cd backend
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints
- `GET /api/health`
- `POST /api/upload` (multipart/form-data, PDF only)
- `POST /api/chat` (stub; no RAG yet)

