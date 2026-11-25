import type {
  Ingredient,
  IngredientsResponse,
} from "@/types/api";

const mockIngredients: Ingredient[] = [
  {
    id: "ING-ESKRIM",
    code: "ING-ESKRIM",
    name: "Es Krim Vanila",
    unit: "scoop",
    lead_time_days: 1,
    is_critical: true,
    is_assumption: true,
    latest_closing_stock: 25,
    latest_log_date: "2026-11-24",
  },
  {
    id: "ING-SUSU",
    code: "ING-SUSU",
    name: "Susu UHT",
    unit: "liter",
    lead_time_days: 2,
    is_critical: true,
    is_assumption: false,
    latest_closing_stock: 12.5,
    latest_log_date: "2026-11-24",
  },
  {
    id: "ING-GULA",
    code: "ING-GULA",
    name: "Gula Pasir",
    unit: "kg",
    lead_time_days: 1,
    is_critical: false,
    is_assumption: false,
    latest_closing_stock: 8,
    latest_log_date: "2026-11-24",
  },
  {
    id: "ING-COKELAT",
    code: "ING-COKELAT",
    name: "Bubuk Cokelat",
    unit: "kg",
    lead_time_days: 2,
    is_critical: false,
    is_assumption: true,
    latest_closing_stock: 3.5,
    latest_log_date: "2026-11-24",
  },
  {
    id: "ING-CUP",
    code: "ING-CUP",
    name: "Cup Plastik",
    unit: "pcs",
    lead_time_days: 3,
    is_critical: false,
    is_assumption: false,
    latest_closing_stock: 100,
    latest_log_date: "2026-11-24",
  },
];

const sleep = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

export async function mockGetIngredients(): Promise<IngredientsResponse> {
  await sleep(400);

  return {
    items: mockIngredients,
    total: mockIngredients.length,
  };
}
