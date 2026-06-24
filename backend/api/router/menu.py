"""动态菜单元数据管理 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import MenuMeta, DataSource
from api.dependencies import verify_token
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/menu", tags=["菜单元数据"], dependencies=[Depends(verify_token)])


class MenuCreate(BaseModel):
    source_id: int
    menu_code: str
    menu_name: str
    list_api: str = ""
    export_api: str = ""
    filter_schema: str = "[]"
    page_param: str = "{}"


@router.get("/list")
def list_menus(source_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取全部菜单列表（用于前端动态路由生成 + 侧边栏）"""
    q = db.query(MenuMeta)
    if source_id:
        q = q.filter(MenuMeta.source_id == source_id)
    menus = q.order_by(MenuMeta.id).all()
    return {
        "data": [
            {
                "id": m.id, "source_id": m.source_id, "menu_code": m.menu_code,
                "menu_name": m.menu_name, "list_api": m.list_api,
                "export_api": m.export_api, "filter_schema": m.filter_schema,
                "page_param": m.page_param,
            }
            for m in menus
        ]
    }


@router.get("/detail/{menu_code}")
def get_menu_detail(menu_code: str, db: Session = Depends(get_db)):
    """获取单菜单元数据"""
    menu = db.query(MenuMeta).filter(MenuMeta.menu_code == menu_code).first()
    if not menu:
        raise HTTPException(404, "菜单不存在")
    return {
        "id": menu.id, "source_id": menu.source_id, "menu_code": menu.menu_code,
        "menu_name": menu.menu_name, "list_api": menu.list_api,
        "export_api": menu.export_api, "filter_schema": menu.filter_schema,
        "page_param": menu.page_param,
    }


@router.post("/create")
def create_menu(req: MenuCreate, db: Session = Depends(get_db)):
    """新增菜单元数据"""
    exists = db.query(MenuMeta).filter(MenuMeta.menu_code == req.menu_code).first()
    if exists:
        raise HTTPException(400, f"菜单编码 {req.menu_code} 已存在")
    menu = MenuMeta(
        source_id=req.source_id, menu_code=req.menu_code, menu_name=req.menu_name,
        list_api=req.list_api, export_api=req.export_api,
        filter_schema=req.filter_schema, page_param=req.page_param,
    )
    db.add(menu)
    db.commit()
    return {"msg": "新增菜单成功", "id": menu.id}


@router.put("/update/{menu_id}")
def update_menu(menu_id: int, req: MenuCreate, db: Session = Depends(get_db)):
    """更新菜单元数据"""
    menu = db.query(MenuMeta).filter(MenuMeta.id == menu_id).first()
    if not menu:
        raise HTTPException(404, "菜单不存在")
    menu.source_id = req.source_id
    menu.menu_code = req.menu_code
    menu.menu_name = req.menu_name
    menu.list_api = req.list_api
    menu.export_api = req.export_api
    menu.filter_schema = req.filter_schema
    menu.page_param = req.page_param
    db.commit()
    return {"msg": "更新成功"}


@router.delete("/delete/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """删除菜单元数据"""
    menu = db.query(MenuMeta).filter(MenuMeta.id == menu_id).first()
    if not menu:
        raise HTTPException(404, "菜单不存在")
    db.delete(menu)
    db.commit()
    return {"msg": "删除成功"}
