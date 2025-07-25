#!/usr/bin/env python3
"""
SubscribeTelemetry 基础功能测试脚本
位置：test/test_subscribe_basic.py
用法：python -m test.test_subscribe_basic
"""

import grpc
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.grpc_client import TelemetryClient
from generated.telemetry.v1 import telemetry_pb2
from google.protobuf import any_pb2, wrappers_pb2

def test_subscribe_basic():
    """测试基础的SubscribeTelemetry订阅功能"""
    
    print("🧪 测试 SubscribeTelemetry 基础功能")
    print("=" * 50)
    
    try:
        # 连接服务器
        with grpc.insecure_channel("localhost:50051") as channel:
            client = TelemetryClient(channel)
            print("📡 连接服务器成功")
            
            # 先发送测试数据
            print("\n1️⃣ 准备测试数据...")
            
            # 创建系统类型数据
            content_any = any_pb2.Any()
            content_string = wrappers_pb2.StringValue(value="系统监控数据-测试")
            content_any.Pack(content_string)
            
            test_data = telemetry_pb2.TelemetryV2(  # type: ignore[attr-defined]
                id="system_test_001",
                type=telemetry_pb2.DataType.DATA_TYPE_SYSTEM,  # type: ignore[attr-defined]
                content=content_any
            )
            
            send_response = client.SendTelemetry(test_data)
            print(f"   ✅ 系统数据发送成功: {send_response.message}")
            
            # 创建应用类型数据（用于测试过滤）
            content_any2 = any_pb2.Any()
            content_string2 = wrappers_pb2.StringValue(value="应用程序数据-测试")
            content_any2.Pack(content_string2)
            
            test_data2 = telemetry_pb2.TelemetryV2(  # type: ignore[attr-defined]
                id="app_test_001",
                type=telemetry_pb2.DataType.DATA_TYPE_APPLICATION,  # type: ignore[attr-defined]
                content=content_any2
            )
            
            send_response2 = client.SendTelemetry(test_data2)
            print(f"   ✅ 应用数据发送成功: {send_response2.message}")
            
            # 测试订阅系统类型数据
            print("\n2️⃣ 开始订阅测试...")
            print("   过滤条件: type=DATA_TYPE_SYSTEM")
            print("   预期结果: 只接收到系统类型的数据")
            
            client.SubscribeTelemetry("type=DATA_TYPE_SYSTEM")
            
            print("\n✅ SubscribeTelemetry 基础功能测试完成！")
            
    except grpc.RpcError as e:
        print(f"❌ gRPC错误: {e}")
        print("💡 请确保服务器运行: python -m test.server")
    except Exception as e:
        print(f"❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_subscribe_basic() 