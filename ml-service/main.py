import datetime as dt
import statistics
from typing import List

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

SERVICE = "moolagi-ml-service"
VERSI = "0.1.0"
MODEL_NAMA = "moving_average_7d"
WINDOW = 7

app = FastAPI(title="Moolagi ML Service", version=VERSI)


# ---------- Skema sesuai Kontrak API v1.0 (bagian 4.2) ----------
class HistoryItem(BaseModel):
    date: dt.date
    usage: float = Field(..., ge=0)
    is_event_day: bool = False
    is_stockout_day: bool = False


class PredictRequest(BaseModel):
    ingredient_id: str = Field(..., min_length=1)
    horizon_days: int = Field(7, ge=1, le=30)
    history: List[HistoryItem] = Field(..., min_length=1)

    @field_validator("ingredient_id")
    @classmethod
    def ingredient_id_tidak_kosong(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("ingredient_id tidak boleh kosong")
        return v


class PredictionItem(BaseModel):
    date: dt.date
    predicted_usage: float


class PredictResponse(BaseModel):
    ingredient_id: str
    model_used: str
    horizon_days: int
    avg_daily_demand: float
    std_daily_demand: float
    predictions: List[PredictionItem]


# ---------- Logika baseline ----------
def hitung_baseline(history: List[HistoryItem]):
    """Rata-rata dan simpangan baku (sampel) dari maksimal 7 hari terakhir.

    Hari stockout diabaikan karena penjualan hari itu menekan angka pemakaian
    (permintaan sebenarnya lebih tinggi). Bila semua hari stockout, semua dipakai.
    """
    data = sorted(history, key=lambda h: h.date)
    normal = [h.usage for h in data if not h.is_stockout_day]
    sumber = normal if normal else [h.usage for h in data]
    jendela = sumber[-WINDOW:]
    rata = sum(jendela) / len(jendela)
    std = statistics.stdev(jendela) if len(jendela) > 1 else 0.0
    return data[-1].date, round(rata, 2), round(std, 2)


# ---------- Endpoint ----------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": SERVICE,
        "active_model": MODEL_NAMA,
        "version": VERSI,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    tanggal_terakhir, rata, std = hitung_baseline(req.history)
    prediksi = [
        PredictionItem(
            date=tanggal_terakhir + dt.timedelta(days=i),
            predicted_usage=rata,
        )
        for i in range(1, req.horizon_days + 1)
    ]
    return PredictResponse(
        ingredient_id=req.ingredient_id,
        model_used=MODEL_NAMA,
        horizon_days=req.horizon_days,
        avg_daily_demand=rata,
        std_daily_demand=std,
        predictions=prediksi,
    )


# ---------- Format error standar (Kontrak API bagian 1) ----------
@app.exception_handler(RequestValidationError)
async def validasi_handler(request: Request, exc: RequestValidationError):
    rincian = []
    for e in exc.errors():
        field = ".".join(str(p) for p in e["loc"] if p != "body")
        rincian.append({"field": field, "message": e["msg"]})
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input tidak valid. Periksa ingredient_id, horizon_days, dan history.",
                "details": rincian,
            }
        },
    )