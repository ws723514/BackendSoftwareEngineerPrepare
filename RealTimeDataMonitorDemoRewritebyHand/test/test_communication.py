#!/usr/bin/env python3
"""
gRPC 服务器和客户端通讯测试脚本

这个脚本会：
1. 启动 gRPC 服务器（在后台线程中）
2. 创建客户端连接
3. 测试基本的 SendTelemetry 和 GetTelemetry 功能
4. 清理资源并退出

运行方法：
    python test_communication.py
"""

import time
import threading
import grpc
from concurrent import futures
from google.protobuf import any_pb2
from google.protobuf import wrappers_pb2

# 导入生成的 protobuf 代码
from generated.telemetry.v1 import telemetry_pb2, telemetry_pb2_grpc

# 导入业务实现
from app.grpc_server import TelemetryServiceServicer
from app.grpc_client import TelemetryClient


def start_server():
    """启动 gRPC 服务器（用于测试）"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(
        TelemetryServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("✅ gRPC 服务器已启动在端口 50051")
    return server


def test_basic_communication():
    """测试基本的客户端-服务器通讯"""
    print("\n🔄 开始测试基本通讯...")
    
    # 创建客户端连接
    with grpc.insecure_channel("localhost:50051") as channel:
        client = TelemetryClient(channel)
        
        # 创建 Any 类型的 content
        content_any = any_pb2.Any()
        content_string = wrappers_pb2.StringValue(value="这是一个测试遥测数据")
        content_any.Pack(content_string)
        
        # 测试数据
        test_telemetry = telemetry_pb2.TelemetryV2(
            id="test_001",
            type=telemetry_pb2.DataType.DATA_TYPE_SYSTEM,
            content=content_any
        )
        
        print(f"📤 发送遥测数据: ID={test_telemetry.id}, Type={test_telemetry.type}, Content={test_telemetry.content}")
        
        # 测试 SendTelemetry
        try:
            response = client.SendTelemetry(test_telemetry)
            print(f"✅ SendTelemetry 成功: {response.message}")
        except Exception as e:
            print(f"❌ SendTelemetry 失败: {e}")
            return False
        
        # 等待一下确保数据已存储
        time.sleep(0.1)
        
        # 测试 GetTelemetry
        try:
            response = client.GetTelemetry("test_001")
            print(f"✅ GetTelemetry 成功: ID={response.telemetry.id}, Content={response.telemetry.content}")
            return True
        except Exception as e:
            print(f"❌ GetTelemetry 失败: {e}")
            return False


def test_error_handling():
    """测试错误处理"""
    print("\n🔄 开始测试错误处理...")
    
    with grpc.insecure_channel("localhost:50051") as channel:
        client = TelemetryClient(channel)
        
        # 测试获取不存在的数据
        try:
            response = client.GetTelemetry("nonexistent_id")
            print(f"❌ 预期应该失败，但成功了: {response}")
            return False
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print(f"✅ 错误处理正确: {e.details()}")
                return True
            else:
                print(f"❌ 错误代码不正确: {e.code()}")
                return False
        except Exception as e:
            print(f"❌ 未预期的错误: {e}")
            return False


def main():
    """主测试函数"""
    print("🚀 开始 gRPC 通讯测试")
    
    # 启动服务器
    server = start_server()
    
    # 等待服务器启动
    time.sleep(1)
    
    try:
        # 运行测试
        basic_test_passed = test_basic_communication()
        error_test_passed = test_error_handling()
        
        # 总结结果
        print("\n📊 测试结果:")
        print(f"  基本通讯测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
        print(f"  错误处理测试: {'✅ 通过' if error_test_passed else '❌ 失败'}")
        
        if basic_test_passed and error_test_passed:
            print("\n🎉 所有测试都通过了！服务器和客户端通讯正常。")
        else:
            print("\n⚠️  部分测试失败，请检查实现。")
            
    finally:
        # 关闭服务器
        print("\n🔄 正在关闭服务器...")
        server.stop(grace=2)
        print("✅ 服务器已关闭")


if __name__ == "__main__":
    main() 