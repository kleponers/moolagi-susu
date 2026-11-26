import { apiFetch, USE_MOCK } from "./client";
import { mockGetIngredients } from "./mock/ingredients.mock";
import type { IngredientsResponse } from "@/types/api";

export function getIngredients(token: string): Promise<IngredientsResponse> {
  if (USE_MOCK) return mockGetIngredients();

  return apiFetch<IngredientsResponse>("/ingredients", {
    method: "GET",
    token,
  });
}
