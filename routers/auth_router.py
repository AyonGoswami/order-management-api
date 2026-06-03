from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import RegisterRequest, LoginRequest, ChangePasswordRequest, TokenResponse, UserResponse
from services.auth_service import register_user, login_user, change_password
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, request.email, request.full_name, request.password, request.role)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    tokens = login_user(db, request.email, request.password)
    return tokens


@router.post("/change_password")
def change_pwd(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = change_password(db, current_user, request.old_password, request.new_password)
    return result
