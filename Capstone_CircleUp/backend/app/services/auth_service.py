from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories import user_repo


def register_user(db: Session, user_data: UserRegister):
    existing_user = user_repo.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        city=user_data.city,
        bio=user_data.bio,
        password=hash_password(user_data.password)
    )
    user_repo.create_user(db, new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str):
    db_user = user_repo.get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": db_user.email})
    return access_token
