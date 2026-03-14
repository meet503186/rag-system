from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service
from sqlalchemy.orm import Session

def register_user(request: RegisterRequest, db: Session):
    return auth_service.register_user(request=request, db=db)

def login_user(request: LoginRequest, db: Session):
    return auth_service.login(request=request, db=db)