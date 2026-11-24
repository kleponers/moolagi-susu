from __future__ import annotations

from datetime import date, datetime, timezone
from functools import lru_cache
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import hash_password


def _default_seed_users() -> dict[str, dict[str, Any]]:
    demo_hash = hash_password("moolagi123")
    return {
        "karyawan": {
            "id": "usr-karyawan-01",
            "username": "karyawan",
            "full_name": "Karyawan Outlet Moolagi",
            "password_hash": demo_hash,
            "role": "karyawan",
            "is_active": True,
        },
        "cfo": {
            "id": "usr-cfo-01",
            "username": "cfo",
            "full_name": "CFO / Pembelian Moolagi",
            "password_hash": demo_hash,
            "role": "cfo",
            "is_active": True,
        },
        "owner": {
            "id": "usr-owner-01",
            "username": "owner",
            "full_name": "Pemilik Moolagi Susu",
            "password_hash": demo_hash,
            "role": "owner",
            "is_active": True,
        },
    }


def _default_seed_ingredients() -> dict[str, dict[str, Any]]:
    # Catatan: satuan & lead_time_days ditandai is_assumption=True sampai dikonfirmasi PIC Moolagi
    return {
        "ING-ESKRIM": {
            "id": "ING-ESKRIM",
            "code": "ING-ESKRIM",
            "name": "Es Krim Vanila",
            "unit": "scoop",
            "lead_time_days": 1,
            "is_critical": True,
            "is_assumption": True,
            "is_active": True,
        },
        "ING-SUSU": {
            "id": "ING-SUSU",
            "code": "ING-SUSU",
            "name": "Susu Pasteurisasi",
            "unit": "liter",
            "lead_time_days": 1,
            "is_critical": True,
            "is_assumption": True,
            "is_active": True,
        },
        "ING-GULA": {
            "id": "ING-GULA",
            "code": "ING-GULA",
            "name": "Gula Cair",
            "unit": "ml",
            "lead_time_days": 2,
            "is_critical": False,
            "is_assumption": True,
            "is_active": True,
        },
        "ING-PERISA": {
            "id": "ING-PERISA",
            "code": "ING-PERISA",
            "name": "Sirup / Perisa Varian",
            "unit": "ml",
            "lead_time_days": 2,
            "is_critical": False,
            "is_assumption": True,
            "is_active": True,
        },
        "ING-CUP": {
            "id": "ING-CUP",
            "code": "ING-CUP",
            "name": "Cup + Tutup + Sedotan",
            "unit": "pcs",
            "lead_time_days": 3,
            "is_critical": False,
            "is_assumption": True,
            "is_active": True,
        },
    }


class MemoryStore:
    """Penyimpanan in-memory untuk pengembangan & pengujian lokal tanpa kredensial Supabase."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._users = _default_seed_users()
        self._ingredients = _default_seed_ingredients()
        base_ts = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
        self._stock_logs: list[dict[str, Any]] = [
            {
                "id": "log-seed-01",
                "log_date": date(2026, 11, 20),
                "ingredient_id": "ING-ESKRIM",
                "ingredient_name": "Es Krim Vanila",
                "unit": "scoop",
                "closing_stock": 25.0,
                "restock_qty": 0.0,
                "is_stockout_day": False,
                "notes": "Seed data awal (asumsi)",
                "recorded_by": "karyawan",
                "created_at": base_ts,
            },
            {
                "id": "log-seed-02",
                "log_date": date(2026, 11, 20),
                "ingredient_id": "ING-SUSU",
                "ingredient_name": "Susu Pasteurisasi",
                "unit": "liter",
                "closing_stock": 14.5,
                "restock_qty": 0.0,
                "is_stockout_day": False,
                "notes": "Seed data awal (asumsi)",
                "recorded_by": "karyawan",
                "created_at": base_ts,
            },
            {
                "id": "log-seed-03",
                "log_date": date(2026, 11, 20),
                "ingredient_id": "ING-GULA",
                "ingredient_name": "Gula Cair",
                "unit": "ml",
                "closing_stock": 1800.0,
                "restock_qty": 0.0,
                "is_stockout_day": False,
                "notes": "Seed data awal (asumsi)",
                "recorded_by": "karyawan",
                "created_at": base_ts,
            },
            {
                "id": "log-seed-04",
                "log_date": date(2026, 11, 20),
                "ingredient_id": "ING-PERISA",
                "ingredient_name": "Sirup / Perisa Varian",
                "unit": "ml",
                "closing_stock": 1200.0,
                "restock_qty": 0.0,
                "is_stockout_day": False,
                "notes": "Seed data awal (asumsi)",
                "recorded_by": "karyawan",
                "created_at": base_ts,
            },
            {
                "id": "log-seed-05",
                "log_date": date(2026, 11, 20),
                "ingredient_id": "ING-CUP",
                "ingredient_name": "Cup + Tutup + Sedotan",
                "unit": "pcs",
                "closing_stock": 160.0,
                "restock_qty": 0.0,
                "is_stockout_day": False,
                "notes": "Seed data awal (asumsi)",
                "recorded_by": "karyawan",
                "created_at": base_ts,
            },
        ]

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        user = self._users.get(username)
        if user and user.get("is_active", True):
            return user
        return None

    def _latest_log_map(self) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        sorted_logs = sorted(
            self._stock_logs,
            key=lambda x: (x["log_date"], x["created_at"]),
            reverse=True,
        )
        for log in sorted_logs:
            ing_id = log["ingredient_id"]
            if ing_id not in latest:
                latest[ing_id] = log
        return latest

    def list_ingredients(self) -> list[dict[str, Any]]:
        latest_map = self._latest_log_map()
        result: list[dict[str, Any]] = []
        for ing in self._ingredients.values():
            if not ing.get("is_active", True):
                continue
            latest = latest_map.get(ing["id"])
            result.append(
                {
                    "id": ing["id"],
                    "code": ing["code"],
                    "name": ing["name"],
                    "unit": ing["unit"],
                    "lead_time_days": ing["lead_time_days"],
                    "is_critical": ing["is_critical"],
                    "is_assumption": ing["is_assumption"],
                    "latest_closing_stock": latest["closing_stock"] if latest else None,
                    "latest_log_date": latest["log_date"] if latest else None,
                }
            )
        return result

    def create_stock_closing(
        self,
        log_date: date,
        items: list[dict[str, Any]],
        user: dict[str, Any],
    ) -> list[dict[str, Any]]:
        # Validasi semua ID bahan terlebih dahulu agar penulisan bersifat atomik
        for item in items:
            if item["ingredient_id"] not in self._ingredients:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "INGREDIENT_NOT_FOUND",
                        "message": f"Bahan baku '{item['ingredient_id']}' tidak ditemukan.",
                    },
                )

        now = datetime.now(timezone.utc)
        created: list[dict[str, Any]] = []
        for item in items:
            ing = self._ingredients[item["ingredient_id"]]
            record = {
                "id": f"log-{uuid4().hex[:12]}",
                "log_date": log_date,
                "ingredient_id": ing["id"],
                "ingredient_name": ing["name"],
                "unit": ing["unit"],
                "closing_stock": float(item["closing_stock"]),
                "restock_qty": float(item.get("restock_qty", 0.0)),
                "is_stockout_day": bool(item.get("is_stockout_day", False)),
                "notes": item.get("notes"),
                "recorded_by": user["username"],
                "created_at": now,
            }
            self._stock_logs.append(record)
            created.append(record)
        return created

    def list_stock_history(
        self,
        ingredient_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        rows = list(self._stock_logs)
        if ingredient_id:
            rows = [r for r in rows if r["ingredient_id"] == ingredient_id]
        if date_from:
            rows = [r for r in rows if r["log_date"] >= date_from]
        if date_to:
            rows = [r for r in rows if r["log_date"] <= date_to]
        rows.sort(key=lambda x: (x["log_date"], x["created_at"]), reverse=True)
        return rows[:limit]

    def list_latest_stocks(self) -> list[dict[str, Any]]:
        latest_map = self._latest_log_map()
        ordered: list[dict[str, Any]] = []
        for ing_id in self._ingredients:
            if ing_id in latest_map:
                ordered.append(latest_map[ing_id])
        return ordered


class PostgresStore:
    """Penyimpanan PostgreSQL (Supabase) menggunakan psycopg v3."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def _connect(self):
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(self._database_url, row_factory=dict_row)

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        query = """
            SELECT id, username, full_name, password_hash, role, is_active
            FROM users
            WHERE username = %s AND is_active = TRUE
            LIMIT 1
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(query, (username,))
            row = cur.fetchone()
            return dict(row) if row else None

    def list_ingredients(self) -> list[dict[str, Any]]:
        query = """
            SELECT
                i.id,
                i.code,
                i.name,
                i.unit,
                i.lead_time_days,
                i.is_critical,
                i.is_assumption,
                sl.closing_stock AS latest_closing_stock,
                sl.log_date AS latest_log_date
            FROM ingredients i
            LEFT JOIN LATERAL (
                SELECT closing_stock, log_date
                FROM stock_logs
                WHERE ingredient_id = i.id
                ORDER BY log_date DESC, created_at DESC
                LIMIT 1
            ) sl ON TRUE
            WHERE i.is_active = TRUE
            ORDER BY i.is_critical DESC, i.name ASC
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [
                {
                    **dict(r),
                    "latest_closing_stock": (
                        float(r["latest_closing_stock"])
                        if r["latest_closing_stock"] is not None
                        else None
                    ),
                }
                for r in rows
            ]

    def create_stock_closing(
        self,
        log_date: date,
        items: list[dict[str, Any]],
        user: dict[str, Any],
    ) -> list[dict[str, Any]]:
        ing_ids = list({item["ingredient_id"] for item in items})
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, unit FROM ingredients WHERE id = ANY(%s) AND is_active = TRUE",
                (ing_ids,),
            )
            found = {row["id"]: dict(row) for row in cur.fetchall()}
            for item in items:
                if item["ingredient_id"] not in found:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "code": "INGREDIENT_NOT_FOUND",
                            "message": f"Bahan baku '{item['ingredient_id']}' tidak ditemukan.",
                        },
                    )

            created: list[dict[str, Any]] = []
            insert_sql = """
                INSERT INTO stock_logs (
                    log_date, ingredient_id, closing_stock, restock_qty,
                    is_stockout_day, notes, recorded_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id::text, log_date, ingredient_id, closing_stock,
                          restock_qty, is_stockout_day, notes, created_at
            """
            for item in items:
                cur.execute(
                    insert_sql,
                    (
                        log_date,
                        item["ingredient_id"],
                        item["closing_stock"],
                        item.get("restock_qty", 0.0),
                        item.get("is_stockout_day", False),
                        item.get("notes"),
                        user["id"],
                    ),
                )
                row = dict(cur.fetchone())
                ing = found[item["ingredient_id"]]
                created.append(
                    {
                        "id": row["id"],
                        "log_date": row["log_date"],
                        "ingredient_id": ing["id"],
                        "ingredient_name": ing["name"],
                        "unit": ing["unit"],
                        "closing_stock": float(row["closing_stock"]),
                        "restock_qty": float(row["restock_qty"]),
                        "is_stockout_day": row["is_stockout_day"],
                        "notes": row["notes"],
                        "recorded_by": user["username"],
                        "created_at": row["created_at"],
                    }
                )
            return created

    def list_stock_history(
        self,
        ingredient_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        clauses = ["TRUE"]
        params: list[Any] = []
        if ingredient_id:
            clauses.append("sl.ingredient_id = %s")
            params.append(ingredient_id)
        if date_from:
            clauses.append("sl.log_date >= %s")
            params.append(date_from)
        if date_to:
            clauses.append("sl.log_date <= %s")
            params.append(date_to)
        params.append(limit)

        query = f"""
            SELECT
                sl.id::text AS id,
                sl.log_date,
                sl.ingredient_id,
                i.name AS ingredient_name,
                i.unit,
                sl.closing_stock,
                sl.restock_qty,
                sl.is_stockout_day,
                sl.notes,
                u.username AS recorded_by,
                sl.created_at
            FROM stock_logs sl
            JOIN ingredients i ON i.id = sl.ingredient_id
            JOIN users u ON u.id = sl.recorded_by
            WHERE {' AND '.join(clauses)}
            ORDER BY sl.log_date DESC, sl.created_at DESC
            LIMIT %s
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [
                {
                    **dict(r),
                    "closing_stock": float(r["closing_stock"]),
                    "restock_qty": float(r["restock_qty"]),
                }
                for r in rows
            ]

    def list_latest_stocks(self) -> list[dict[str, Any]]:
        query = """
            SELECT DISTINCT ON (sl.ingredient_id)
                sl.id::text AS id,
                sl.log_date,
                sl.ingredient_id,
                i.name AS ingredient_name,
                i.unit,
                sl.closing_stock,
                sl.restock_qty,
                sl.is_stockout_day,
                sl.notes,
                u.username AS recorded_by,
                sl.created_at
            FROM stock_logs sl
            JOIN ingredients i ON i.id = sl.ingredient_id
            JOIN users u ON u.id = sl.recorded_by
            ORDER BY sl.ingredient_id, sl.log_date DESC, sl.created_at DESC
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [
                {
                    **dict(r),
                    "closing_stock": float(r["closing_stock"]),
                    "restock_qty": float(r["restock_qty"]),
                }
                for r in rows
            ]


@lru_cache
def get_store() -> MemoryStore | PostgresStore:
    settings = get_settings()
    if settings.storage_mode == "postgres":
        return PostgresStore(settings.database_url)
    return MemoryStore()
