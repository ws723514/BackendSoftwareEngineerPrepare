"""
    1.gRPC 服务器架构理解
        Servicer 是什么？
            类似于 Web 框架中的 Controller
            继承自生成的 TelemetryServiceServicer 基类
            实现具体的业务逻辑

    2. 四种 RPC 模式的实现差异
        单向调用:   def method(request,             context) -> response
        服务器流:   def method(request,             context) -> Iterator[response]
        客户端流:   def method(request_iterator,    context) -> response
        双向流:     def method(request_iterator,    context) -> Iterator[response]

    3.消息类型映射关系
    protobuf 定义 → Python 类
    message TelemetryServiceSendTelemetryRequest → telemetry_pb2.TelemetryServiceSendTelemetryRequest

    4. 错误处理机制
    如何使用 context.set_code() 和 context.set_details()
    gRPC 状态码的含义
    异常处理的最佳实践
        
    5. 服务器生命周期管理
    如何启动服务器
    线程池配置
    优雅关闭
"""
from generated.telemetry.v1 import telemetry_pb2, telemetry_pb2_grpc
import grpc


class TelemetryServiceServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def __init__(self):
        # 简易内存数据源：键=id，值=TelemetryV2；后续可替换 Redis/Kafka
        self.telemetry_datasource: dict[str, telemetry_pb2.TelemetryV2] = {}  # type: ignore[attr-defined]


    
    # 单向发送遥测数据
    def SendTelemetry(self, request, context):
        client_id = request.client_id

        # 把收到的遥测数据写入内存数据源
        self.telemetry_datasource[request.telemetry.id] = request.telemetry

        # 构造并返回响应消息
        return telemetry_pb2.TelemetryServiceSendTelemetryResponse(  # type: ignore[attr-defined]
            success=True,
            message=f"{client_id} 遥测数据发送成功"
        )
        
    # 获取遥测数据
    def GetTelemetry(self, request, context):
        if request.id in self.telemetry_datasource:
            return telemetry_pb2.TelemetryServiceGetTelemetryResponse(  # type: ignore[attr-defined]
                telemetry=self.telemetry_datasource[request.id]
            )

        context.abort(grpc.StatusCode.NOT_FOUND, f"遥测数据 {request.id} 不存在")
        
    # 流式发送遥测数据
    def StreamTelemetry(self, request_iterator, context):
        for req in request_iterator:
            target_id = req.telemetry.id  # StreamTelemetryRequest 内含 telemetry
            if target_id in self.telemetry_datasource:
                yield telemetry_pb2.TelemetryServiceStreamTelemetryResponse(  # type: ignore[attr-defined]
                    telemetry=self.telemetry_datasource[target_id]
                )
            else:
                context.abort(grpc.StatusCode.NOT_FOUND, f"遥测数据 {target_id} 不存在")


        # 如果整个流结束也未命中，可选择在此处 abort；此 demo 直接结束生成器
        

    """
    # 订阅遥测数据
    # 1. 方法
    # 输入：TelemetryServiceSubscribeTelemetryRequest（客户端发来的订阅请求，里面可能有过滤条件等）
    # 输出：stream TelemetryServiceSubscribeTelemetryResponse（服务器会不断推送遥测数据）

    # 2. 作用说明
    # SubscribeTelemetry 是一个“服务器流”RPC方法，主要用于客户端订阅实时遥测数据。
    # 客户端发起一次订阅请求，服务器会不断地把新的遥测数据推送给客户端（而不是只返回一条）。
    # 典型场景：客户端想要实时接收某类数据的推送，比如监控、告警、实时仪表盘等。

    # 3.Python 端实现思路
    # 你需要实现一个生成器（generator），每当有新的遥测数据时就 yield 一条响应。
    # 只要客户端不主动断开，服务器就可以一直推送数据。
    """
    def SubscribeTelemetry(self, request, context):
        """
        filter = request.filter
        # telemetry_datasource 是 list[telemetry_pb2.TelemetryV2]
        # filter 是 TelemetryService SubscribeTelemetryRequest 中的 filter
        for telemetry_data in self.telemetry_datasource.values(): 
            if filter in (telemetry_data, filter):
                response = telemetry_pb2.TelemetryServiceSubscribeTelemetryResponse(  # type: ignore[attr-defined]
                    telemetry = telemetry_data
                )
                yield response
            else:
                continue
        """
        filter_expr = request.filter  # e.g., "type=SYSTEM"

        for telemetry_data in self.telemetry_datasource.values():
            # 简单示例：按类型匹配
            if filter_expr and filter_expr.startswith("type="):
                expected_type = filter_expr.split("=", 1)[1]
                if str(telemetry_data.type) != expected_type:
                    continue

            yield telemetry_pb2.TelemetryServiceSubscribeTelemetryResponse(  # type: ignore[attr-defined]
                telemetry = telemetry_data
            )
    