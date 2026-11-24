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
