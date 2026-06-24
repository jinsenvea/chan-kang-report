"""FastAPI 全局依赖：接口鉴权"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.auth import decode_access_token

security = HTTPBearer()


async def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """校验 JWT Token，返回用户信息"""
    payload = decode_access_token(cred.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效或已过期")
    return payload
