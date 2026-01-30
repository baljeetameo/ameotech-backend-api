# backend/app/auth_interceptor.py

from typing import List
from jose import jwt, JWTError
from fastapi import Header, HTTPException, status, Depends
import os

SECRET_KEY = os.getenv("AMEOTECH_AUTH_SECRET", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = "HS256"  # your JWT algorithm

def get_current_user_role(authorization: str = Header(...)) -> str:
    """
    Extract the user's role from JWT token.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not found in token")
        return role
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def role_checker(allowed_roles: List[str]):
    """
    Returns a dependency that ensures the current user has one of the allowed roles.
    """
    def checker(role: str = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires role(s) {allowed_roles}"
            )
        return role
    return checker
