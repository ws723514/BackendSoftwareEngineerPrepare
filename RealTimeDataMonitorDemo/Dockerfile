################## Builder ##################
FROM python:3.12-slim AS builder
WORKDIR /code

# 1. 仅依赖
COPY pyproject.toml poetry.lock* ./
RUN pip install --upgrade pip \
 && pip install poetry==1.8.3 \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --only main --no-root

# 2. 复制源码 + 安装当前项目
COPY . /code
RUN poetry install --no-interaction --no-ansi

################## Runtime ##################
FROM python:3.12-slim
WORKDIR /app

# ← 把 **python 运行时依赖** 拷过来
COPY --from=builder /usr/local /usr/local

# ← 把项目源码拷过来
COPY --from=builder /code /app

EXPOSE 8000 50051
CMD ["sh", "-c", "python -m app.ingest & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
