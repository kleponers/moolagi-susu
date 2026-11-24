# Data Science — Moolagi Susu (Data Dummy, EDA, Safety Stock & ROP)

**PJ Tahap Awal (21–22 Nov):**
- **Nugraheni:** Generator data dummy (`sales_dummy.csv`, `ingredients_master.csv`, `recipes_master.csv`, `stock_closing_dummy.csv`)
- **Nabil:** Eksplorasi data dummy (EDA) & draf rumus Safety Stock (SS) + Reorder Point (ROP)

## Acuan Wajib
- Ikuti format kolom 4 file CSV & kontrak modul Python ROP di [docs/api-contract.md](../docs/api-contract.md) Bagian 5.
- Fakta Moolagi dari wawancara:
  - Operasional outlet: **Senin–Jumat** (Sabtu–Minggu tutup).
  - 3 menu utama: **Moo Basic**, **Moo Special**, **Moo Float**.
  - Bahan kritis utama: **Es Krim** (untuk Moo Float) & **Susu Pasteurisasi**.
  - Frekuensi stockout es krim: **1–2x/minggu** (wajib tandai kolom `is_stockout_day` agar hari kehabisan tidak dihitung sebagai permintaan rendah).
- Seluruh takaran resep dan *lead time* sementara **wajib ditandai `is_assumption = true`** dan dicatat dalam daftar asumsi.
- Simpan dataset dummy v1 di `ds/data/` — **jangan pernah commit data asli/rahasia UMKM**.
- Hasil akhir perhitungan SS & ROP diserahkan sebagai **modul Python** (bukan notebook saja) agar mudah diintegrasikan ke `backend/`.
- Kerjakan di branch terpisah (misal `feat/ds-dummy-generator`, `feat/ds-eda-rop`).
