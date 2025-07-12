import grpc
from generated.telemetry.v1 import telemetry_pb2, telemetry_pb2_grpc


class TelemetryClient:
    def __init__(self, channel: grpc.Channel):

        self.stub = telemetry_pb2_grpc.TelemetryServiceStub(channel)
        self.channel = channel
        
    
    def SendTelemetry(self, telemetry_data: telemetry_pb2.TelemetryV2):  # type: ignore[attr-defined]
        # local data source 中添加遥测数据到字典数据库中
        # wrong code: self.telemetry_datasource[telemetry.id] = telemetry  即使是存入本地数据源，也要通过stub调用rpc

        # 创建请求对象
        # 原始代码 - 注释原因：变量名'request'不够明确，改为'send_request'以明确表示这是发送的请求
        # request = telemetry_pb2.TelemetryServiceSendTelemetryRequest(  # type: ignore[attr-defined]
        #     telemetry = telemetry_data,
        #     client_id = "client_1",
        #     priority = telemetry_pb2.TelemetryPriority.TELEMETRY_PRIORITY_HIGH  # type: ignore[attr-defined]
        # )
        # 新代码 - 改进：使用更清晰的变量名
        send_request = telemetry_pb2.TelemetryServiceSendTelemetryRequest(  # type: ignore[attr-defined]
            telemetry = telemetry_data,
            client_id = "client_1",
            priority = telemetry_pb2.TelemetryPriority.TELEMETRY_PRIORITY_HIGH  # type: ignore[attr-defined]
        )

        # 调用 gRPC 服务发送遥测数据
        # 原始代码 - 注释原因：直接return不够清晰，改为明确的'receive_response'变量名
        # return self.stub.SendTelemetry(request)
        # 新代码 - 改进：使用明确的变量名表示这是接收到的响应
        receive_response = self.stub.SendTelemetry(send_request)
        return receive_response

    def GetTelemetry(self, id_data: str):
        # 原始代码 - 注释原因：变量名'request'不够明确，改为'send_request'以明确表示这是发送的请求
        # request = telemetry_pb2.TelemetryServiceGetTelemetryRequest(  # type: ignore[attr-defined]
        #     id = id_data 
        # )
        # 新代码 - 改进：使用更清晰的变量名
        send_request = telemetry_pb2.TelemetryServiceGetTelemetryRequest(  # type: ignore[attr-defined]
            id = id_data 
        )
        
        # 原始代码 - 注释原因：变量名'response'不够明确，改为'receive_response'以明确表示这是接收的响应
        # response = self.stub.GetTelemetry(request)
        # return response
        # 新代码 - 改进：使用明确的变量名表示这是接收到的响应
        receive_response = self.stub.GetTelemetry(send_request)
        return receive_response
    
    def StreamTelemetry(self, filter: str):
        request = telemetry_pb2.TelemetryServiceStreamTelemetryRequest(  # type: ignore[attr-defined]
            filter = filter
        )
    
    # 客户端流
    # 客户端发送请求订阅，然后服务器发送流式响应
    def SubscribeTelemetry(self, filter: str):
        request = telemetry_pb2.TelemetryServiceSubscribeTelemetryRequest(  # type: ignore[attr-defined]
            fileter = "type=SYSTEM"
            response_
    
if __name__ == "__main__":
    # 原始代码 - 注释原因：protobuf类型使用错误，TelemetryType不存在，应该是DataType；content应该是Any类型
    # with grpc.insecure_channel("localhost:50051") as channel:
    #     client = TelemetryClient(channel)
    #     demo_data = telemetry_pb2.TelemetryV2(  # type: ignore[attr-defined]
    #         id = "1",
    #         type = telemetry_pb2.TelemetryType.SYSTEM,  # type: ignore[attr-defined]
    #         content = "test"
    #     )
    #     client.SendTelemetry(demo_data)
    #     response = client.GetTelemetry("1")
    #     print(response)
    
    # 新代码 - 改进：修复protobuf类型错误，使用正确的Any类型和清晰的变量命名
    from google.protobuf import any_pb2, wrappers_pb2
    
    print("🚀 启动 gRPC 客户端测试...")
    
    with grpc.insecure_channel("localhost:50051") as channel:
        client = TelemetryClient(channel)
        
        # 创建 Any 类型的 content - 改进：使用正确的protobuf Any类型
        content_any = any_pb2.Any()
        content_string = wrappers_pb2.StringValue(value="客户端测试数据")
        content_any.Pack(content_string)
        
        # 创建测试数据 - 改进：使用正确的DataType枚举
        demo_data = telemetry_pb2.TelemetryV2(  # type: ignore[attr-defined]
            id = "client_test_001",
            type = telemetry_pb2.DataType.DATA_TYPE_SYSTEM,  # type: ignore[attr-defined]
            content = content_any
        )
        
        print(f"📤 准备发送遥测数据: ID={demo_data.id}")
        print(f"   发送请求内容: 类型={demo_data.type}, 内容={demo_data.content}")
        try:
            # 原始代码 - 注释原因：变量名不够明确，改为'receive_response'以明确表示这是接收的响应
            # client.SendTelemetry(demo_data)
            # 新代码 - 改进：使用明确的变量名并显示详细的请求-响应过程
            print("   🔄 正在发送请求...")
            receive_response = client.SendTelemetry(demo_data)
            print(f"✅ 接收到服务器响应: {receive_response.message}")
            print(f"   响应状态: success={receive_response.success}")
        except Exception as e:
            print(f"❌ 发送请求失败: {e}")
            exit(1)
        
        print(f"📥 发送获取请求: ID=client_test_001")
        try:
            # 原始代码 - 注释原因：变量名不够明确，改为'receive_response'以明确表示这是接收的响应
            # response = client.GetTelemetry("1")
            # print(response)
            # 新代码 - 改进：使用明确的变量名并显示详细的请求-响应过程
            print("   🔄 正在发送获取请求...")
            receive_response = client.GetTelemetry("client_test_001")
            print(f"✅ 接收到服务器响应数据: ID={receive_response.telemetry.id}")
            print(f"   接收到的内容: {receive_response.telemetry.content}")
        except Exception as e:
            print(f"❌ 发送获取请求失败: {e}")
            exit(1)
        
        print("🎉 客户端测试完成！")








