-- ============================================================================
-- Skema Database PostgreSQL (Supabase) — Moolagi Susu (Tim A26-CS226)
-- Program Asah 2026 (Dicoding x GoTo)
-- ============================================================================
-- Cara pakai:
-- 1. Buka dashboard Supabase -> SQL Editor -> New Query
-- 2. Salin & jalankan seluruh isi file ini (schema.sql)
-- 3. Lanjutkan dengan menjalankan supabase/seed.sql untuk data demo awal
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Tabel Pengguna (kata sandi WAJIB disimpan dalam bentuk hash bcrypt)
CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('karyawan', 'cfo', 'owner')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Master Bahan Baku (takaran & lead_time ditandai is_assumption = TRUE sebelum dikonfirmasi PIC)
CREATE TABLE IF NOT EXISTS ingredients (
    id              TEXT PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    unit            TEXT NOT NULL,
    lead_time_days  INTEGER NOT NULL DEFAULT 1 CHECK (lead_time_days >= 0),
    is_critical     BOOLEAN NOT NULL DEFAULT FALSE,
    is_assumption   BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Master Menu Moolagi (Moo Basic, Moo Special, Moo Float)
CREATE TABLE IF NOT EXISTS menus (
    id              TEXT PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Master Resep / Takaran Bahan per Menu (ditandai is_assumption = TRUE sampai dikonfirmasi PIC)
CREATE TABLE IF NOT EXISTS recipes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_id         TEXT NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
    ingredient_id   TEXT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    qty_per_serving NUMERIC(12, 3) NOT NULL CHECK (qty_per_serving > 0),
    unit            TEXT NOT NULL,
    is_assumption   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (menu_id, ingredient_id)
);

-- 5. Log Pencatatan Stok Akhir Saat Closing (diisi karyawan via tablet)
CREATE TABLE IF NOT EXISTS stock_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_date        DATE NOT NULL,
    ingredient_id   TEXT NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    closing_stock   NUMERIC(12, 3) NOT NULL CHECK (closing_stock >= 0),
    restock_qty     NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (restock_qty >= 0),
    is_stockout_day BOOLEAN NOT NULL DEFAULT FALSE,
    notes           TEXT,
    recorded_by     TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_logs_date
    ON stock_logs (log_date DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_stock_logs_ingredient_date
    ON stock_logs (ingredient_id, log_date DESC, created_at DESC);

-- 6. Data Penjualan Harian (dummy / hasil impor CSV format Loyverse; operasional Senin-Jumat)
CREATE TABLE IF NOT EXISTS sales_daily (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_date       DATE NOT NULL,
    menu_id         TEXT NOT NULL REFERENCES menus(id) ON DELETE RESTRICT,
    qty_sold        INTEGER NOT NULL CHECK (qty_sold >= 0),
    is_event_day    BOOLEAN NOT NULL DEFAULT FALSE,
    is_stockout_day BOOLEAN NOT NULL DEFAULT FALSE,
    data_source     TEXT NOT NULL DEFAULT 'dummy' CHECK (data_source IN ('dummy', 'actual')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sale_date, menu_id, data_source)
);

CREATE INDEX IF NOT EXISTS idx_sales_daily_date
    ON sales_daily (sale_date DESC);

-- 7. Hasil Perhitungan Safety Stock & Reorder Point (ROP) + Sinyal Pemesanan
CREATE TABLE IF NOT EXISTS rop_results (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calc_date              DATE NOT NULL,
    ingredient_id          TEXT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    predicted_daily_demand NUMERIC(12, 3) NOT NULL CHECK (predicted_daily_demand >= 0),
    safety_stock           NUMERIC(12, 3) NOT NULL CHECK (safety_stock >= 0),
    reorder_point          NUMERIC(12, 3) NOT NULL CHECK (reorder_point >= 0),
    closing_stock          NUMERIC(12, 3) NOT NULL CHECK (closing_stock >= 0),
    needs_reorder          BOOLEAN NOT NULL DEFAULT FALSE,
    method_used            TEXT NOT NULL,
    formula_explanation    TEXT NOT NULL,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (calc_date, ingredient_id)
);

CREATE INDEX IF NOT EXISTS idx_rop_results_date_alert
    ON rop_results (calc_date DESC, needs_reorder);

-- 8. Ringkasan Kondisi Stok Harian (dari Gemini API lewat server, atau fallback template)
CREATE TABLE IF NOT EXISTS daily_summaries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    summary_date    DATE NOT NULL UNIQUE,
    summary_text    TEXT NOT NULL,
    source          TEXT NOT NULL CHECK (source IN ('gemini', 'template_fallback')),
    alert_count     INTEGER NOT NULL DEFAULT 0 CHECK (alert_count >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
