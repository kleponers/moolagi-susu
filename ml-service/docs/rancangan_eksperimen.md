# Rancangan Eksperimen Model Prediksi Kebutuhan Bahan

Tim A26-CS226 — Moolagi Susu | Penanggung jawab: Faizah (AE)

## 1. Tujuan
Memprediksi **pemakaian harian tiap bahan baku** (mis. es krim, susu pasteurisasi) untuk 1–7 hari ke depan.
Hasil prediksi dan ukuran galatnya dipakai tim DS untuk menghitung Safety Stock dan Reorder Point (ROP),
lalu backend menandai bahan yang perlu dipesan.

## 2. Data
- Sumber: data dummy buatan DS (format kolom mirip Loyverse POS). Data asli Moolagi belum diserahkan PIC.
  Semua angka dummy dan takaran resep adalah **asumsi tim**, bukan data dari UMKM.
- Satu baris = satu bahan pada satu hari.
- Kolom yang dibutuhkan model:

| Kolom (`history` di `/predict`) | Keterangan |
|---|---|
| `date` | Tanggal harian (YYYY-MM-DD) |
| `usage` | Pemakaian bahan pada hari itu (target), >= 0 |
| `is_event_day` | Penanda hari event kampus |
| `is_stockout_day` | Penanda hari menu kehabisan (permintaan sebenarnya bisa lebih tinggi) |

- `ingredient_id` dikirim terpisah di request (mis. `ING-ESKRIM`). Data latih berasal dari `sales_dummy.csv`,
  `recipes_master.csv`, dan `ingredients_master.csv` (modul DS).
- Catatan: hari stockout menekan angka penjualan sehingga pemakaian tampak lebih rendah. Hari ini ditandai
  dan diperlakukan khusus (mis. dikeluarkan dari data latih atau dikoreksi), bukan dianggap permintaan normal.

## 3. Target dan fitur
- **Target:** `usage` per bahan per hari.
- **Fitur:**
  - pemakaian 1, 7 hari sebelumnya (lag), rata-rata bergerak 7 hari
  - hari dalam minggu (Senin–Minggu)
  - penanda hari libur nasional
  - penanda minggu ujian (UTS/UAS kampus)
  - penanda hari event kampus (`is_event_day`)
- Model dilatih **per bahan** (satu model per bahan, atau satu model dengan fitur `ingredient_id`; dipilih saat eksperimen).

## 4. Model yang dibandingkan
Semua model dilatih sendiri (bukan model siap pakai, bukan AutoML).

| No | Model | Peran |
|---|---|---|
| 1 | Rata-rata bergerak 7 hari (`moving_average_7d`) | **Baseline** (sudah ada di `/predict` v0.1.0) |
| 2 | Random Forest / XGBoost (regresi tabular) | Model utama kandidat |
| 3 | SARIMA | Model deret waktu pembanding |
| 4 | LSTM | Opsional, hanya bila waktu cukup |

## 5. Validasi dan metrik
- **Validasi berbasis waktu**, bukan acak: data latih diambil dari periode awal, data uji dari periode setelahnya.
  Dipakai walk-forward validation (jendela bertambah, uji pada beberapa hari berikutnya).
- **Metrik sama untuk semua model:** MAE, RMSE, MAPE.
  - Bila ada hari dengan pemakaian 0, MAPE tidak stabil; hitung MAPE hanya pada hari bernilai > 0
    atau tambahkan sMAPE sebagai pelengkap.
- **Metrik bisnis (bersama DS):** perkiraan jumlah stockout per minggu bila ROP memakai prediksi tiap model.
- Seed acak dicatat supaya hasil dapat diulang.

## 6. Tabel hasil (diisi setelah eksperimen, lalu dipindahkan ke README.md)

| Model | Bahan | MAE | RMSE | MAPE | Catatan |
|---|---|---|---|---|---|
| Rata-rata bergerak 7 hari (baseline) | | | | | |
| Random Forest / XGBoost | | | | | |
| SARIMA | | | | | |

## 7. Kriteria memilih model
1. Galat uji (MAE/RMSE) lebih rendah dari baseline secara konsisten di beberapa jendela validasi.
2. Bila selisih kecil, pilih model **paling sederhana** dan paling mudah dilayani lewat REST API.
3. Bila tidak ada model yang mengalahkan baseline, backend memakai rata-rata bergerak untuk ROP
   dan hal ini dicatat jujur di README beserta alasannya.
4. Hasil pada data dummy dilaporkan sebagai **uji alur**, bukan klaim performa di Moolagi.

## 8. Kontrak API layanan model (mengikuti docs/api-contract.md Bagian 4, beku 22 Nov 2026)

Layanan model berjalan terpisah dari backend utama (lokal: `http://localhost:8001`) dan dipanggil backend
secara server-to-server dengan timeout pendek (sekitar 5 detik). Bila layanan mati atau timeout, backend memakai
fallback rata-rata bergerak historis.

### `GET /health`
```json
{
  "status": "ok",
  "service": "moolagi-ml-service",
  "active_model": "moving_average_7d",
  "version": "0.1.0"
}
```

### `POST /predict` — request
```json
{
  "ingredient_id": "ING-ESKRIM",
  "horizon_days": 7,
  "history": [
    { "date": "2026-11-16", "usage": 20.0, "is_event_day": false, "is_stockout_day": false },
    { "date": "2026-11-17", "usage": 24.0, "is_event_day": true,  "is_stockout_day": false }
  ]
}
```

### `POST /predict` — response 200
```json
{
  "ingredient_id": "ING-ESKRIM",
  "model_used": "moving_average_7d",
  "horizon_days": 7,
  "avg_daily_demand": 22.0,
  "std_daily_demand": 2.83,
  "predictions": [
    { "date": "2026-11-18", "predicted_usage": 22.0 }
  ]
}
```
`avg_daily_demand` dan `std_daily_demand` dipakai modul DS untuk menghitung safety stock dan reorder point.
Pada baseline, keduanya dihitung dari maksimal 7 hari terakhir dengan hari stockout diabaikan
(simpangan baku sampel). Tanggal prediksi dimulai sehari setelah tanggal terakhir pada `history`.

### `POST /predict` — response 422 (format error standar kontrak)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid. Periksa ingredient_id, horizon_days, dan history.",
    "details": [
      { "field": "history.0.usage", "message": "Input should be greater than or equal to 0" }
    ]
  }
}
```

Aturan validasi: `ingredient_id` tidak boleh kosong; `horizon_days` 1–30; `history` minimal 1 data;
`usage` tidak boleh negatif; `date` harus tanggal ISO 8601.

## 9. Mekanisme cadangan
- Layanan model tidak merespons atau tidak mengalahkan baseline: backend memakai rata-rata bergerak untuk ROP.
- Sinyal pemesanan tetap dihitung terpisah dari model generatif.

## 10. Rencana kerja
| Tanggal | Pekerjaan |
|---|---|
| 23–29 Nov | EDA, preprocessing, fitur; latih model selain baseline; split berbasis waktu |
| 30 Nov–3 Des | Bandingkan minimal 2 model, isi tabel hasil di README.md, pilih model, finalkan `/predict` |
| 3 Des | Layanan model terintegrasi dengan backend dan online |