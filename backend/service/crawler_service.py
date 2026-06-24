"""
爬虫核心 — 纯 requests 实现
支持无限动态菜单：读取menu_meta filter_schema动态组装筛选参数
"""

import json
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from db.models import DataSource, RawData, MenuMeta
from core.auth import decrypt_ciphertext
from utils.common import random_delay


_token_cache: Dict[int, Dict[str, Any]] = {}


def _login(account: str, password: str, base_url: str, login_api: str = "") -> Optional[str]:
    """模拟 POST 登录，缓存 token"""
    login_url = base_url.rstrip("/") + (login_api or "/api/login")
    cache_key = f"{account}@{base_url}"
    cached = _token_cache.get(cache_key)
    if cached:
        return cached.get("token")
    try:
        resp = requests.post(
            login_url,
            json={"account": account, "password": password},
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token") or data.get("access_token") or data.get("data", {}).get("token")
        if token:
            _token_cache[cache_key] = {"token": token, "login_time": datetime.now()}
            return token
    except Exception as e:
        raise Exception(f"登录失败: {str(e)}")
    return None


def _get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }


def _resolve_password(source: DataSource, password: str = "") -> str:
    """解析密码：优先用传入的明文，否则解密存储的加密密码"""
    if password:
        return password
    return decrypt_ciphertext(source.password_encrypt)


def test_source_connection(source: DataSource, password: str = "") -> tuple:
    """测试数据源连通性"""
    try:
        pwd = _resolve_password(source, password)
        token = _login(source.account, pwd, source.base_url, source.login_api)
        if token:
            return True, "连接成功"
        return False, "无法获取Token"
    except Exception as e:
        return False, f"连接失败: {str(e)}"


def build_menu_query_params(menu: MenuMeta, extra_params: dict = None) -> dict:
    """
    根据菜单 filter_schema 动态组装查询参数
    filter_schema 格式示例:
    [
        {"field": "page", "value": 1},
        {"field": "page_size", "value": 100},
        {"field": "store_id", "value": "all"},
        {"field": "date_from", "value": "2026-05-01"}
    ]
    """
    params = {}
    try:
        schema = json.loads(menu.filter_schema or "[]")
        for item in schema:
            field = item.get("field", "")
            val = item.get("value", "")
            if field:
                params[field] = val
    except (json.JSONDecodeError, TypeError):
        pass

    # 额外参数覆盖
    if extra_params:
        params.update(extra_params)

    # 确保分页参数
    page_param = {}
    try:
        page_param = json.loads(menu.page_param or "{}")
    except:
        pass

    if "page" not in params:
        params["page"] = page_param.get("page_field", "page")
    if "page_size" not in params:
        params["page_size"] = page_param.get("size_field", "page_size")

    return params


def crawl_data(source: DataSource, db: Session, params: dict = None, on_log=None,
               menu: Optional[MenuMeta] = None, password: str = "") -> List[dict]:
    """
    核心爬虫：支持绑定菜单，按菜单filter_schema动态组装参数
    """
    menu_name = menu.menu_name if menu else source.source_name
    if on_log:
        on_log(f"开始爬取 [{menu_name}]")

    pwd = _resolve_password(source, password)
    token = _login(source.account, pwd, source.base_url, source.login_api)
    if not token:
        raise Exception("登录失败，无法获取Token")

    headers = _get_headers(token)
    data_api = source.base_url.rstrip("/") + (menu.list_api if menu and menu.list_api else (source.data_api or "/api/data"))
    page_size = source.page_size or 100
    page = 1
    all_rows: List[dict] = []

    # 组装参数
    query_params = {}
    if menu:
        query_params = build_menu_query_params(menu, params)
    elif params:
        query_params.update(params)

    while True:
        random_delay(1.0, 3.0)

        post_data = dict(query_params)
        post_data["page"] = page
        post_data["page_size"] = page_size

        try:
            resp = requests.post(data_api, json=post_data, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            if on_log:
                on_log(f"第{page}页请求失败: {str(e)}")
            break

        rows = result.get("data") or result.get("list") or result.get("records") or []
        if not rows:
            break

        # 入库，标记 menu_code + 筛选快照
        for row in rows:
            raw = RawData(
                source_id=source.id,
                menu_code=menu.menu_code if menu else "",
                capture_filters=json.dumps(query_params, ensure_ascii=False),
                raw_json=json.dumps(row, ensure_ascii=False),
                crawl_time=datetime.now(timezone.utc),
            )
            db.add(raw)

        all_rows.extend(rows)

        if on_log:
            on_log(f"第{page}页完成，已获取 {len(rows)} 条")
        page += 1

        total = result.get("total") or result.get("totalCount") or 0
        if total and (page - 1) * page_size >= total:
            break
        if len(rows) < page_size:
            break

    db.commit()
    if on_log:
        on_log(f"[{menu_name}] 爬取完成，共 {len(all_rows)} 条")
    return all_rows


def clean_data(rows: List[dict]) -> List[dict]:
    """数据清洗"""
    cleaned = []
    for row in rows:
        item = {}
        for key, val in row.items():
            if isinstance(val, (str, int, float, bool)):
                item[key] = val
            elif isinstance(val, (list, dict)):
                item[key] = json.dumps(val, ensure_ascii=False)
            else:
                item[key] = str(val) if val else ""
        cleaned.append(item)
    return cleaned
