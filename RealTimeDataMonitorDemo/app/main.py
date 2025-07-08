import asyncio  # Python标准库，支持异步编程。大厂后端高并发/高性能服务必备。
import os  # 读取环境变量
from fastapi import FastAPI  # FastAPI是现代Python Web框架，自动生成API文档，适合微服务和API开发。
from .pipeline import aggregator, get_metrics_snapshot  # 导入数据处理管道和快照函数。

""" aggregator Learning Notes:
    aggregator() - 数据处理管道
    作用：
        后台协程：持续从队列中消费数据包并更新计数
        生产者-消费者模式：gRPC服务作为生产者，aggregator作为消费者
    
    大厂使用场景：
    单进程场景：适合小规模应用，内存计数
    多进程场景：建议用Redis/Kafka等中间件
    高并发场景：队列解耦，避免阻塞

    实际使用注意事项：
    内存限制：队列大小限制防止OOM
    错误处理：需要try-catch处理异常
    监控告警：队列积压、处理延迟监控
    优雅关闭：需要正确处理协程关闭

    本工程未使用队列，直接在aggregator中处理数据包。   
"""

""" get_metrics_snapshot Learning Notes:
    作用：
    数据查询接口：返回当前计数的浅拷贝
    API数据格式：转换为前端友好的JSON格式

    大厂使用场景：
    监控面板：实时数据展示
    API接口：供其他系统调用
    数据导出：批量数据查询

    实际使用注意事项：
    数据一致性：多进程下需要分布式锁
    性能优化：大数据量需要分页
    缓存策略：频繁查询需要Redis缓存
    数据格式：需要版本控制和向后兼容
"""


""" FastAPI Learning Notes:

"""
import redis  # 第三方库，连接Redis。大厂常用的分布式缓存/计数/状态同步中间件。

# 读取 Redis 连接信息：容器化场景下通过环境变量注入
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, db=0)  # 连接Redis服务

# 创建FastAPI应用实例，设置标题
# FastAPI是一个现代、快速的Python Web框架，基于Starlette和Pydantic
# title参数会显示在自动生成的API文档中
app = FastAPI(title="RealTime Packet Monitor Demo")

@app.on_event("startup")
async def startup() -> None: 
    """
    应用启动事件处理器
    在FastAPI应用启动时自动执行
    用于启动后台数据处理协程
    
    工程意义：
    - 确保数据处理管道在Web服务启动时就开始工作
    - 避免HTTP请求到达时还没有数据处理能力
    - 实际工程中，所有需要后台运行的任务都应在startup事件里注册
    """
    asyncio.get_event_loop().create_task(aggregator())  # 启动后台数据处理协程

@app.get("/metrics")
async def metrics():
    """
    HTTP GET接口：/metrics
    返回Redis中的实时统计数据
    工程意义：
    - 这是前端/其他系统获取实时数据的标准API接口
    - 直接从Redis读取，保证多进程/多服务下数据一致性
    """
    metrics = r.hgetall("device_metrics")  # 从Redis哈希表读取所有设备计数
    # 转换为前端友好的格式
    return [{"device_id": k.decode("utf-8"), "count": int(v)} for k, v in metrics.items()]

if __name__ == "__main__":
    import uvicorn  # Uvicorn是ASGI服务器，适合运行FastAPI应用。
    # 直接运行时的启动配置
    # uvicorn是ASGI服务器，用于运行FastAPI应用
    # host="0.0.0.0": 监听所有网络接口，允许外部访问
    # port=8000: FastAPI的默认端口
    # reload=True: 启用热重载，开发时文件变化自动重启
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
