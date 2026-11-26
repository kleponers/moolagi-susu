# ML Service — Moolagi Susu (REST API Prediksi Kebutuhan Bahan)

**PJ:** Faizah (Next-Gen AI Engineer).

## Acuan Wajib
- Layanan **terpisah** dari `backend/` (Python FastAPI) lengkap dengan `requirements.txt` berversi jelas (disarankan Python 3.12).
- Ikuti kontrak endpoint di [docs/api-contract.md](../docs/api-contract.md) Bagian 4:
  - `GET /health` → status layanan & nama model aktif
  - `POST /predict` → prediksi kebutuhan bahan harian (tolak input tidak lengkap dengan `422` + pesan jelas)
- **Target 21–22 Nov:** kerangka service + baseline rata-rata bergerak (misal 7 hari).
- **Target Minggu 1–2:** bandingkan minimal 2 model (misal Random Forest/XGBoost & SARIMA) dengan validasi berbasis waktu (*walk-forward*), metrik MAE/RMSE/MAPE, dan tulis tabel perbandingan + alasan pemilihan model di `README.md`.
- Kerjakan di branch terpisah (misal `feat/ae-ml-service-baseline`).

## Status Saat Ini
- Baseline rata-rata bergerak 7 hari (`moving_average_7d`) aktif di `POST /predict`.
- Hari dengan `is_stockout_day: true` tidak dihitung dalam rata-rata karena pemakaiannya lebih rendah dari permintaan sebenarnya.
- Rancangan perbandingan model: [docs/rancangan_eksperimen.md](docs/rancangan_eksperimen.md).
- Tabel perbandingan model dan alasan pemilihan akan ditambahkan setelah eksperimen (Minggu 1–2).

## Menjalankan Secara Lokal
```bash
cd ml-service
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1   |   Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
Buka `http://127.0.0.1:8001/docs` untuk mencoba endpoint.