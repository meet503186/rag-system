from app.repositories.auth_repository import create_user, get_user
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.jwt import create_access_token
from app.utils.security import hash_password, verify_password
from sqlalchemy.orm import Session

def register_user(request: RegisterRequest, db: Session):
    request.password = hash_password(request.password)
    user = create_user(user_data=request, db=db)
    return { user }

def login(request: LoginRequest, db: Session):
    user = get_user(email=request.email, db=db)
    
    if not user:
        return None

    if not verify_password(request.password, user.password):
        return None

    token = create_access_token({"user_id": str(user.id)})

    return { token }