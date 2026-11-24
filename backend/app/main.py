from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routers import auth, health, ingredients, stocks

settings = get_settings()

app = FastAPI(
    title="Moolagi Susu Stock & ROP API",
    description="Backend REST API prototipe pencatatan dan peringatan stok bahan baku Moolagi Susu (Tim A26-CS226).",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", "Terjadi kesalahan pada permintaan.")
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": message, "details": []}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    details = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", []) if part != "body")
        raw_msg = err.get("msg", "Nilai tidak valid.")
        # Bersihkan prefix bawaan Pydantic v2 "Value error, "
        clean_msg = raw_msg.removeprefix("Value error, ")
        details.append({"field": loc or "body", "message": clean_msg})

    first_message = details[0]["message"] if details else "Data input tidak valid."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": first_message,
                "details": details,
            }
        },
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(ingredients.router)
app.include_router(stocks.router)
