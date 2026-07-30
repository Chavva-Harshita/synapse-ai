# Synapse AI

Modern full-stack starter (Frontend: React+Vite+TailwindCSS, Backend: FastAPI).

## Folder structure
- `frontend/` - React app
- `backend/` - FastAPI server

## Prerequisites
- Node.js (for frontend)
- Python 3.10+ (for backend)

## Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend base URL (default): `http://localhost:8000`

## Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend base URL (default): `http://localhost:5173`

## Notes
- This is a foundation only (no RAG yet).
- Chat and file upload are stubbed/minimally implemented.

