"""
数据库会话工厂 — 双模式自动切换

核心逻辑：
- DB_TYPE=sqlite ➔ 连接本地 SQLite 文件
- DB_TYPE=mysql  ➔ 连接阿里云 RDS MySQL
- 业务 service 层无需感知数据库类型，完全复用 ORM 模型
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from db.base import Base


def get_database_url() -> str:
    """根据 DB_TYPE 返回对应的数据库连接串"""
    if settings.DB_TYPE == "mysql":
        return (
            f"mysql+pymysql://{settings.RDS_USER}:{settings.RDS_PWD}"
            f"@{settings.RDS_HOST}:{settings.RDS_PORT}/{settings.RDS_DB}"
            f"?charset=utf8mb4"
        )
    # 默认 SQLite
    db_path = settings.SQLITE_PATH
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    return f"sqlite:///{db_path}"


engine = create_engine(
    get_database_url(),
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.DB_TYPE == "sqlite" else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库：创建所有表 + 初始化管理员账号"""
    Base.metadata.create_all(bind=engine)

    # 初始化管理员
    from db.models import AdminUser
    from core.auth import hash_password

    db: Session = SessionLocal()
    try:
        exists = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
        if not exists:
            admin = AdminUser(
                username=settings.ADMIN_USERNAME,
                password=hash_password(settings.ADMIN_PASSWORD),
                real_name="系统管理员",
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
