"""gRPC 服务启动脚本（测试 / 本地运行用）

运行方法：
    python -m test.server   # 在项目根目录执行

功能说明：
1. 创建 ThreadPoolExecutor 作为 gRPC 线程池(10 个工作线程足够本地测试)。
2. 实例化业务层 `TelemetryServiceServicer` 并注册到 gRPC 服务器。
3. 监听 0.0.0.0:50051 端口(明文，不启用 TLS,便于调试)。
4. 打印启动日志，最后阻塞在 `wait_for_termination()`，直到 Ctrl+C 结束。
"""

import grpc
from concurrent import futures

# 导入自动生成的 gRPC 绑定代码
from generated.telemetry.v1 import telemetry_pb2_grpc

# 导入业务实现类：包含 SendTelemetry / GetTelemetry 等方法
from app.grpc_server import TelemetryServiceServicer

def serve() -> None:
    """启动 gRPC 服务器"""

    # 1) 创建 gRPC Server，使用线程池处理并发请求
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 2) 注册业务 Servicer 到 gRPC Server
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(
        TelemetryServiceServicer(), server
    )

    # 3) 绑定端口（IPv6 + IPv4 通用写法）
    server.add_insecure_port("[::]:50051")

    # 4) 启动并阻塞等待
    server.start()
    print("[gRPC] Server started on 0.0.0.0:50051 (insecure)")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
