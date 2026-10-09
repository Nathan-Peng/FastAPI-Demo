"""
FastAPI 完整基础功能示例
覆盖：路由、路径参数、查询参数、请求体、表单、文件上传、依赖注入、
     中间件、异常处理、状态码、Header/Cookie、后台任务等
运行：uvicorn main:app --reload
文档：http://127.0.0.1:8000/docs
"""

from typing import Optional
from datetime import datetime

from fastapi import (
    FastAPI, Depends, HTTPException, Header, Cookie, File, UploadFile,
    Form, Request, BackgroundTasks, status, Query,
)
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field, EmailStr


# ============ 1. 数据模型（Pydantic）============
class Item(BaseModel):
    """请求体 / 响应模型示例"""
    name: str = Field(..., example="苹果", description="商品名称")
    price: float = Field(..., gt=0, description="价格必须大于0")
    description: Optional[str] = None
    tax: Optional[float] = None

    # 示例值（用于自动文档）
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "苹果", "price": 5.0, "description": "红富士", "tax": 0.5}
            ]
        }
    }


class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


# ============ 2. 创建应用实例 ============
app = FastAPI(
    title="FastAPI 完整示例",
    description="覆盖 FastAPI 所有基础功能的示例项目",
    version="1.0.0",
)


# ============ 3. 依赖注入 ============
def get_query_token(token: Optional[str] = None):
    """简单的依赖：验证查询 token"""
    if token is None:
        raise HTTPException(status_code=400, detail="缺少 token 参数")
    return token


def fake_db():
    """模拟数据库连接（实际项目中可替换为真实 DB 会话）"""
    db = {"items": {}, "users": {}}
    yield db
    # 此处可写清理逻辑


# ============ 4. 中间件 ============
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """记录每个请求的处理耗时"""
    start = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============ 5. 异常处理 ============
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"message": str(exc)})


# ============ 6. 路由示例 ============

# --- 6.1 基础路径操作 ---
@app.get("/", tags=["基础"])
async def root():
    """根路径，返回欢迎信息"""
    return {"message": "欢迎使用 FastAPI 完整示例"}


@app.get("/hello/{name}", tags=["基础"])
async def hello(name: str, greeting: str = "你好"):
    """
    路径参数 + 查询参数
    - name: 路径参数
    - greeting: 查询参数（可选，默认"你好"）
    """
    return {"message": f"{greeting}, {name}!"}


# --- 6.2 路径参数与类型校验 ---
@app.get("/items/{item_id}", tags=["路径参数"])
async def read_item(
    item_id: int,          # 路径参数，自动转为 int
    q: Optional[str] = None,  # 可选查询参数
    short: bool = False,    # 布尔查询参数
):
    """演示路径参数 + 多种查询参数"""
    item = {"item_id": item_id}
    if q:
        item["q"] = q
    if short:
        item["short"] = True
    return item


# --- 6.3 请求体（Pydantic 模型）---
@app.post("/items/", tags=["请求体"], status_code=status.HTTP_201_CREATED)
async def create_item(item: Item, db: dict = Depends(fake_db)):
    """创建商品，使用 Pydantic 模型校验请求体"""
    item_id = len(db["items"]) + 1
    db["items"][item_id] = item.model_dump()
    return {"item_id": item_id, **db["items"][item_id]}


@app.put("/items/{item_id}", tags=["请求体"])
async def update_item(item_id: int, item: Item):
    """更新商品"""
    return {"item_id": item_id, **item.model_dump()}


# --- 6.4 查询参数列表 ---
@app.get("/search/", tags=["查询参数"])
async def search(q: list[str] = Query(default=[])):
    """支持重复查询参数，如 ?q=a&q=b"""
    return {"query": q}


# --- 6.5 表单数据 ---
@app.post("/login/", tags=["表单"])
async def login(username: str = Form(...), password: str = Form(...)):
    """接收表单数据（Content-Type: application/x-www-form-urlencoded）"""
    if username == "admin" and password == "secret":
        return {"msg": "登录成功", "token": "fake-jwt-token"}
    raise HTTPException(status_code=401, detail="用户名或密码错误")


# --- 6.6 文件上传 ---
@app.post("/upload/", tags=["文件上传"])
async def upload_file(file: UploadFile = File(...)):
    """单文件上传"""
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }


@app.post("/upload-multi/", tags=["文件上传"])
async def upload_multiple(files: list[UploadFile] = File(...)):
    """多文件上传"""
    return [{"filename": f.filename, "size": len(await f.read())} for f in files]


# --- 6.7 依赖注入使用 ---
@app.get("/protected/", tags=["依赖注入"])
async def protected(token: str = Depends(get_query_token)):
    """需要 token 的受保护接口"""
    return {"message": "访问成功", "token": token}


# --- 6.8 Header / Cookie ---
@app.get("/headers/", tags=["Header/Cookie"])
async def read_headers(
    user_agent: Optional[str] = Header(None),
    x_token: Optional[str] = Header(None),
):
    """读取请求头"""
    return {"User-Agent": user_agent, "X-Token": x_token}


@app.get("/cookies/", tags=["Header/Cookie"])
async def read_cookies(session_id: Optional[str] = Cookie(None)):
    """读取 Cookie"""
    return {"session_id": session_id}


# --- 6.9 自定义响应 ---
@app.get("/html/", tags=["响应"], response_class=HTMLResponse)
async def get_html():
    """返回 HTML 响应"""
    return "<h1>Hello, FastAPI!</h1>"


@app.get("/custom-status/", tags=["响应"])
async def custom_status():
    """自定义状态码与响应头"""
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"msg": "已接受处理"},
        headers={"X-Custom": "value"},
    )


# --- 6.10 后台任务 ---
def write_log(message: str):
    """后台任务：写入日志（示例仅打印）"""
    print(f"[后台任务] {datetime.now()}: {message}")


@app.post("/send-notification/", tags=["后台任务"])
async def send_notification(
    background_tasks: BackgroundTasks,
    email: str,
):
    """触发后台任务（响应返回后再执行）"""
    background_tasks.add_task(write_log, f"通知已发送至 {email}")
    return {"msg": "通知已触发，后台处理中"}


# --- 6.11 手动触发 HTTP 异常 ---
@app.get("/users/{user_id}", tags=["错误处理"])
async def get_user(user_id: int):
    """模拟用户查询，不存在则抛出 404"""
    if user_id != 1:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user_id": 1, "username": "demo"}


# ============ 7. 启动入口 ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
