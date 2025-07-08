import time  # Python标准库，获取当前时间戳。常用于生成唯一数据。
import grpc  # gRPC官方库，支持高性能RPC通信。大厂微服务/IoT常用。
import random  # Python标准库，生成随机数。用于模拟真实数据变化。
import string  # Python标准库，提供字符串常量。用于生成随机字符串。
import json  # Python标准库，JSON数据处理。用于生成结构化数据。
from app import telemetry_pb2, telemetry_pb2_grpc  # 导入gRPC生成的消息和服务类。

# 创建到gRPC服务器的连接
# grpc.insecure_channel() 创建不安全的连接（无TLS加密）
# "localhost:50051" 连接到本地50051端口，这是gRPC的默认端口
channel = grpc.insecure_channel("localhost:50051")
# 工程意义：gRPC是高性能、跨语言的RPC框架，适合微服务、IoT等场景。

# 创建客户端存根（stub）
# 存根是gRPC客户端的代理，用于调用服务器上的RPC方法
# TelemetryIngestStub 是从proto文件生成的客户端存根类
stub = telemetry_pb2_grpc.TelemetryIngestStub(channel)
# 学习点：gRPC客户端和服务端解耦，便于多语言互通和分布式部署。

def generate_sensor_data():
    """
    生成模拟传感器数据
    模拟温度、湿度、压力等传感器读数
    
    返回:
    - bytes: JSON格式的传感器数据
    
    工程意义：
    - 模拟真实IoT设备的传感器数据
    - 包含多种数据类型和数值范围
    - 便于测试数据处理和解析逻辑
    """
    sensor_data = {
        "temperature": round(random.uniform(20.0, 35.0), 2),  # 温度 20-35°C
        "humidity": round(random.uniform(30.0, 80.0), 2),     # 湿度 30-80%
        "pressure": round(random.uniform(980.0, 1020.0), 2),  # 气压 980-1020 hPa
        "light": random.randint(0, 1000),                     # 光照 0-1000 lux
        "battery": round(random.uniform(20.0, 100.0), 2),    # 电池电量 20-100%
        "signal_strength": random.randint(-80, -30),          # 信号强度 -80到-30 dBm
        "timestamp": int(time.time() * 1000)  # 毫秒级时间戳
    }
    return json.dumps(sensor_data).encode('utf-8')

def generate_binary_data():
    """
    生成模拟二进制数据
    模拟图像、音频、视频等二进制数据
    
    返回:
    - bytes: 随机二进制数据
    
    工程意义：
    - 模拟真实IoT设备的二进制数据传输
    - 测试大数据量处理能力
    - 验证内存和网络性能
    """
    # 生成100-500字节的随机二进制数据
    length = random.randint(100, 500)
    return bytes(random.getrandbits(8) for _ in range(length))

def generate_text_data():
    """
    生成模拟文本数据
    模拟日志、消息、配置等文本数据
    
    返回:
    - bytes: 随机文本数据
    
    工程意义：
    - 模拟日志文件、配置文件等文本数据
    - 测试文本处理和分析能力
    - 验证编码和字符集处理
    """
    # 生成不同类型的文本数据
    text_types = [
        "INFO: System running normally",
        "WARNING: High temperature detected",
        "ERROR: Connection timeout",
        "DEBUG: Processing sensor data",
        "ALERT: Battery level low"
    ]
    
    # 随机选择文本类型并添加随机参数
    base_text = random.choice(text_types)
    random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    random_value = round(random.uniform(0, 100), 2)
    
    text_data = f"{base_text} | ID: {random_id} | Value: {random_value}"
    return text_data.encode('utf-8')

def generate_random_payload():
    """
    生成随机payload数据
    随机选择不同类型的模拟数据
    
    返回:
    - bytes: 随机生成的字节数据
    
    工程意义：
    - 模拟真实IoT设备的数据多样性
    - 确保每次传输的数据都不同
    - 便于测试不同类型数据的处理逻辑
    """
    # 随机选择数据类型
    data_type = random.choice(['sensor', 'binary', 'text'])
    
    if data_type == 'sensor':
        return generate_sensor_data()
    elif data_type == 'binary':
        return generate_binary_data()
    else:
        return generate_text_data()

def gen_packets(n=10000):
    """
    生成器函数：产生测试数据包
    模拟IoT设备持续发送数据
    
    参数:
    - n: 要生成的数据包数量，默认10000个
    
    返回:
    - 生成器对象，可以迭代产生Packet对象
    
    这个函数模拟了真实IoT设备的行为：
    1. 持续产生数据包
    2. 每个数据包包含设备ID、时间戳和数据载荷
    3. 使用yield实现流式数据产生
    4. 每次生成不同的随机payload数据
    5. 模拟多个设备同时发送数据
    工程意义：流式数据生成适合高并发/大数据量场景。
    """
    device_ids = [f"sensor-{i}" for i in range(1, 6)]  # 5个不同的设备ID
    
    for i in range(n):
        device_id = random.choice(device_ids)  # 随机选择设备ID
        yield telemetry_pb2.Packet(
            device_id=device_id,                           # 随机设备ID
            timestamp=int(time.time() * 1000) + i,        # 毫秒级递增时间戳
            payload=generate_random_payload(),             # 随机生成的payload数据
        )

# 发送10000个测试数据包到gRPC服务器
# stub.StreamPackets() 调用服务器上的StreamPackets RPC方法
# gen_packets(10000) 产生10000个测试数据包
# 这是一个阻塞调用，会等待所有数据包发送完成
stub.StreamPackets(gen_packets(10000))
print("✅ Sent 10000 packets with diverse random payloads")  # 打印成功消息，确认数据包已发送
# 工程意义：自动化测试/模拟数据发送是实际工程开发和调试的常用手段。
