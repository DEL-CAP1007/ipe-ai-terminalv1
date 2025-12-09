from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from src.core.config import get_db
from services.auth.service import AuthService
from services.auth.identity import get_current_identity

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str
    user_agent: str = None
    client_ip: str = None

class LogoutRequest(BaseModel):
    pass

@router.post("/auth/login")
def login(req: LoginRequest):
    db = get_db()
    try:
        session = AuthService.login(
            db,
            email=req.email,
            password=req.password,
            user_agent=req.user_agent,
            client_ip=req.client_ip,
        )
        return {"session_id": str(session.id)}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/auth/logout")
def logout(session_id: str):
    db = get_db()
    AuthService.logout(db, session_id)
    return {"ok": True}

@router.get("/auth/whoami")
def whoami(session_id: str):
    db = get_db()
    identity = get_current_identity(db, session_id)
    if not identity:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return identity.__dict__
