import { apiFetch, USE_MOCK } from "./client";
import { mockSaveClosingStock } from "./mock/stocks.mock";
import type {
  ClosingStockRequest,
  ClosingStockResponse,
} from "@/types/api";

export function saveClosingStock(
  payload: ClosingStockRequest,
  token: string
): Promise<ClosingStockResponse> {
  if (USE_MOCK) return mockSaveClosingStock(payload);

  return apiFetch<ClosingStockResponse>("/stocks/closing", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}