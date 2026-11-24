# Frontend — Moolagi Susu (Next.js + Tailwind CSS)

**PJ Tahap Awal (21–22 Nov):** Naura (kerangka Next.js + Tailwind, login & input stok mock) & Rafiqi (deploy Vercel).

## Acuan Wajib
- Baca [docs/api-contract.md](../docs/api-contract.md) untuk format request/response login (`POST /api/v1/auth/login`), daftar bahan (`GET /api/v1/ingredients`), dan pencatatan stok closing (`POST /api/v1/stocks/closing`).
- Utamakan tampilan **nyaman di tablet outlet** (tombol & font cukup besar, sederhana untuk karyawan awam digital) serta tetap responsif di ponsel dan laptop.
- **Jangan pernah commit** `.env.local` atau rahasia ke repo; gunakan `.env.example` dengan variabel seperti `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`.
- Kerjakan di branch terpisah (misal `feat/fe-init-login-stok`).
