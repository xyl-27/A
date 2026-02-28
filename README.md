# A股智能选股分析平台 - 部署指南

## 后端部署

### 环境要求
- Python 3.10+
- MySQL 8.0
- Redis 7.0

### 本地开发

```bash
# 1. 创建并激活虚拟环境
conda create -n stock-analysis python=3.10 -y
conda activate stock-analysis

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 MySQL、Redis、API Key 等配置

# 4. 启动服务
uvicorn main:app --reload --port 8000
```

### Docker 部署

```bash
cd /opt/A
docker-compose up -d
```

---

## 前端部署

### 环境要求
- Node.js 18+

### 本地开发

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev
# 访问 http://localhost:3000
```

### 生产构建

```bash
cd frontend
npm run build
# 构建产物在 dist 目录
```

### Docker 部署

```bash
# 使用 nginx 部署
docker build -t stock-frontend .
docker run -d -p 80:80 stock-frontend
```

---

## 完整 Docker 部署

```bash
# 启动所有服务 (MySQL + Redis + Backend + Frontend)
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

服务地址：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
