import { apiFetch, USE_MOCK } from "./client";
import { mockLogin } from "./mock/auth.mock";
import type { LoginRequest, LoginResponse } from "@/types/api";

export function login(payload: LoginRequest): Promise<LoginResponse> {
  if (USE_MOCK) return mockLogin(payload);
  return apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}