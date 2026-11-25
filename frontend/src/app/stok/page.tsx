
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getAuth } from "@/lib/auth-storage";
import { getIngredients } from "@/lib/api/ingredients";
import { saveClosingStock } from "@/lib/api/stocks";
import { ApiError } from "@/lib/api/client";

import type { Ingredient } from "@/types/api";

export default function StokPage() {
  const router = useRouter();

  const [token, setToken] = useState("");
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [stockInputs, setStockInputs] = useState<Record<string, string>>({});
  const [logDate, setLogDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Ambil tanggal lokal dan data bahan setelah komponen dimuat.
  useEffect(() => {
  const auth = getAuth();

  if (!auth?.token) {
    router.replace("/login");
    return;
  }

  const accessToken = auth.token;
  setToken(accessToken);

  const today = new Date();
  const localDate = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");

  setLogDate(localDate);

  async function loadIngredients() {
    try {
      const response = await getIngredients(accessToken);
      setIngredients(response.items);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Gagal mengambil daftar bahan."
      );
    } finally {
      setLoading(false);
    }
  }

  loadIngredients();
}, [router]);

  function handleStockChange(id: string, value: string) {
    setStockInputs((previous) => ({
      ...previous,
      [id]: value,
    }));

    setError("");
    setSuccess("");
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!logDate) {
      setError("Tanggal pencatatan wajib diisi.");
      return;
    }

    if (ingredients.length === 0) {
      setError("Tidak ada bahan yang dapat dicatat.");
      return;
    }

    // Validasi semua input sebelum dikirim.
    for (const ingredient of ingredients) {
      const value = stockInputs[ingredient.id];

      if (value === undefined || value.trim() === "") {
        setError(`Stok ${ingredient.name} wajib diisi.`);
        return;
      }

      const numberValue = Number(value);

      if (!Number.isFinite(numberValue) || numberValue < 0) {
        setError(
          `Stok ${ingredient.name} harus berupa angka nol atau lebih.`
        );
        return;
      }
    }

    const payload = {
      log_date: logDate,
      items: ingredients.map((ingredient) => ({
        ingredient_id: ingredient.id,
        closing_stock: Number(stockInputs[ingredient.id]),
      })),
    };

    try {
      setSaving(true);

      const response = await saveClosingStock(payload, token);

      setSuccess(
        `${response.message} Total ${response.saved_count} bahan berhasil dicatat.`
      );
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Terjadi kesalahan. Silakan coba lagi.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-sm text-slate-500">Memuat daftar bahan...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8">
          <p className="mb-2 text-sm font-medium text-emerald-700">
            MOOLAGI SUSU · OPERASIONAL OUTLET
          </p>

          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Input Stok Closing
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Catat jumlah persediaan bahan setelah operasional outlet selesai.
          </p>
        </header>

        <form onSubmit={handleSubmit}>
          <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <label
              htmlFor="logDate"
              className="mb-2 block text-sm font-semibold text-slate-700"
            >
              Tanggal pencatatan
            </label>

            <input
              id="logDate"
              type="date"
              value={logDate}
              onChange={(e) => setLogDate(e.target.value)}
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 sm:w-64"
              required
            />
          </section>

          <section className="mb-6">
            <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
              <div>
                <h2 className="text-lg font-bold text-slate-900">
                  Daftar Bahan
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Masukkan stok akhir untuk setiap bahan.
                </p>
              </div>

              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                {ingredients.length} bahan
              </span>
            </div>

            {ingredients.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
                Belum ada data bahan.
              </div>
            ) : (
              <div className="space-y-3">
                {ingredients.map((ingredient) => (
                  <div
                    key={ingredient.id}
                    className="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[1fr_180px] sm:items-center"
                  >
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold text-slate-900">
                          {ingredient.name}
                        </h3>

                        {ingredient.is_critical && (
                          <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                            Kritis
                          </span>
                        )}
                      </div>

                      <p className="mt-1 text-xs text-slate-500">
                        Kode: {ingredient.code}
                      </p>

                      <p className="mt-2 text-sm text-slate-600">
                        Stok terakhir:{" "}
                        <span className="font-semibold">
                          {ingredient.latest_closing_stock ?? "-"}{" "}
                          {ingredient.unit}
                        </span>
                      </p>
                    </div>

                    <div>
                      <label
                        htmlFor={`stock-${ingredient.id}`}
                        className="mb-2 block text-sm font-medium text-slate-700"
                      >
                        Stok closing ({ingredient.unit})
                      </label>

                      <input
                        id={`stock-${ingredient.id}`}
                        type="number"
                        min="0"
                        step="any"
                        inputMode="decimal"
                        placeholder="Masukkan jumlah"
                        value={stockInputs[ingredient.id] ?? ""}
                        onChange={(e) =>
                          handleStockChange(ingredient.id, e.target.value)
                        }
                        className="w-full rounded-xl border border-slate-300 px-3 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
                        required
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {error && (
            <div
              role="alert"
              className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              role="status"
              className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
            >
              {success}
            </div>
          )}

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={() => router.refresh()}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Refresh
            </button>

            <button
              type="submit"
              disabled={saving || ingredients.length === 0}
              className="rounded-xl bg-emerald-700 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? "Menyimpan..." : "Simpan Stok Closing"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
