export type Role = "karyawan" | "cfo" | "owner";

export interface User {
  id: string;
  username: string;
  full_name: string;
  role: Role;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_in_minutes: number;
  user: User;
}

export interface ApiErrorDetail {
  field: string;
  message: string;
}

export interface ApiErrorBody {
  error: { code: string; message: string; details?: ApiErrorDetail[] };
}

export interface Ingredient {
  id: string;
  code: string;
  name: string;
  unit: string;
  lead_time_days: number;
  is_critical: boolean;
  is_assumption: boolean;
  latest_closing_stock: number | null;
  latest_log_date: string | null;
}

export interface IngredientsResponse {
  items: Ingredient[];
  total: number;
}

export interface ClosingStockItem {
  ingredient_id: string;
  closing_stock: number;
  restock_qty?: number;
  is_stockout_day?: boolean;
  notes?: string;
}

export interface ClosingStockRequest {
  log_date: string;
  items: ClosingStockItem[];
}

export interface ClosingStockRecord extends ClosingStockItem {
  id: string;
  log_date: string;
  ingredient_name: string;
  unit: string;
  restock_qty: number;
  is_stockout_day: boolean;
  recorded_by: string;
  created_at: string;
}

export interface ClosingStockResponse {
  message: string;
  log_date: string;
  saved_count: number;
  records: ClosingStockRecord[];
}