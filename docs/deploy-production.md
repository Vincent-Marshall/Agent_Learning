# 生产部署文档（腾讯云轻量 · Ubuntu 24.04）

> 线上地址：http://42.193.189.196（域名审核通过后换 HTTPS，见文末）
> 首次上线：2026-09-24

## 架构

```
浏览器
  └─ nginx :80（同源收敛，架构上避免跨源）
       ├─ /            前端构建产物（React dist 静态托管；未命中回落 FastAPI 的后台页路由）
       ├─ /api/        → 反代 uvicorn :8000（SSE：关缓冲、读超时 300s）
       └─ /static/     → 反代 FastAPI（后台各页资源）

uvicorn :8000        systemd: mewhelp-api（EnvironmentFile=.env.production）
MCP :8101 / :8102    systemd: mewhelp-mcp-logistics / mewhelp-mcp-aftersales
MySQL / Milvus 栈     docker compose（restart=unless-stopped + 内存限额，见 docker-compose.prod.yml）
```

**跨源策略**：生产为同源部署，FastAPI 的 `cors_origins` 留空（不挂 CORS 中间件）。
只有前后端分离部署时才填白名单（如 `CORS_ORIGINS=http://localhost:5173`）——这是「优先架构消源，
CORS 兜底」的原则，见 `app/main.py` 与 `app/config.py`。

## 服务器初始化（一次性）

```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2 nginx nodejs npm curl rsync
sudo systemctl enable --now docker nginx
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv(位于 ~/.local/bin/uv)

# Docker 镜像加速(腾讯云内网镜像源,拉取 Docker Hub 镜像走它)
sudo mkdir -p /etc/docker
echo '{"registry-mirrors":["https://mirror.ccs.tencentyun.com"]}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

## 首次部署

```bash
# 1. 同步代码(或 git clone;GitHub 直连不稳时用 rsync)
rsync -az -e 'ssh -i ~/.ssh/id_ed25519_tencent' \
  --exclude '.venv/' --exclude 'node_modules/' --exclude 'frontend/dist/' \
  --exclude '.env' --exclude 'data/*.db*' --exclude 'log/' --exclude '__pycache__/' \
  ~/Agent_Learning/ ubuntu@42.193.189.196:~/app/

# 2. 生产配置(密钥只存在于服务器,永不上库)
cp .env.production.example .env.production   # 填上游三组 key
PW=$(openssl rand -hex 12)                   # 生成 MySQL 强口令
echo "MYSQL_ROOT_PASSWORD=$PW" >> .env.production
echo "DATABASE_URL=mysql+asyncmy://root:$PW@localhost:3306/mewhelp" >> .env.production

# 3. 容器栈(MySQL 首启自动执行 sql/ 建表灌种)
sudo docker compose --env-file .env.production \
  -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Python 依赖 + 前端构建
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple ~/.local/bin/uv sync
cd frontend && npm install && npm run build && cd ..

# 5. 知识库(52 块 → 双写 Milvus)
set -a && source .env.production && set +a
PYTHONPATH=. .venv/bin/python scripts/build_kb.py
PYTHONPATH=. .venv/bin/python scripts/vectorize_kb.py

# 6. systemd 守护 + nginx 反代
sudo cp deploy/*.service /etc/systemd/system/ && sudo systemctl daemon-reload
sudo systemctl enable --now mewhelp-api mewhelp-mcp-logistics mewhelp-mcp-aftersales
sudo rm -f /etc/nginx/sites-enabled/default
sudo cp deploy/nginx-mewhelp.conf /etc/nginx/sites-available/mewhelp
sudo ln -sf /etc/nginx/sites-available/mewhelp /etc/nginx/sites-enabled/mewhelp
sudo nginx -t && sudo systemctl reload nginx
```

## 日常更新

```bash
rsync …(同上)                      # 或服务器上 git pull
cd ~/app && ~/.local/bin/uv sync && cd frontend && npm install && npm run build && cd ..
sudo systemctl restart mewhelp-api  # 代码改动只重启 API;MCP/容器无改动不用动
```

## 验证记录（2026-09-24 上线）

| 项 | 结果 |
| --- | --- |
| 公网首页（nginx → React dist） | ✅ `http://42.193.189.196/` 返回 React 聊天页 |
| 公网 API | ✅ /api/kb/overview：知识块 52、Milvus 52、双写一致 True |
| 公网聊天 SSE（经 nginx 反代） | ✅ citations/流式帧正常透传；服务器日志确认 query_order → query_logistics（MCP）三步收敛 |
| systemd 三服务 | ✅ 全部 active，开机自启 |
| 容器内存限额 | ✅ mysql 768M / milvus 2G / etcd 512M / minio 512M（prod 编排生效） |

## 待办：域名与 HTTPS

域名审核通过后：

1. DNS 解析 A 记录 → 42.193.189.196
2. nginx 配置 `server_name` 换成域名，加 443 端口 + SSL（Let's Encrypt / certbot 自动续期，或腾讯云免费证书）
3. 浏览器验证 HTTPS + 安全锁；部署文档与 README 的演示链接换成 https://域名
