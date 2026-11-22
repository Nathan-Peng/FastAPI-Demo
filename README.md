# FastAPI 完整基础功能示例

一个符合 Python 工程化规范的 FastAPI 示例项目，单文件 `main.py` 覆盖 FastAPI 几乎所有基础功能，并配套完整的项目脚手架。

## 目录结构

```
.
├── main.py                  # 应用主代码（覆盖全部基础功能）
├── pyproject.toml           # 项目元数据、依赖、构建配置
├── requirements.txt         # 依赖清单（兼容 pip install -r）
├── Dockerfile               # 容器化部署
├── .dockerignore            # Docker 构建排除项
├── .env.example             # 环境变量示例
├── .gitignore
├── README.md
├── tests/
│   ├── __init__.py
│   └── test_main.py         # 接口单元测试（httpx + pytest）
└── .github/
    └── workflows/
        └── ci.yml           # GitHub Actions 持续集成
```

## 功能覆盖清单

| 模块 | 说明 |
|------|------|
| 数据模型 | Pydantic `BaseModel`、字段校验 `Field`、邮箱校验 `EmailStr` |
| 路由 | GET/POST/PUT，路径参数、查询参数（含列表/布尔） |
| 请求体 | JSON 请求体、表单 `Form`、文件上传 `File`/`UploadFile` |
| 依赖注入 | `Depends`、可复用依赖、数据库会话模拟 |
| 中间件 | 自定义 HTTP 中间件（记录请求耗时） |
| 异常处理 | `@exception_handler`、手动 `HTTPException` |
| Header/Cookie | 读取请求头、Cookie |
| 响应 | `JSONResponse`、`HTMLResponse`、自定义状态码与响应头 |
| 后台任务 | `BackgroundTasks` |

项目配置集中在 `pyproject.toml`；`requirements.txt` 保留为 pip 安装兼容入口。

运行 `python main.py` 时会读取 `.env.example` 中列出的变量名；默认不会自动加载 `.env`
文件。需要从文件加载时，请先导出变量，或使用支持环境文件的启动方式。

## 快速开始

### 方式一：pip 直接安装

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 方式二：可编辑安装（推荐，含开发依赖）

```bash
pip install -e ".[dev]"
uvicorn main:app --reload
```

### 方式三：Docker

```bash
docker build -t fastapi-example .
docker run -p 8000:8000 fastapi-example
```

## 交互文档

启动后访问：
- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

## 运行测试

```bash
pytest
```

测试使用 `httpx.AsyncClient` + `ASGITransport` 直接调用应用，无需启动真实服务器。

## 代码质量

```bash
# 静态检查
ruff check .

# 格式化
ruff format .
```

> **安全说明：**`/login/` 中的硬编码用户名、密码和伪 JWT，以及 `/protected/` 中的查询 token 都是教学示例，不应用于生产认证。项目未实现真实密码哈希、JWT 签名、数据库持久化或授权策略。

## 快速测试示例

```bash
# 根路径
curl http://127.0.0.1:8000/

# 路径参数 + 查询参数
curl "http://127.0.0.1:8000/hello/元宝?greeting=Hi"

# 创建商品（请求体）
curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name":"苹果","price":5.0,"description":"红富士"}'

# 受保护接口（依赖注入）
curl "http://127.0.0.1:8000/protected/?token=abc"

# 文件上传
curl -X POST http://127.0.0.1:8000/upload/ -F "file=@./README.md"

# 后台任务
curl -X POST "http://127.0.0.1:8000/send-notification/?email=test@example.com"
```

## License

MIT
