"""FastAPI 应用入口 — 双数据库兼容启动"""

import os
import sys

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import settings, CORS_ORIGIN_LIST
from core.scheduler import start_scheduler
from db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化"""
    init_db()
    start_scheduler()
    yield


app = FastAPI(
    title="PeerBizSync - 第三方渠道数据采集报表管理系统",
    description="K3Cloud 数据爬取、报表生成、多渠道推送",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由挂载
from api.router import auth, source, push_config, raw_data, report, menu

app.include_router(auth.router)
app.include_router(source.router)
app.include_router(push_config.router)
app.include_router(raw_data.router)
app.include_router(report.router)
app.include_router(menu.router)


@app.get("/api/health")
def health():
    """健康检查"""
    return {"status": "ok", "db_type": settings.DB_TYPE}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
