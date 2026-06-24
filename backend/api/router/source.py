from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import DataSource
from core.auth import encrypt_plaintext, decrypt_ciphertext
from api.dependencies import verify_token
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/source", tags=["数据源"], dependencies=[Depends(verify_token)])


class DataSourceCreate(BaseModel):
    source_name: str
    base_url: str
    account: str
    password: str
    client_type: str = ""
    login_api: str = ""
    data_api: str = ""
    page_size: int = 100
    enable: bool = True


class DataSourceUpdate(BaseModel):
    source_name: Optional[str] = None
    base_url: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    client_type: Optional[str] = None
    login_api: Optional[str] = None
    data_api: Optional[str] = None
    page_size: Optional[int] = None
    enable: Optional[bool] = None


@router.get("/list")
def list_sources(db: Session = Depends(get_db)):
    """数据源列表"""
    sources = db.query(DataSource).order_by(DataSource.id.desc()).all()
    result = []
    for s in sources:
        result.append({
            "id": s.id, "source_name": s.source_name, "base_url": s.base_url,
            "account": s.account, "client_type": s.client_type,
            "login_api": s.login_api, "data_api": s.data_api,
            "page_size": s.page_size, "enable": s.enable,
            "create_time": s.create_time.isoformat() if s.create_time else "",
        })
    return {"data": result, "total": len(result)}


@router.post("/create")
def create_source(req: DataSourceCreate, db: Session = Depends(get_db)):
    """新增数据源（密码加密存储）"""
    source = DataSource(
        source_name=req.source_name, base_url=req.base_url,
        account=req.account, password_encrypt=encrypt_plaintext(req.password),
        client_type=req.client_type, login_api=req.login_api,
        data_api=req.data_api, page_size=req.page_size, enable=req.enable,
    )
    db.add(source)
    db.commit()
    return {"msg": "新增成功", "id": source.id}


@router.put("/update/{source_id}")
def update_source(source_id: int, req: DataSourceUpdate, db: Session = Depends(get_db)):
    """编辑数据源"""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    update_data = req.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_encrypt"] = encrypt_plaintext(update_data.pop("password"))
    elif "password" in update_data:
        update_data.pop("password")
    for key, val in update_data.items():
        setattr(source, key, val)
    source.update_time = datetime.now(timezone.utc)
    db.commit()
    return {"msg": "更新成功"}


class TestConnectReq(BaseModel):
    password: Optional[str] = None


@router.post("/test-connect/{source_id}")
def test_connect(source_id: int, req: Optional[TestConnectReq] = None, db: Session = Depends(get_db)):
    """连通性测试"""
    from service.crawler_service import test_source_connection
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    pwd = req.password if req and req.password else ""
    ok, msg = test_source_connection(source, password=pwd)
    return {"ok": ok, "msg": msg}
