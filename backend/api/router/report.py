from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import ReportTask, DataSource
from api.dependencies import verify_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/report", tags=["报表管理"], dependencies=[Depends(verify_token)])


class ReportCreate(BaseModel):
    source_id: int
    report_name: str
    crawl_params: str = "{}"
    cron_expr: str = ""
    auto_push: bool = False


@router.get("/list")
def list_reports(db: Session = Depends(get_db)):
    """报表任务列表"""
    reports = db.query(ReportTask).order_by(ReportTask.id.desc()).all()
    return {
        "data": [
            {
                "id": r.id, "source_id": r.source_id, "report_name": r.report_name,
                "crawl_params": r.crawl_params, "cron_expr": r.cron_expr,
                "auto_push": r.auto_push,
                "last_crawl_time": r.last_crawl_time.isoformat() if r.last_crawl_time else "",
                "excel_file_path": r.excel_file_path, "task_status": r.task_status,
                "task_log": r.task_log,
            }
            for r in reports
        ]
    }


@router.post("/create")
def create_report(req: ReportCreate, db: Session = Depends(get_db)):
    """新建报表任务"""
    task = ReportTask(
        source_id=req.source_id, report_name=req.report_name,
        crawl_params=req.crawl_params, cron_expr=req.cron_expr,
        auto_push=req.auto_push,
    )
    db.add(task)
    db.commit()

    # 如果启用了定时，注册到 APScheduler
    from core.scheduler import add_cron_job
    from service.report_service import execute_report_task
    if req.cron_expr and req.auto_push:
        add_cron_job(f"report_{task.id}", lambda: execute_report_task(task.id, db), req.cron_expr)

    return {"msg": "创建成功", "id": task.id}


@router.post("/re-crawl/{task_id}")
def re_crawl(task_id: int, db: Session = Depends(get_db)):
    """重新爬取（异步）"""
    from service.report_service import start_crawl_task
    task = db.query(ReportTask).filter(ReportTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    run_id = start_crawl_task(task, db)
    return {"run_id": run_id, "msg": "爬取任务已启动"}


@router.get("/task-progress/{run_id}")
def task_progress(run_id: str):
    """查询爬取任务进度"""
    from service.report_service import get_task_progress
    return get_task_progress(run_id)


@router.post("/push/{task_id}")
def push_report(task_id: int, db: Session = Depends(get_db)):
    """立即推送报表"""
    from service.push_service import push_report_to_all_channels
    task = db.query(ReportTask).filter(ReportTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    if not task.excel_file_path:
        return {"ok": False, "msg": "尚无报表文件，请先爬取"}
    ok, msg = push_report_to_all_channels(task.source_id, task.excel_file_path, db)
    return {"ok": ok, "msg": msg}


@router.post("/cron-config/{task_id}")
def cron_config(task_id: int, cron_expr: str = Query(...), auto_push: bool = Query(True), db: Session = Depends(get_db)):
    """定时配置"""
    from core.scheduler import add_cron_job
    from service.report_service import execute_report_task
    task = db.query(ReportTask).filter(ReportTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    task.cron_expr = cron_expr
    task.auto_push = auto_push
    db.commit()
    if cron_expr and auto_push:
        add_cron_job(f"report_{task.id}", lambda: execute_report_task(task.id, next(get_db())), cron_expr)
    return {"msg": "定时配置已更新"}
