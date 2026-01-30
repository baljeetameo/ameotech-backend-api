# app/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional,List

from fastapi import APIRouter, HTTPException, Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .utils.password_auth import verify_password

SECRET_KEY = os.getenv("AMEOTECH_AUTH_SECRET", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ADMIN_EMAIL = os.getenv("AMEOTECH_ADMIN_EMAIL", "admin@ameotech.com")
ADMIN_PASSWORD = os.getenv("AMEOTECH_ADMIN_PASSWORD", "Cool@coder1")  # change in env for prod

ROLES = {
            "admin": "Admin",
            "hr": "HR",
            "sales_engineer": "SalesEngineer",
            "end_user": "User",
        }

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    # username == email
    try:
        user = db.query(User).filter(User.email == form_data.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email"
            )

        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        # if form_data.username.lower() != ADMIN_EMAIL.lower() or form_data.password != ADMIN_PASSWORD:
        #     raise HTTPException(status_code=401, detail="Incorrect email or password")


        access_token = create_access_token({"sub": user.email, "role": get_current_role(user)})
        return Token(access_token=access_token)
    except Exception as e:
        # Log the actual error
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_current_role(user):
    if getattr(user, "is_admin", False):
        return ROLES["admin"]
    if getattr(user, "is_hr", False):
        return ROLES["hr"]
    if getattr(user, "is_sales_engineer", False):
        return ROLES["sales_engineer"]
    if getattr(user, "is_end_user", False):
        return ROLES["end_user"]

    # fallback if no flags match
    return None