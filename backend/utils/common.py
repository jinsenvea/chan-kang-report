"""通用工具函数"""

import random
import time
import os
import json
from datetime import datetime
from core.config import settings


def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    """1~3s 随机延迟，规避平台风控"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def format_datetime(dt: datetime) -> str:
    """格式化日期时间"""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


def ensure_dir(dir_path: str):
    """确保目录存在"""
    os.makedirs(dir_path, exist_ok=True)


def get_date_storage_dir() -> str:
    """按日期分层存储目录：./reports/2026/06/18/"""
    now = datetime.now()
    path = os.path.join(settings.EXCEL_STORAGE_DIR, str(now.year), f"{now.month:02d}", f"{now.day:02d}")
    ensure_dir(path)
    return path


def save_report_log(run_id: str, status: str, log: str, file_path: str = ""):
    """持久化任务日志"""
    log_dir = os.path.join(settings.LOG_DIR, "tasks")
    ensure_dir(log_dir)
    log_file = os.path.join(log_dir, f"{run_id}.json")
    data = {"run_id": run_id, "status": status, "log": log, "file_path": file_path, "update_time": format_datetime(datetime.now())}
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
