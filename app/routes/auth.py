from datetime import timedelta
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, get_password_hash, verify_password
from app.config import settings
from app.database import get_session
from app.models import Role, User

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    username: str
    role: Role

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    existing = session.exec(select(User).where(User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    user = User(username=payload.username, password_hash=get_password_hash(payload.password), role=payload.role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> Token:
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires)
    return Token(access_token=access_token)


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, session: Session = Depends(get_session)) -> Dict:
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码长度不能少于6位")

    user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user or not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或原密码错误")

    user.password_hash = get_password_hash(payload.new_password)
    session.add(user)
    session.commit()

    return {"success": True, "message": "密码修改成功"}


@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
