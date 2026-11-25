import { ApiError } from "../client";
import type {
  ClosingStockRequest,
  ClosingStockResponse,
} from "@/types/api";

const sleep = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

export async function mockSaveClosingStock(
  payload: ClosingStockRequest
): Promise<ClosingStockResponse> {
  await sleep(500);

  if (!payload.items.length) {
    throw new ApiError(
      422,
      "VALIDATION_ERROR",
      "Minimal satu bahan harus diisi."
    );
  }

  for (const item of payload.items) {
    if (
      item.closing_stock === null ||
      item.closing_stock === undefined ||
      !Number.isFinite(item.closing_stock) ||
      item.closing_stock < 0
    ) {
      throw new ApiError(
        422,
        "VALIDATION_ERROR",
        "Stok akhir harus berupa angka nol atau lebih."
      );
    }
  }

  return {
    message: "Stok closing berhasil disimpan.",
    log_date: payload.log_date,
    saved_count: payload.items.length,
    records: payload.items.map((item, index) => ({
      ...item,
      id: `MOCK-STOCK-${Date.now()}-${index}`,
      log_date: payload.log_date,
      ingredient_name: item.ingredient_id,
      unit: "unit",
      restock_qty: item.restock_qty ?? 0,
      is_stockout_day: item.is_stockout_day ?? false,
      recorded_by: "karyawan",
      created_at: new Date().toISOString(),
    })),
  };
}