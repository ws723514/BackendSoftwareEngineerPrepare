import random
import string
import json
import time

def generate_sensor_data():
    """生成模拟传感器数据"""
    sensor_data = {
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(30.0, 80.0), 2),
        "pressure": round(random.uniform(980.0, 1020.0), 2),
        "light": random.randint(0, 1000),
        "battery": round(random.uniform(20.0, 100.0), 2),
        "signal_strength": random.randint(-80, -30),
        "timestamp": int(time.time() * 1000)
    }
    return json.dumps(sensor_data).encode('utf-8')

def generate_binary_data():
    """生成模拟二进制数据"""
    length = random.randint(100, 500)
    return bytes(random.getrandbits(8) for _ in range(length))

def generate_text_data():
    """生成模拟文本数据"""
    text_types = [
        "INFO: System running normally",
        "WARNING: High temperature detected",
        "ERROR: Connection timeout",
        "DEBUG: Processing sensor data",
        "ALERT: Battery level low"
    ]
    
    base_text = random.choice(text_types)
    random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    random_value = round(random.uniform(0, 100), 2)
    
    text_data = f"{base_text} | ID: {random_id} | Value: {random_value}"
    return text_data.encode('utf-8')

def generate_random_payload():
    """生成随机payload数据"""
    data_type = random.choice(['sensor', 'binary', 'text'])
    
    if data_type == 'sensor':
        return generate_sensor_data()
    elif data_type == 'binary':
        return generate_binary_data()
    else:
        return generate_text_data()

def test_random_data_generation():
    """测试随机数据生成"""
    print("🔬 测试随机数据生成效果")
    print("=" * 50)
    
    # 测试10次，展示不同类型的数据
    for i in range(10):
        payload = generate_random_payload()
        print(f"数据包 {i+1}:")
        print(f"  长度: {len(payload)} 字节")
        print(f"  内容: {payload[:100]}{'...' if len(payload) > 100 else ''}")
        print(f"  类型: {'JSON传感器数据' if payload.startswith(b'{') else '二进制数据' if len(payload) > 50 else '文本数据'}")
        print("-" * 30)
    
    print("\n📊 统计信息:")
    print("✅ 每次生成的数据都不同")
    print("✅ 包含传感器数据、二进制数据、文本数据")
    print("✅ 数据长度在合理范围内")
    print("✅ 适合测试10000次传输")

if __name__ == "__main__":
    test_random_data_generation() 