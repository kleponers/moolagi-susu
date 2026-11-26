import { ApiError } from "../client";
import type { ApiErrorDetail, LoginRequest, LoginResponse } from "@/types/api";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function mockLogin({ username, password }: LoginRequest): Promise<LoginResponse> {
  await sleep(500);

  const details: ApiErrorDetail[] = [];
  if (!username.trim()) details.push({ field: "username", message: "Username wajib diisi." });
  if (!password) details.push({ field: "password", message: "Kata sandi wajib diisi." });
  if (details.length) {
    throw new ApiError(422, "VALIDATION_ERROR", "Username dan kata sandi wajib diisi.", details);
  }

  if (username !== "karyawan" || password !== "moolagi123") {
    throw new ApiError(401, "INVALID_CREDENTIALS", "Username atau kata sandi salah.");
  }

  return {
    access_token: "mock-token-karyawan",
    token_type: "bearer",
    expires_in_minutes: 480,
    user: {
      id: "usr-karyawan-01",
      username: "karyawan",
      full_name: "Karyawan Outlet Moolagi",
      role: "karyawan",
    },
  };
}