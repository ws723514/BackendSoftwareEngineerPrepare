import asyncio  # Python标准库，支持异步编程。大厂后端高并发/高性能服务必备。
import logging  # 标准库，做日志记录。实际工程日志是排查问题的生命线。
import os       # 读取环境变量，容器化后可灵活配置。
import redis    # 第三方库，连接Redis。大厂常用的分布式缓存/计数/状态同步中间件。

from grpc.aio import server  # gRPC异步服务器，支持高并发。大厂常用的RPC框架。
from . import telemetry_pb2, telemetry_pb2_grpc  # gRPC代码生成文件，定义消息结构和服务接口。

# 配置日志级别为INFO，这样可以看到服务器启动和运行信息
logging.basicConfig(level=logging.INFO)
# 工程意义：日志级别设置为INFO，既能看到关键事件，又不会被DEBUG信息刷屏。

# 连接Redis：优先使用环境变量（Docker compose 中使用），默认回退 localhost
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, db=0)
# 学习点：Redis是高并发场景下的首选缓存/计数/状态同步方案。实际工程几乎必用。

"""
TelemetryServicer类:
- 继承自生成的Servicer基类，实现proto文件中定义的服务接口
- 负责处理客户端发送的流式数据包
- 每收到一个包，就在Redis里按设备ID计数
工程意义：gRPC服务解耦了数据接收和处理，便于横向扩展和多语言互通。
"""
class TelemetryServicer(telemetry_pb2_grpc.TelemetryIngestServicer):
    async def StreamPackets(self, request_iterator, context):
        """
        实现proto文件中定义的StreamPackets RPC方法
        处理客户端发送的流式数据包
        每收到一个包，就在Redis里按设备ID计数
        工程意义：流式RPC能高效处理大量IoT设备/探针的实时数据。
        """
        async for pkt in request_iterator:  # 异步迭代，支持高并发数据流
            # 用Redis哈希表做分设备计数
            r.hincrby("device_metrics", pkt.device_id, 1)
            # 学习点：hincrby是Redis哈希自增操作，适合做分组计数。大厂常用。
        return telemetry_pb2.Ack(ok=True)  # 返回确认消息，告知客户端已收到
        # 工程意义：RPC接口要有返回，便于客户端确认数据已被处理。

async def serve() -> None:
    """
    启动gRPC服务器，注册服务实现类，监听50051端口。
    工程意义：服务注册和端口监听是所有微服务的基础。
    """
    s = server()  # 创建异步gRPC服务器实例

    # 注册服务实现类到服务器
    # 学习点：add_TelemetryIngestServicer_to_server是gRPC的注册方法。
    # 注册服务实现类到服务器
    telemetry_pb2_grpc.add_TelemetryIngestServicer_to_server(TelemetryServicer(), s)
    
    s.add_insecure_port("[::]:50051")  # 监听所有网卡的50051端口

    await s.start() # 启动服务器
    logging.info("🚚 gRPC ingest on :50051") # 记录启动日志
    await s.wait_for_termination()  # 阻塞，直到服务被关闭
    # 学习点：wait_for_termination是gRPC的阻塞方法。    


if __name__ == "__main__":
    # 当直接运行此文件时，启动gRPC服务器
    asyncio.run(serve())
    # 学习点：asyncio.run是Python3.7+推荐的异步主入口。实际工程常用。
