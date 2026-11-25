"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { saveAuth } from "@/lib/auth-storage";

type FieldErrors = { username?: string; password?: string };

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setFormError("");

    const errs: FieldErrors = {};
    if (!username.trim()) errs.username = "Username wajib diisi.";
    if (!password) errs.password = "Kata sandi wajib diisi.";
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setLoading(true);
    try {
      const res = await login({ username: username.trim(), password });
      saveAuth(res);
      router.replace("/stok");
    } catch (err) {
      if (err instanceof ApiError) {
        const mapped: FieldErrors = {};
        err.details.forEach((d) => {
          if (d.field === "username" || d.field === "password") mapped[d.field] = d.message;
        });
        setFieldErrors(mapped);
        setFormError(err.message);
      } else {
        setFormError("Terjadi kesalahan. Silakan coba lagi.");
      }
    } finally {
      setLoading(false);
    }
  }

  const inputBase =
    "w-full h-14 rounded-xl border-2 px-4 text-xl outline-none focus:ring-4 focus:ring-blue-200";

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <form
        onSubmit={handleSubmit}
        noValidate
        className="w-full max-w-md space-y-6 rounded-2xl bg-white p-8 shadow-lg"
      >
        <header className="text-center">
          <h1 className="text-3xl font-bold text-slate-800">Moolagi Susu</h1>
          <p className="mt-2 text-lg text-slate-600">Masuk untuk catat stok closing</p>
        </header>

        {formError && (
          <div role="alert" className="rounded-xl bg-red-50 border-2 border-red-300 p-4 text-lg text-red-700">
            {formError}
          </div>
        )}

        <div>
          <label htmlFor="username" className="block mb-2 text-lg font-semibold text-slate-700">
            Username
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            aria-invalid={!!fieldErrors.username}
            className={`${inputBase} ${fieldErrors.username ? "border-red-500" : "border-slate-300"}`}
          />
          {fieldErrors.username && <p className="mt-2 text-lg text-red-600">{fieldErrors.username}</p>}
        </div>

        <div>
          <label htmlFor="password" className="block mb-2 text-lg font-semibold text-slate-700">
            Kata sandi
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={!!fieldErrors.password}
            className={`${inputBase} ${fieldErrors.password ? "border-red-500" : "border-slate-300"}`}
          />
          {fieldErrors.password && <p className="mt-2 text-lg text-red-600">{fieldErrors.password}</p>}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full h-14 rounded-xl bg-blue-600 text-xl font-bold text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? "Memproses..." : "Masuk"}
        </button>
      </form>
    </main>
  );
}