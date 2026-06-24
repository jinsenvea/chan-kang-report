# PeerBizSync 项目启动部署文档

## 一、项目结构

```
benchAutoReport/
├── frontend/          # Vue3 + TypeScript + Element Plus
├── backend/           # FastAPI + SQLAlchemy + Python
├── DEPLOY.md          # 本部署文档
```

---

## 二、本地测试启动流程（默认 SQLite）

### 2.1 后端启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境（建议 Python 3.10+）
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 检查 .env 配置（默认 SQLite，无需修改即可启动）
#    如需修改可编辑 .env 文件

# 5. 启动后端服务
python main.py
# 服务将在 http://localhost:8000 启动
# API 文档: http://localhost:8000/docs
```

### 2.2 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器（Vite 代理到后端 8000 端口）
npm run dev
# 服务将在 http://localhost:5173 启动
```

### 2.3 登录系统

- 打开 http://localhost:5173
- 默认管理员账号：`admin` / `Admin123!`
- 登录后自动跳转数据源列表页面

### 2.4 本地测试流程

1. **新增数据源**：配置 K3Cloud 平台地址、账号、密码、接口地址，测试连通性
2. **配置推送规则**：绑定数据源，选择钉钉/飞书/企微/邮箱，填入对应 webhook/密钥
3. **新建报表任务**：关联数据源，配置爬取参数
4. **执行爬取**：点击「重新爬取」，观察全屏 Loading 进度日志
5. **推送报表**：爬取成功后可立即推送或配置定时自动推送

---

## 三、阿里云 ECS + RDS 部署切换

### 3.1 后端部署

```bash
# 1. 将 backend/ 上传到阿里云 ECS 服务器
scp -r backend/ root@your-ecs-ip:/app/peer-biz-sync/

# 2. SSH 登录服务器
ssh root@your-ecs-ip

# 3. 安装 Python 依赖
cd /app/peer-biz-sync
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 修改 .env 切换为 MySQL 模式
vim .env
# DB_TYPE=mysql
# RDS_HOST=your-rds-host.mysql.rds.aliyuncs.com
# RDS_PORT=3306
# RDS_USER=your_db_user
# RDS_PWD=your_db_password
# RDS_DB=peer_biz_sync
```

### 3.2 数据库迁移（SQLite → MySQL）

```bash
# 1. 本地导出 SQLite 数据
python -m db.db_migrate export sqlite_export.json

# 2. 将 json 上传到服务器
scp sqlite_export.json root@your-ecs-ip:/app/peer-biz-sync/

# 3. 在服务器上导入 MySQL（需先切 DB_TYPE=mysql）
python -m db.db_migrate import sqlite_export.json
```

### 3.3 Systemd 服务配置

```ini
# /etc/systemd/system/peer-biz-sync.service
[Unit]
Description=PeerBizSync Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app/peer-biz-sync
EnvironmentFile=/app/peer-biz-sync/.env
ExecStart=/app/peer-biz-sync/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable peer-biz-sync
systemctl start peer-biz-sync
# 查看日志
journalctl -u peer-biz-sync -f
```

### 3.4 前端打包部署

```bash
# 1. 修改 .env.production 为实际 ECS 域名
# VITE_API_BASE=https://your-ecs-domain.com

# 2. 构建
cd frontend
npm run build
# 产物在 dist/ 目录

# 3. 上传 dist 到 ECS（建议使用 Nginx 托管）
scp -r dist/ root@your-ecs-ip:/var/www/peer-biz-sync/
```

### 3.5 Nginx 配置

```nginx
# /etc/nginx/conf.d/peer-biz-sync.conf
server {
    listen 80;
    server_name your-ecs-domain.com;

    # 前端静态文件
    root /var/www/peer-biz-sync;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 四、环境变量配置示例

### 4.1 本地（backend/.env）

```ini
DB_TYPE=sqlite
SQLITE_PATH=./data.db
JWT_SECRET_KEY=local-dev-key
CORS_ORIGINS=http://localhost:5173
```

### 4.2 生产（backend/.env）

```ini
DB_TYPE=mysql
RDS_HOST=rm-xxx.mysql.rds.aliyuncs.com
RDS_PORT=3306
RDS_USER=prod_user
RDS_PWD=ProdPwd!2026
RDS_DB=peer_biz_sync
JWT_SECRET_KEY=<64位随机密钥>
CORS_ORIGINS=https://your-frontend-domain.com
LOG_DIR=/var/log/peer-biz-sync
EXCEL_STORAGE_DIR=/data/peer-biz-sync/reports
```

---

## 五、注意事项

1. **密码安全**：首次启动后请立即修改 `.env` 中的 `ADMIN_PASSWORD`
2. **JWT密钥**：生产环境请使用 `openssl rand -hex 32` 生成随机 JWT 密钥
3. **CORS**：生产环境 `CORS_ORIGINS` 必须设置为前端真实域名
4. **MySQL驱动**：依赖 `pymysql`，切换 MySQL 前确认已安装
5. **文件存储**：`EXCEL_STORAGE_DIR` 确保有足够磁盘空间，建议挂载数据盘
6. **日志轮转**：生产环境建议配置 logrotate 管理日志文件
