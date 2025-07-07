# RealTimeDataMonitorDemo

FastAPI + gRPC + asyncio 的实时数据监控 Demo

## 本地运行

```bash
poetry install            # 安装依赖
poetry run make proto     # 生成 gRPC stub
poetry run python -m app.ingest      # 终端1
poetry run uvicorn app.main:app --reload   # 终端2
poetry run python send_once.py       # 终端3：发送测试包
