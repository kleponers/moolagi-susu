-- ============================================================================
-- Data Seed Awal (Demo & Asumsi) — Moolagi Susu (Tim A26-CS226)
-- Jalankan SETELAH supabase/schema.sql di Supabase SQL Editor.
-- Catatan:
--   * Password seluruh akun demo di bawah ini adalah: moolagi123 (disimpan sebagai hash bcrypt)
--   * Seluruh takaran resep & lead_time ditandai is_assumption = TRUE sampai dikonfirmasi PIC
-- ============================================================================

-- 1. Akun Demo (3 peran: karyawan, cfo, owner)
INSERT INTO users (id, username, full_name, password_hash, role) VALUES
    ('usr-karyawan-01', 'karyawan', 'Karyawan Outlet Moolagi', '$2b$12$9YVgczUWs8Bc8Erh2bP5YuhdNpx8sCsARMmkXb.PgB1LIAgfmXfyK', 'karyawan'),
    ('usr-cfo-01',      'cfo',      'CFO / Pembelian Moolagi', '$2b$12$9YVgczUWs8Bc8Erh2bP5YuhdNpx8sCsARMmkXb.PgB1LIAgfmXfyK', 'cfo'),
    ('usr-owner-01',    'owner',    'Pemilik Moolagi Susu',    '$2b$12$9YVgczUWs8Bc8Erh2bP5YuhdNpx8sCsARMmkXb.PgB1LIAgfmXfyK', 'owner')
ON CONFLICT (id) DO NOTHING;

-- 2. Master Menu Moolagi (fakta wawancara: 3 menu utama)
INSERT INTO menus (id, code, name) VALUES
    ('MOO-BASIC',   'MOO-BASIC',   'Moo Basic'),
    ('MOO-SPECIAL', 'MOO-SPECIAL', 'Moo Special'),
    ('MOO-FLOAT',   'MOO-FLOAT',   'Moo Float')
ON CONFLICT (id) DO NOTHING;

-- 3. Master Bahan Baku (satuan & lead_time ditandai is_assumption = TRUE)
INSERT INTO ingredients (id, code, name, unit, lead_time_days, is_critical, is_assumption) VALUES
    ('ING-ESKRIM', 'ING-ESKRIM', 'Es Krim Vanila',        'scoop', 1, TRUE,  TRUE),
    ('ING-SUSU',   'ING-SUSU',   'Susu Pasteurisasi',     'liter', 1, TRUE,  TRUE),
    ('ING-GULA',   'ING-GULA',   'Gula Cair',             'ml',    2, FALSE, TRUE),
    ('ING-PERISA', 'ING-PERISA', 'Sirup / Perisa Varian', 'ml',    2, FALSE, TRUE),
    ('ING-CUP',    'ING-CUP',    'Cup + Tutup + Sedotan', 'pcs',   3, FALSE, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 4. Master Resep / Takaran per Porsi (ASUMSI sementara, mudah diubah setelah konfirmasi PIC)
INSERT INTO recipes (menu_id, ingredient_id, qty_per_serving, unit, is_assumption) VALUES
    -- Moo Basic: susu 0.25 L, gula 20 ml, cup 1 pcs
    ('MOO-BASIC',   'ING-SUSU',   0.250, 'liter', TRUE),
    ('MOO-BASIC',   'ING-GULA',  20.000, 'ml',    TRUE),
    ('MOO-BASIC',   'ING-CUP',    1.000, 'pcs',   TRUE),
    -- Moo Special: susu 0.25 L, perisa 25 ml, gula 15 ml, cup 1 pcs
    ('MOO-SPECIAL', 'ING-SUSU',   0.250, 'liter', TRUE),
    ('MOO-SPECIAL', 'ING-PERISA',25.000, 'ml',    TRUE),
    ('MOO-SPECIAL', 'ING-GULA',  15.000, 'ml',    TRUE),
    ('MOO-SPECIAL', 'ING-CUP',    1.000, 'pcs',   TRUE),
    -- Moo Float (produk unggulan): susu 0.22 L, es krim 1 scoop, perisa 15 ml, gula 15 ml, cup 1 pcs
    ('MOO-FLOAT',   'ING-SUSU',   0.220, 'liter', TRUE),
    ('MOO-FLOAT',   'ING-ESKRIM', 1.000, 'scoop', TRUE),
    ('MOO-FLOAT',   'ING-PERISA',15.000, 'ml',    TRUE),
    ('MOO-FLOAT',   'ING-GULA',  15.000, 'ml',    TRUE),
    ('MOO-FLOAT',   'ING-CUP',    1.000, 'pcs',   TRUE)
ON CONFLICT (menu_id, ingredient_id) DO NOTHING;

-- 5. Contoh Log Stok Awal (Jumat, 20 Nov 2026) agar tampilan riwayat langsung terisi
INSERT INTO stock_logs (log_date, ingredient_id, closing_stock, restock_qty, is_stockout_day, notes, recorded_by)
SELECT v.log_date::date, v.ingredient_id, v.closing_stock, 0, FALSE, 'Seed data awal (asumsi)', 'usr-karyawan-01'
FROM (VALUES
    ('2026-11-20', 'ING-ESKRIM',  25.0),
    ('2026-11-20', 'ING-SUSU',    14.5),
    ('2026-11-20', 'ING-GULA',  1800.0),
    ('2026-11-20', 'ING-PERISA',1200.0),
    ('2026-11-20', 'ING-CUP',    160.0)
) AS v(log_date, ingredient_id, closing_stock)
WHERE NOT EXISTS (
    SELECT 1 FROM stock_logs sl
    WHERE sl.log_date = v.log_date::date AND sl.ingredient_id = v.ingredient_id
);
