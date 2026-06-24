"""5张核心数据库表模型定义（SQLite / MySQL 通用）"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from db.base import Base


class AdminUser(Base):
    """管理员账号表"""
    __tablename__ = "admin_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(256), nullable=False)          # bcrypt 加密
    real_name = Column(String(64), default="")
    is_active = Column(Boolean, default=True)
    last_login_time = Column(DateTime, nullable=True)
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DataSource(Base):
    """数据源配置表"""
    __tablename__ = "data_source"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(128), nullable=False)
    base_url = Column(String(512), nullable=False)
    account = Column(String(128), nullable=False)
    password_encrypt = Column(String(512), nullable=False)   # 加密存储
    client_type = Column(String(64), default="")
    login_api = Column(String(512), default="")
    data_api = Column(String(512), default="")
    page_size = Column(Integer, default=100)
    enable = Column(Boolean, default=True)
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    update_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class PushConfig(Base):
    """推送规则表"""
    __tablename__ = "push_config"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, nullable=False, index=True)
    push_type = Column(String(32), nullable=False)           # dingtalk/feishu/wecom/email
    config_json = Column(Text, default="{}")                 # JSON 配置内容
    is_enable = Column(Boolean, default=True)
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ReportTask(Base):
    """报表任务表"""
    __tablename__ = "report_task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, nullable=False, index=True)
    report_name = Column(String(256), nullable=False)
    crawl_params = Column(Text, default="{}")                # JSON 筛选条件
    cron_expr = Column(String(64), default="")               # Cron 表达式，空=不自动
    auto_push = Column(Boolean, default=False)
    last_crawl_time = Column(DateTime, nullable=True)
    excel_file_path = Column(String(512), default="")
    task_status = Column(String(32), default="idle")         # idle/running/success/fail
    task_log = Column(Text, default="")
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MenuMeta(Base):
    """全局菜单元数据表 — 支持无限动态菜单"""
    __tablename__ = "menu_meta"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, nullable=False, index=True)
    menu_code = Column(String(128), nullable=False, unique=True, index=True)
    menu_name = Column(String(256), nullable=False)
    list_api = Column(String(512), default="")
    export_api = Column(String(512), default="")
    filter_schema = Column(Text, default="[]")                # JSON 筛选字段定义数组
    page_param = Column(Text, default="{}")                   # 分页参数配置
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    update_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RawData(Base):
    """原始抓取数据表"""
    __tablename__ = "raw_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, nullable=False, index=True)
    menu_code = Column(String(128), default="", index=True)   # 菜单编码，区分不同菜单数据
    capture_filters = Column(Text, default="{}")              # 抓取时的筛选条件快照
    raw_json = Column(Text, default="{}")                     # 原始 JSON 数据
    crawl_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
