# Port Configuration

## Current Setup

### Frontend (Vite Dev Server)
- **Port**: `5173`
- **URL**: `http://localhost:5173`
- **Configuration**: [`vite.config.ts`](vite.config.ts) line 9
- **Terminal**: Terminal 1 (`npm run dev`)

### Backend (FastAPI/Uvicorn)
- **Port**: `8000`
- **URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Terminal**: Terminal 28 (`uvicorn app.main:app --port 8000`)

## Environment Variables

### Frontend `.env`
```
VITE_API_URL=http://localhost:8000
```

This tells the frontend where to find the backend API.

## Why These Ports?

- **5173** - Vite's default development server port
- **8000** - Common Python/FastAPI development port

## Accessing the Application

1. **Frontend UI**: Open browser to `http://localhost:5173`
2. **Backend API Docs**: Open browser to `http://localhost:8000/docs`

## No Port Conflicts

These ports are intentionally different to avoid conflicts:
- Frontend serves the React UI on 5173
- Backend serves the API on 8000
- Frontend makes API calls to backend at `http://localhost:8000`
