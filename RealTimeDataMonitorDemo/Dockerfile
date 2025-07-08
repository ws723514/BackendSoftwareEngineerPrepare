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

# 3. 生成 protobuf 代码
RUN python -m grpc_tools.protoc \
    --python_out=app \
    --grpc_python_out=app \
    --proto_path=proto \
    proto/telemetry.proto

# 4. 修复导入语句为相对导入
RUN sed -i 's/^import telemetry_pb2 as/from \. import telemetry_pb2 as/' app/telemetry_pb2_grpc.py

################## Runtime ##################
FROM python:3.12-slim
WORKDIR /app

# ← 把 **python 运行时依赖** 拷过来
COPY --from=builder /usr/local /usr/local

# ← 把项目源码拷过来，但只复制 app 目录
COPY --from=builder /code/app /app/app

EXPOSE 8000 50051
CMD ["sh", "-c", "cd /app && python -m app.ingest & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
