import uuid

from fastapi import HTTPException
from sqlite3 import IntegrityError

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest

def create_user(user_data: RegisterRequest, db: Session):
    try:
        existing = db.query(User).filter(User.email == user_data.email).first()

        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")


def get_user(email: str, db: Session):
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        return user
    
    except Exception as e:
        print("[ERROR] get user by email :- ", e)
        raise HTTPException(status_code=500, detail="Database error")

def get_user_by_id(user_id: str, db: Session):
    try:
        user_id = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return None

        return user
    except Exception as e:
        print("[ERROR] get user by id :- ", e)
        raise HTTPException(status_code=500, detail="Database error")