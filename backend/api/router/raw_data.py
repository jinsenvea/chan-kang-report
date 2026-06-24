"""原始数据查询 — 支持 menu_code 动态菜单隔离"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from api.dependencies import verify_token
from typing import Optional
from service.raw_data_service import query_raw_data, export_raw_to_excel

router = APIRouter(prefix="/api/raw-data", tags=["原始数据"], dependencies=[Depends(verify_token)])


@router.get("/list")
def list_raw_data(
    source_id: Optional[int] = None,
    menu_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=10, le=200),
    db: Session = Depends(get_db),
):
    """分页查询（支持 menu_code 过滤）"""
    result = query_raw_data(db, source_id, menu_code, date_from, date_to, page, page_size)
    return {"data": result["data"], "total": result["total"], "page": page, "page_size": page_size}


@router.get("/export")
def export_raw_data(
    source_id: Optional[int] = None,
    menu_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """导出原始数据为 Excel"""
    file_path = export_raw_to_excel(db, source_id, menu_code, date_from, date_to)
    if not file_path:
        return {"ok": False, "msg": "无数据可导出"}
    return {"ok": True, "file_path": file_path, "msg": "导出成功"}
