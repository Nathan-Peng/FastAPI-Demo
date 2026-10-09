"""
针对 main.py 各接口的单元测试
使用 httpx 的 ASGITransport 直接调用 FastAPI 应用，无需启动真实服务器
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "欢迎" in resp.json()["message"]


@pytest.mark.anyio
async def test_hello(client):
    resp = await client.get("/hello/元宝?greeting=Hi")
    assert resp.json()["message"] == "Hi, 元宝!"


@pytest.mark.anyio
async def test_read_item(client):
    resp = await client.get("/items/42?q=test&short=true")
    data = resp.json()
    assert data["item_id"] == 42
    assert data["q"] == "test"
    assert data["short"] is True


@pytest.mark.anyio
async def test_create_item(client):
    payload = {"name": "香蕉", "price": 3.5, "description": "新鲜香蕉"}
    resp = await client.post("/items/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "香蕉"
    assert data["item_id"] == 1


@pytest.mark.anyio
async def test_create_item_invalid(client):
    # 价格为负数，应被 Pydantic 校验拒绝
    resp = await client.post("/items/", json={"name": "坏商品", "price": -1})
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_update_item(client):
    payload = {"name": "橘子", "price": 4.0}
    resp = await client.put("/items/1", json=payload)
    assert resp.status_code == 200
    assert resp.json()["name"] == "橘子"


@pytest.mark.anyio
async def test_search(client):
    # 重复查询参数 ?q=a&q=b 需用 params 传入列表
    resp = await client.get("/search/", params={"q": ["a", "b"]})
    assert resp.json()["query"] == ["a", "b"]


@pytest.mark.anyio
async def test_login_success(client):
    resp = await client.post(
        "/login/",
        data={"username": "admin", "password": "secret"},
    )
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.anyio
async def test_login_fail(client):
    resp = await client.post(
        "/login/",
        data={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_protected_with_token(client):
    resp = await client.get("/protected/?token=abc123")
    assert resp.status_code == 200
    assert resp.json()["token"] == "abc123"


@pytest.mark.anyio
async def test_protected_without_token(client):
    resp = await client.get("/protected/")
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_html_response(client):
    resp = await client.get("/html/")
    assert resp.status_code == 200
    assert "Hello, FastAPI!" in resp.text


@pytest.mark.anyio
async def test_custom_status(client):
    resp = await client.get("/custom-status/")
    assert resp.status_code == 202
    assert resp.headers["X-Custom"] == "value"


@pytest.mark.anyio
async def test_get_user_found(client):
    resp = await client.get("/users/1")
    assert resp.status_code == 200
    assert resp.json()["username"] == "demo"


@pytest.mark.anyio
async def test_get_user_not_found(client):
    resp = await client.get("/users/999")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_upload_file(client):
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    resp = await client.post("/upload/", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.txt"
    assert data["size"] == 11


@pytest.mark.anyio
async def test_upload_multiple(client):
    files = [
        ("files", ("a.txt", b"aaa", "text/plain")),
        ("files", ("b.txt", b"bbbb", "text/plain")),
    ]
    resp = await client.post("/upload-multi/", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["filename"] == "a.txt"
    assert data[1]["size"] == 4


@pytest.mark.anyio
async def test_send_notification(client):
    resp = await client.post("/send-notification/?email=test@example.com")
    assert resp.status_code == 200
    assert "后台处理中" in resp.json()["msg"]


@pytest.mark.anyio
async def test_headers(client):
    resp = await client.get(
        "/headers/",
        headers={"User-Agent": "pytest", "X-Token": "tok"},
    )
    data = resp.json()
    assert data["User-Agent"] == "pytest"
    assert data["X-Token"] == "tok"
