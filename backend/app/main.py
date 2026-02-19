from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text

import os
import secrets

# =========================
# НАСТРОЙКИ БД
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# =========================
# SWAGGER AUTH (Basic Auth)
# =========================
security = HTTPBasic()

def require_swagger_auth(credentials: HTTPBasicCredentials = Depends(security)):
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "changeme123")

    is_user_ok = secrets.compare_digest(credentials.username, admin_user)
    is_pass_ok = secrets.compare_digest(credentials.password, admin_pass)

    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
headers={"WWW-Authenticate": "Basic"}

        )
    return True


# =========================
# FASTAPI (Swagger s паролem)
# =========================
app = FastAPI(
    title="tvoyaprofessiya API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
@app.get("/openapi.json", include_in_schema=False)
def openapi_json(auth: bool = Depends(require_swagger_auth)):
    return JSONResponse(app.openapi())

@app.get("/docs", include_in_schema=False)
def swagger_docs(auth: bool = Depends(require_swagger_auth)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger UI")

@app.get("/redoc", include_in_schema=False)
def redoc_docs(auth: bool = Depends(require_swagger_auth)):
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")

# =========================
# МОДЕЛИ
# =========================
class LeadCreate(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(min_length=5)
    email: Optional[EmailStr] = None
    direction: str = Field(min_length=1)
    message: Optional[str] = None


# =========================
# ИНИЦИАЛИЗАЦИЯ ТАБЛИЦЫ
# =========================
@app.on_event("startup")
def on_startup():
    # Создаём таблицу если нет
    ddl = """
    CREATE TABLE IF NOT EXISTS leads (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NULL,
        direction TEXT NOT NULL,
        message TEXT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))


# =========================
# ENDPOINTS
# =========================
@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/leads")
def create_lead(lead: LeadCreate) -> Dict[str, Any]:
    q = text("""
        INSERT INTO leads (name, phone, email, direction, message)
        VALUES (:name, :phone, :email, :direction, :message)
        RETURNING id, name, phone, email, direction, message, created_at;
    """)

    try:
        with engine.begin() as conn:
            row = conn.execute(q, {
                "name": lead.name,
                "phone": lead.phone,
                "email": str(lead.email) if lead.email is not None else None,
                "direction": lead.direction,
                "message": lead.message,
            }).mappings().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return dict(row)


@app.get("/leads")
def list_leads(limit: int = 50) -> List[Dict[str, Any]]:
    limit = max(1, min(limit, 500))
    q = text("""
        SELECT id, name, phone, email, direction, message, created_at
        FROM leads
        ORDER BY created_at DESC
        LIMIT :limit;
    """)
    with engine.begin() as conn:
        rows = conn.execute(q, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]


@app.get("/leads/{lead_id}")
def get_lead(lead_id: int) -> Dict[str, Any]:
    q = text("""
        SELECT id, name, phone, email, direction, message, created_at
        FROM leads
        WHERE id = :id;
    """)
    with engine.begin() as conn:
        row = conn.execute(q, {"id": lead_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")

    return dict(row)

