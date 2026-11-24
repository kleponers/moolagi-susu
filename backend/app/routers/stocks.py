from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user
from app.db.store import get_store
from app.schemas.stock import (
    StockClosingRequest,
    StockClosingResponse,
    StockHistoryResponse,
    StockLogOut,
)

router = APIRouter(prefix="/api/v1/stocks", tags=["Stocks"])


@router.post(
    "/closing",
    response_model=StockClosingResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_closing_stock(
    payload: StockClosingRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> StockClosingResponse:
    store = get_store()
    created = store.create_stock_closing(
        log_date=payload.log_date,
        items=[item.model_dump() for item in payload.items],
        user=current_user,
    )
    records = [StockLogOut(**row) for row in created]
    return StockClosingResponse(
        message="Pencatatan stok closing berhasil disimpan.",
        log_date=payload.log_date,
        saved_count=len(records),
        records=records,
    )


@router.get("/history", response_model=StockHistoryResponse)
def get_stock_history(
    ingredient_id: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: dict[str, Any] = Depends(get_current_user),
) -> StockHistoryResponse:
    store = get_store()
    rows = store.list_stock_history(
        ingredient_id=ingredient_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
    items = [StockLogOut(**row) for row in rows]
    return StockHistoryResponse(items=items, total=len(items))


@router.get("/latest", response_model=StockHistoryResponse)
def get_latest_stocks(
    _: dict[str, Any] = Depends(get_current_user),
) -> StockHistoryResponse:
    store = get_store()
    rows = store.list_latest_stocks()
    items = [StockLogOut(**row) for row in rows]
    return StockHistoryResponse(items=items, total=len(items))
