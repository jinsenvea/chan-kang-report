from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import AdminUser
from core.auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter(prefix="/api/auth", tags=["认证"])


class LoginReq(BaseModel):
    username: str
    password: str


class LoginResp(BaseModel):
    token: str
    username: str
    real_name: str


@router.post("/login", response_model=LoginResp)
def login(req: LoginReq, db: Session = Depends(get_db)):
    """管理员登录"""
    user = db.query(AdminUser).filter(AdminUser.username == req.username).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token({"sub": user.username, "uid": user.id})
    user.last_login_time = datetime.now(timezone.utc)
    db.commit()
    return LoginResp(token=token, username=user.username, real_name=user.real_name or user.username)
