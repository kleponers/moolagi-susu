# Kontrak API & Format Data v1.0 — Moolagi Susu (Tim A26-CS226)

**Status:** Beku v1.0 (22 November 2026)  
**Acuan bersama:** Frontend (Naura), Deploy (Rafiqi), Backend (Kevin), Data Science (Nugraheni & Nabil), Next-Gen AI Engineer (Faizah).

> Setiap perubahan endpoint atau nama field JSON setelah tanggal beku wajib disepakati bersama di grup tim agar integrasi tidak patah.

---

## 1. Konvensi Umum

- **Base URL Backend:** `http://localhost:8000` (lokal) atau URL deploy Render/Railway; prefix API: `/api/v1`
- **Base URL ML Service (terpisah):** `http://localhost:8001` (lokal) atau URL deploy terpisah
- **Format Data:** `Content-Type: application/json`, tanggal ISO 8601 (`YYYY-MM-DD`), timestamp UTC ISO 8601
- **Autentikasi:** Header `Authorization: Bearer <access_token>` (JWT)
- **Peran Pengguna (`role`):**
  - `karyawan`: catat stok closing, lihat riwayat stok, lihat daftar bahan
  - `cfo`: akses `karyawan` + daftar bahan perlu dipesan (sinyal ROP) & dasbor
  - `owner`: akses `cfo` + ringkasan harian generatif & ubah parameter asumsi

### Format Error Standar

Seluruh error validasi, autentikasi, atau server menggunakan struktur konsisten agar frontend mudah menampilkan pesan yang jelas bagi karyawan outlet:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid. Pastikan stok akhir berupa angka 0 atau lebih.",
    "details": [
      {
        "field": "items.0.closing_stock",
        "message": "Stok akhir tidak boleh negatif"
      }
    ]
  }
}
```

Kode status HTTP utama: `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`.

---

## 2. Endpoint Backend Utama — Tahap 1 (Aktif di Kerangka 21–22 Nov)

### 2.1 Health Check
- **Endpoint:** `GET /health`
- **Auth:** Tidak perlu (publik, dipakai monitor deploy & cek CORS)
- **Response `200 OK`:**
```json
{
  "status": "ok",
  "service": "moolagi-backend",
  "version": "0.1.0",
  "storage_mode": "memory",
  "timestamp": "2026-11-22T07:30:00Z"
}
```

### 2.2 Login
- **Endpoint:** `POST /api/v1/auth/login`
- **Auth:** Tidak perlu
- **Request:**
```json
{
  "username": "karyawan",
  "password": "moolagi123"
}
```
- **Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in_minutes": 480,
  "user": {
    "id": "usr-karyawan-01",
    "username": "karyawan",
    "full_name": "Karyawan Outlet Moolagi",
    "role": "karyawan"
  }
}
```
- **Error:**
  - `422`: `username` atau `password` kosong
  - `401`: kredensial salah (`code: "INVALID_CREDENTIALS"`, pesan jelas: `"Username atau kata sandi salah."`)

### 2.3 Profil Pengguna Aktif
- **Endpoint:** `GET /api/v1/auth/me`
- **Auth:** Wajib Bearer token
- **Response `200 OK`:**
```json
{
  "id": "usr-karyawan-01",
  "username": "karyawan",
  "full_name": "Karyawan Outlet Moolagi",
  "role": "karyawan"
}
```
- **Error `401`:** Token kosong, rusak, atau kedaluwarsa (frontend otomatis alihkan ke halaman login).

### 2.4 Daftar Master Bahan Baku
- **Endpoint:** `GET /api/v1/ingredients`
- **Auth:** Wajib Bearer token (`karyawan`, `cfo`, `owner`)
- **Response `200 OK`:**
```json
{
  "items": [
    {
      "id": "ING-ESKRIM",
      "code": "ING-ESKRIM",
      "name": "Es Krim Vanila",
      "unit": "scoop",
      "lead_time_days": 1,
      "is_critical": true,
      "is_assumption": true,
      "latest_closing_stock": 25.0,
      "latest_log_date": "2026-11-20"
    }
  ],
  "total": 5
}
```

### 2.5 Pencatatan Stok Akhir Saat Closing
- **Endpoint:** `POST /api/v1/stocks/closing`
- **Auth:** Wajib Bearer token (`karyawan`, `cfo`, `owner`)
- **Catatan UI Tablet:** Mendukung pengiriman banyak bahan sekaligus dalam satu klik tombol **Simpan** (array `items` minimal 1 item).
- **Request:**
```json
{
  "log_date": "2026-11-22",
  "items": [
    {
      "ingredient_id": "ING-ESKRIM",
      "closing_stock": 18.0,
      "restock_qty": 0,
      "is_stockout_day": false,
      "notes": "Sisa closing sore"
    },
    {
      "ingredient_id": "ING-SUSU",
      "closing_stock": 12.5,
      "restock_qty": 0,
      "is_stockout_day": false
    }
  ]
}
```
- **Aturan Validasi Ketat:**
  - `items` tidak boleh kosong.
  - `ingredient_id` harus ada di master bahan (`404` jika tidak ditemukan).
  - `closing_stock` wajib angka dan `>= 0` (nilai kosong/`null`, teks, atau negatif seperti `-3` ditolak `422` dengan pesan jelas, dan **tidak ada data yang tersimpan**).
  - `restock_qty` opsional, default `0`, tidak boleh negatif (`>= 0`).
- **Response `201 Created`:**
```json
{
  "message": "Pencatatan stok closing berhasil disimpan.",
  "log_date": "2026-11-22",
  "saved_count": 2,
  "records": [
    {
      "id": "log-...",
      "log_date": "2026-11-22",
      "ingredient_id": "ING-ESKRIM",
      "ingredient_name": "Es Krim Vanila",
      "unit": "scoop",
      "closing_stock": 18.0,
      "restock_qty": 0.0,
      "is_stockout_day": false,
      "notes": "Sisa closing sore",
      "recorded_by": "karyawan",
      "created_at": "2026-11-22T10:15:00Z"
    }
  ]
}
```

### 2.6 Riwayat Pencatatan Stok
- **Endpoint:** `GET /api/v1/stocks/history?ingredient_id=ING-ESKRIM&date_from=2026-11-01&date_to=2026-11-30&limit=50`
- **Auth:** Wajib Bearer token (`karyawan`, `cfo`, `owner`)
- **Response `200 OK`:**
```json
{
  "items": [
    {
      "id": "log-...",
      "log_date": "2026-11-22",
      "ingredient_id": "ING-ESKRIM",
      "ingredient_name": "Es Krim Vanila",
      "unit": "scoop",
      "closing_stock": 18.0,
      "restock_qty": 0.0,
      "is_stockout_day": false,
      "notes": "Sisa closing sore",
      "recorded_by": "karyawan",
      "created_at": "2026-11-22T10:15:00Z"
    }
  ],
  "total": 1
}
```

### 2.7 Stok Terakhir Per Bahan
- **Endpoint:** `GET /api/v1/stocks/latest`
- **Auth:** Wajib Bearer token (`karyawan`, `cfo`, `owner`)
- **Response `200 OK`:** Daftar kondisi stok terakhir tiap bahan (berguna untuk ringkasan cepat & pre-fill konteks di tablet).

---

## 3. Endpoint Backend Utama — Tahap 2 (Target Minggu 1–2: 23 Nov–3 Des)

Kontrak dibekukan lebih awal supaya Frontend, DS, dan AE bisa bekerja paralel:

| Endpoint | Role | Fungsi Singkat |
|---|---|---|
| `GET /api/v1/stocks/variance?date=YYYY-MM-DD` | `cfo`, `owner` | Perkiraan stok dari penjualan × takaran resep vs stok fisik (menampilkan selisih) |
| `GET /api/v1/rop/alerts` | `cfo`, `owner` | Daftar bahan yang `closing_stock <= reorder_point`, nilai SS & ROP, `method_used` (`ml_prediction` / `moving_average_fallback`), dan penjelasan rumus |
| `GET /api/v1/summary/daily?date=YYYY-MM-DD` | `cfo`, `owner` | Ringkasan kondisi stok berbahasa natural (dipanggil lewat server ke Gemini API, fallback ke `template_fallback` bila gagal) |
| `GET /api/v1/analytics/dashboard` | `cfo`, `owner` | Data grafik tren pemakaian harian, stok vs ROP, dan kejadian stockout untuk dasbor analisis DS |

---

## 4. Kontrak ML Service Terpisah (`ml-service` — Bagian Faizah / AE)

Backend utama memanggil layanan ini secara *server-to-server* dengan timeout pendek (misal 5 detik). Bila layanan mati/timeout, backend otomatis memakai fallback rata-rata bergerak historis.

### 4.1 `GET /health`
```json
{
  "status": "ok",
  "service": "moolagi-ml-service",
  "active_model": "moving_average_7d",
  "version": "0.1.0"
}
```

### 4.2 `POST /predict`
- **Request:**
```json
{
  "ingredient_id": "ING-ESKRIM",
  "horizon_days": 7,
  "history": [
    {
      "date": "2026-11-16",
      "usage": 20.0,
      "is_event_day": false,
      "is_stockout_day": false
    },
    {
      "date": "2026-11-17",
      "usage": 24.0,
      "is_event_day": true,
      "is_stockout_day": false
    }
  ]
}
```
- **Response `200 OK`:**
```json
{
  "ingredient_id": "ING-ESKRIM",
  "model_used": "moving_average_7d",
  "horizon_days": 7,
  "avg_daily_demand": 22.0,
  "std_daily_demand": 2.83,
  "predictions": [
    { "date": "2026-11-23", "predicted_usage": 22.0 }
  ]
}
```
- **Error `422`:** bila `ingredient_id` kosong, `horizon_days < 1`, atau `history` kosong/tidak valid.

---

## 5. Kontrak Format Data & Modul DS (`ds/` — Bagian Nugraheni & Nabil)

### 5.1 Skema 4 File CSV Dummy v1 (Fokus Operasional Senin–Jumat)

1. `sales_dummy.csv` *(meniru struktur export item sales Loyverse)*  
   `date,menu_name,qty_sold,is_event_day,is_stockout_day`
2. `ingredients_master.csv` *(takaran & lead time ditandai asumsi)*  
   `ingredient_id,ingredient_name,unit,lead_time_days,initial_stock,is_assumption`
3. `recipes_master.csv` *(asumsi)*  
   `menu_name,ingredient_id,qty_per_serving,unit,is_assumption`
4. `stock_closing_dummy.csv`  
   `date,ingredient_id,closing_stock,restock_qty,is_stockout_day`

### 5.2 Kontrak Modul Python ROP (Target Integrasi Minggu 1–2)

Output perhitungan DS diserahkan sebagai modul Python (bukan notebook saja) dengan signature dasar:

```python
def calculate_rop(
    daily_usage: list[float],
    lead_time_days: int,
    predicted_daily_demand: float | None = None,
    service_level: float = 0.95,
    method: str = "empirical_percentile",
) -> dict:
    """
    Returns:
      {
        "avg_daily_demand": float,
        "safety_stock": float,
        "reorder_point": float,
        "method_used": str,
        "formula_explanation": str
      }
    """
```
