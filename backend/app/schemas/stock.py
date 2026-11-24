from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


class IngredientOut(BaseModel):
    id: str
    code: str
    name: str
    unit: str
    lead_time_days: int
    is_critical: bool
    is_assumption: bool
    latest_closing_stock: float | None = None
    latest_log_date: date | None = None


class IngredientListResponse(BaseModel):
    items: list[IngredientOut]
    total: int


class StockClosingItemIn(BaseModel):
    ingredient_id: str = Field(..., min_length=1)
    closing_stock: float
    restock_qty: float = 0.0
    is_stockout_day: bool = False
    notes: str | None = Field(default=None, max_length=300)

    @field_validator("ingredient_id")
    @classmethod
    def validate_ingredient_id(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("ID bahan baku wajib diisi.")
        return cleaned

    @field_validator("closing_stock")
    @classmethod
    def validate_closing_stock(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Stok akhir tidak boleh negatif.")
        return round(float(v), 3)

    @field_validator("restock_qty")
    @classmethod
    def validate_restock_qty(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Jumlah restock tidak boleh negatif.")
        return round(float(v), 3)


class StockClosingRequest(BaseModel):
    log_date: date
    items: list[StockClosingItemIn] = Field(..., min_length=1)


class StockLogOut(BaseModel):
    id: str
    log_date: date
    ingredient_id: str
    ingredient_name: str
    unit: str
    closing_stock: float
    restock_qty: float
    is_stockout_day: bool
    notes: str | None = None
    recorded_by: str
    created_at: datetime


class StockClosingResponse(BaseModel):
    message: str
    log_date: date
    saved_count: int
    records: list[StockLogOut]


class StockHistoryResponse(BaseModel):
    items: list[StockLogOut]
    total: int
