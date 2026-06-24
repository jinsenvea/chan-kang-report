"""
数据库迁移工具：SQLite → MySQL 数据导出导入

用于将本地 SQLite 数据迁移至阿里云 RDS MySQL。
"""

import json
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from core.config import settings
from db.base import Base
from db.session import get_database_url


def export_sqlite_to_json(output_file: str = "sqlite_export.json"):
    """导出 SQLite 全部数据为 JSON"""
    from db.session import engine, SessionLocal

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    export_data: dict = {}

    db: Session = SessionLocal()
    try:
        for table in tables:
            rows = db.execute(f"SELECT * FROM {table}").fetchall()
            columns = [col["name"] for col in inspector.get_columns(table)]
            export_data[table] = [
                {col: (str(val) if isinstance(val, datetime) else val) for col, val in zip(columns, row)}
                for row in rows
            ]
    finally:
        db.close()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"✅ 数据已导出至 {output_file}")


def import_json_to_mysql(json_file: str):
    """将 JSON 数据导入 MySQL（需先切换 DB_TYPE=mysql）"""
    if settings.DB_TYPE != "mysql":
        print("❌ 请先设置 DB_TYPE=mysql 并填写 RDS 配置")
        return

    mysql_engine = create_engine(get_database_url())
    Base.metadata.create_all(bind=mysql_engine)

    from sqlalchemy.orm import sessionmaker
    MySQLSession = sessionmaker(bind=mysql_engine)

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    db: Session = MySQLSession()
    try:
        for table, rows in data.items():
            if not rows:
                continue
            table_obj = Base.metadata.tables.get(table)
            if table_obj is None:
                print(f"⚠️ 跳过未知表: {table}")
                continue
            for row in rows:
                db.execute(table_obj.insert().values(**row))
        db.commit()
        print(f"✅ 数据已导入 MySQL")
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python -m db.db_migrate export|import [json_file]")
        sys.exit(1)
    action = sys.argv[1]
    json_file = sys.argv[2] if len(sys.argv) > 2 else "sqlite_export.json"
    if action == "export":
        export_sqlite_to_json(json_file)
    elif action == "import":
        import_json_to_mysql(json_file)
    else:
        print("未知操作，使用 export 或 import")
