# Moolagi Susu — Sistem Pencatatan & Peringatan Stok Bahan Baku

**Tim Capstone:** A26-CS226 (Program Asah 2026 — Dicoding x GoTo)  
**UMKM Mitra:** Moolagi Susu (Kantin Purple Corner, Kampus IPB Dramaga)  
**Judul Use Case:** *Digitalisasi Pencatatan dan Peringatan Stok Bahan Baku untuk Mencegah Menu Kehabisan di Moolagi Susu*

---

## Ringkasan Arsitektur

Aplikasi web prototipe (MVP) yang ramah tablet outlet untuk mencatat stok bahan baku saat *closing*, menghitung perkiraan pemakaian dari data penjualan, menentukan *Safety Stock* dan *Reorder Point (ROP)* berbasis prediksi/statistik, serta menampilkan daftar bahan yang perlu dipesan dan ringkasan harian berbahasa natural.

```text
[Tablet / Browser: Next.js + Tailwind]
                │  REST JSON + JWT Bearer
                ▼
[Backend Utama: Python FastAPI] ──────────► [PostgreSQL via Supabase]
       │                     │
       │ POST /predict       │ Server-side call (API key di server)
       ▼                     ▼
[ML Service: FastAPI]   [Gemini API + fallback template]
```

## Struktur Repositori

| Folder | Isi | Penanggung Jawab (Tahap Awal 21–22 Nov) |
|---|---|---|
| `frontend/` | Aplikasi web Next.js + Tailwind CSS (ramah tablet & responsif) | Naura (UI/mock), Rafiqi (deploy Vercel) |
| `backend/` | REST API utama Python FastAPI (auth, stok, ROP, jembatan ML & Gemini) | Kevin (kerangka/kontrak), Rafiqi (deploy Render/Railway) |
| `ml-service/` | Layanan REST API terpisah untuk model prediksi (`/health`, `/predict`) | Faizah |
| `ds/` | Generator data dummy, EDA, perhitungan Safety Stock & ROP (modul Python) | Nugraheni (generator dummy), Nabil (EDA & rumus SS/ROP) |
| `supabase/` | Skema SQL (`schema.sql`) & data awal (`seed.sql`) PostgreSQL Supabase | Kevin |
| `docs/` | Kontrak API beku (`api-contract.md`) & dokumentasi teknis bersama | Kevin & Semua |

## Menjalankan Backend Secara Lokal

Prasyarat: **Python 3.11 / 3.12** (disarankan 3.12 agar kompatibel dengan library ML & platform deploy).

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # atau cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- Health check: `http://localhost:8000/health`
- Dokumentasi Swagger interaktif: `http://localhost:8000/docs`
- Jalankan automated test: `pytest -v`

> Secara default (`DATABASE_URL` kosong), backend berjalan dalam **mode `memory`** dengan data *seed* asumsi sehingga frontend dan pengujian lokal bisa langsung jalan tanpa menunggu kredensial Supabase. Saat `DATABASE_URL` Supabase diisi di `.env`, backend otomatis memakai **mode `postgres`**.

## Akun Demo Lokal / Seed

Semua password disimpan dalam bentuk hash (bukan teks biasa):

| Peran | Username | Password Demo | Hak Akses Utama |
|---|---|---|---|
| Karyawan Outlet | `karyawan` | `moolagi123` | Input stok closing, lihat riwayat & master bahan |
| Pembelian (CFO) | `cfo` | `moolagi123` | Akses karyawan + daftar bahan perlu dipesan & dasbor |
| Pemilik (Owner) | `owner` | `moolagi123` | Akses CFO + ringkasan harian & parameter asumsi |

## Aturan Git & Keamanan Tim

1. **Dilarang keras commit** file `.env`, API key (Supabase/Gemini/Fonnte), password produksi, atau data asli/rahasia UMKM ke repositori.
2. Kerjakan fitur di **branch masing-masing** (contoh: `feat/fe-login-stok`, `feat/ds-dummy-generator`, `feat/ae-ml-baseline`), lalu buka Pull Request ke `main`.
3. Seluruh angka takaran resep dan *lead time* yang belum dikonfirmasi PIC Moolagi **wajib ditandai sebagai asumsi** (`is_assumption = true`).
4. Lihat [docs/api-contract.md](docs/api-contract.md) sebelum mengubah format endpoint atau kolom data.
