from typing import Any

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.store import get_store
from app.schemas.stock import IngredientListResponse, IngredientOut

router = APIRouter(prefix="/api/v1/ingredients", tags=["Ingredients"])


@router.get("", response_model=IngredientListResponse)
def list_ingredients(
    _: dict[str, Any] = Depends(get_current_user),
) -> IngredientListResponse:
    store = get_store()
    items = [IngredientOut(**row) for row in store.list_ingredients()]
    return IngredientListResponse(items=items, total=len(items))
