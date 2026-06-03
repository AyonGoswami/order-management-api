from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User, UserRole
from auth import hash_password, verify_password, create_access_token, create_refresh_token


def register_user(db: Session, email: str, full_name: str, password: str, role: str) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered!!!",
        )

    if role not in ["admin", "customer"]:
        role = "customer"

    new_user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        role=UserRole(role),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Password entered!",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated.",
        )

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def change_password(db: Session, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect. Please enter the correct password.",
        )

    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully!"}
