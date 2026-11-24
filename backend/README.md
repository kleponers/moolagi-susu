# Backend Utama — Moolagi Susu (FastAPI)

**PJ Tahap Awal:** Kevin (kerangka, auth, stok, kontrak API, skema Supabase) & Rafiqi (deploy Render/Railway).

## Menjalankan Lokal (Python 3.12)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

- Health check: `GET http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- Jalankan test: `pytest -v`

## Mode Penyimpanan
- **Mode `memory` (default bila `DATABASE_URL` kosong):** langsung memakai data seed (3 akun demo + 5 bahan baku asumsi Moolagi). Cocok untuk pengembangan frontend & pengujian cepat tanpa setup kredensial.
- **Mode `postgres` (otomatis bila `DATABASE_URL` diisi):** membaca & menulis ke tabel PostgreSQL Supabase (`../supabase/schema.sql` & `../supabase/seed.sql`).

## Catatan Deploy (Render / Railway)
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set environment variables (`JWT_SECRET_KEY`, `CORS_ORIGINS`, `DATABASE_URL`, `ML_SERVICE_URL`, `GEMINI_API_KEY`) di dashboard platform deploy.
