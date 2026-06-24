"""原始数据查询 & 导出 — 支持 menu_code 单菜单隔离"""

import json
from typing import Optional
from sqlalchemy.orm import Session
from db.models import RawData, DataSource, MenuMeta
from utils.excel_util import generate_report
from datetime import datetime


def query_raw_data(
    db: Session,
    source_id: Optional[int] = None,
    menu_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    """通用分页查询（支持 menu_code 过滤）"""
    q = db.query(RawData)
    if source_id:
        q = q.filter(RawData.source_id == source_id)
    if menu_code:
        q = q.filter(RawData.menu_code == menu_code)
    if date_from:
        q = q.filter(RawData.crawl_time >= date_from)
    if date_to:
        q = q.filter(RawData.crawl_time <= f"{date_to} 23:59:59")

    total = q.count()
    items = q.order_by(RawData.crawl_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [
            {
                "id": r.id, "source_id": r.source_id, "menu_code": r.menu_code,
                "capture_filters": r.capture_filters,
                "raw_json": r.raw_json,
                "crawl_time": r.crawl_time.isoformat() if r.crawl_time else "",
            }
            for r in items
        ],
        "total": total,
    }


def export_raw_to_excel(
    db: Session,
    source_id: Optional[int] = None,
    menu_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Optional[str]:
    """导出（支持 menu_code 过滤）"""
    q = db.query(RawData)
    if source_id:
        q = q.filter(RawData.source_id == source_id)
    if menu_code:
        q = q.filter(RawData.menu_code == menu_code)
    if date_from:
        q = q.filter(RawData.crawl_time >= date_from)
    if date_to:
        q = q.filter(RawData.crawl_time <= f"{date_to} 23:59:59")

    items = q.order_by(RawData.crawl_time.desc()).limit(10000).all()
    if not items:
        return None

    rows = []
    for r in items:
        try:
            row = json.loads(r.raw_json)
            row["_crawl_time"] = r.crawl_time.isoformat() if r.crawl_time else ""
            row["_menu_code"] = r.menu_code or ""
            rows.append(row)
        except:
            pass

    label = f"menu_{menu_code}" if menu_code else "全部"
    file_path = generate_report(rows, list(rows[0].keys()) if rows else [], f"原始数据_{label}")
    return file_path
