from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.controllers.auth_controller import login_user, register_user
from app.schemas.auth import LoginRequest, RegisterRequest
from app.db.database import get_db

router = APIRouter(prefix="/auth")


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(request, db)


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):

    token = login_user(request, db)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": token}