from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import PushConfig
from api.dependencies import verify_token
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/push-config", tags=["推送规则"], dependencies=[Depends(verify_token)])


class PushConfigCreate(BaseModel):
    source_id: int
    push_type: str           # dingtalk/feishu/wecom/email
    config_json: str = "{}"
    is_enable: bool = True


@router.get("/list")
def list_configs(source_id: Optional[int] = None, db: Session = Depends(get_db)):
    """推送规则列表"""
    q = db.query(PushConfig)
    if source_id:
        q = q.filter(PushConfig.source_id == source_id)
    configs = q.order_by(PushConfig.id.desc()).all()
    return {"data": [{"id": c.id, "source_id": c.source_id, "push_type": c.push_type,
                       "config_json": c.config_json, "is_enable": c.is_enable} for c in configs]}


@router.post("/create")
def create_config(req: PushConfigCreate, db: Session = Depends(get_db)):
    """新增推送规则"""
    cfg = PushConfig(source_id=req.source_id, push_type=req.push_type,
                     config_json=req.config_json, is_enable=req.is_enable)
    db.add(cfg)
    db.commit()
    return {"msg": "新增成功", "id": cfg.id}


@router.put("/update/{config_id}")
def update_config(config_id: int, req: PushConfigCreate, db: Session = Depends(get_db)):
    """编辑推送规则"""
    cfg = db.query(PushConfig).filter(PushConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(404, "配置不存在")
    cfg.push_type = req.push_type
    cfg.config_json = req.config_json
    cfg.is_enable = req.is_enable
    cfg.source_id = req.source_id
    db.commit()
    return {"msg": "更新成功"}


@router.delete("/delete/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db)):
    """删除推送规则"""
    cfg = db.query(PushConfig).filter(PushConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(404, "配置不存在")
    db.delete(cfg)
    db.commit()
    return {"msg": "删除成功"}


@router.post("/test-push/{config_id}")
def test_push(config_id: int, db: Session = Depends(get_db)):
    """测试推送（发送测试 Excel）"""
    from service.push_service import push_to_channel
    cfg = db.query(PushConfig).filter(PushConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(404, "配置不存在")
    ok, msg = push_to_channel(cfg, test_mode=True)
    return {"ok": ok, "msg": msg}
