import type { LoginResponse, User } from "@/types/api";

const KEY = "moolagi_auth";

export function saveAuth(res: LoginResponse) {
  localStorage.setItem(KEY, JSON.stringify({ token: res.access_token, user: res.user }));
}

export function getAuth(): { token: string; user: User } | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearAuth() {
  localStorage.removeItem(KEY);
}