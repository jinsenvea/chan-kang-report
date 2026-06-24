"""JWT 认证 / 密码加密 / 可逆加密工具"""

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def _get_fernet() -> Fernet:
    """从 JWT 密钥派生 Fernet 密钥（对称可逆加密）"""
    key = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_plaintext(plain: str) -> str:
    """可逆加密（用于数据源密码存储）"""
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_ciphertext(cipher: str) -> str:
    """可逆解密"""
    try:
        return _get_fernet().decrypt(cipher.encode()).decode()
    except Exception:
        return cipher  # 兼容旧数据（bcrypt hash 直接返回）


def hash_password(password: str) -> str:
    """bcrypt 加密密码"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """签发 JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效或已过期")


async def get_current_user(cred: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """依赖注入：从请求头解析当前用户"""
    return decode_access_token(cred.credentials)
