FROM python:3.12-slim

WORKDIR /app

# 先复制依赖清单，利用 Docker 缓存
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]"

# 复制源码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
