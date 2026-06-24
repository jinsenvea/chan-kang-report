"""数据源业务逻辑 + 报表任务管理"""

import json
import uuid
import threading
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from db.models import DataSource, MenuMeta, ReportTask
from datetime import datetime, timezone


_running_tasks: Dict[str, Dict[str, Any]] = {}


def start_crawl_task(task: ReportTask, db: Session) -> str:
    """启动异步爬取任务（支持菜单绑定）"""
    run_id = str(uuid.uuid4())[:8]

    _running_tasks[run_id] = {"status": "running", "log": "", "file_path": ""}

    task.task_status = "running"
    task.task_log = ""
    db.commit()

    def _run():
        log_lines = []
        def log(msg: str):
            log_lines.append(msg)
            _running_tasks[run_id]["log"] = "\n".join(log_lines)
            task.task_log = "\n".join(log_lines)

        try:
            source = db.query(DataSource).filter(DataSource.id == task.source_id).first()
            if not source:
                raise Exception("数据源不存在")

            # 解析 crawl_params，提取菜单和筛选参数
            params = {}
            menu_code = None
            if task.crawl_params and task.crawl_params != "{}":
                try:
                    cp = json.loads(task.crawl_params)
                    if isinstance(cp, dict):
                        menu_code = cp.pop("menu_code", None)
                        params = cp
                except:
                    pass

            # 查找菜单元数据
            menu = None
            if menu_code:
                menu = db.query(MenuMeta).filter(
                    MenuMeta.menu_code == menu_code,
                    MenuMeta.source_id == task.source_id
                ).first()

            menu_name = menu.menu_name if menu else source.source_name
            log(f"开始爬取: [{menu_name}]")

            from service.crawler_service import crawl_data, clean_data
            from utils.excel_util import generate_report

            rows = crawl_data(source, db, params, on_log=log, menu=menu)
            cleaned = clean_data(rows)

            columns = list(cleaned[0].keys()) if cleaned else ["暂无数据"]
            file_path = generate_report(cleaned, columns, task.report_name)

            task.last_crawl_time = datetime.now(timezone.utc)
            task.excel_file_path = file_path
            task.task_status = "success"

            _running_tasks[run_id]["status"] = "success"
            _running_tasks[run_id]["file_path"] = file_path
            log(f"报表已生成: {file_path}")

            if task.auto_push:
                from service.push_service import push_report_to_all_channels
                push_report_to_all_channels(task.source_id, file_path, db)

        except Exception as e:
            task.task_status = "fail"
            _running_tasks[run_id]["status"] = "fail"
            log(f"❌ 爬取失败: {str(e)}")
        finally:
            db.commit()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return run_id


def get_task_progress(run_id: str) -> dict:
    data = _running_tasks.get(run_id, {"status": "idle", "log": "", "file_path": ""})
    return {"status": data["status"], "log": data["log"], "file_path": data["file_path"]}


def execute_report_task(task_id: int, db: Session):
    try:
        task = db.query(ReportTask).filter(ReportTask.id == task_id).first()
        if task:
            start_crawl_task(task, db)
    except Exception as e:
        print(f"定时任务 {task_id} 执行异常: {e}")
