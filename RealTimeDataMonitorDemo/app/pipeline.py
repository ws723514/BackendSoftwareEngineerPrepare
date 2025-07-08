import asyncio  # Python标准库，支持异步编程。大厂后端高并发/高性能服务必备。
from collections import defaultdict  # defaultdict用于自动初始化字典值，避免KeyError。
from typing import Dict, List  # 类型注解，提升代码可读性和可维护性。

# 全局异步队列，用于存储待处理的数据包
# maxsize=10_000 限制队列大小，防止内存溢出
# 这是一个生产者-消费者模式的队列，gRPC服务作为生产者，aggregator协程作为消费者
packet_queue: asyncio.Queue = asyncio.Queue(maxsize=10_000)
# 工程意义：异步队列是高并发数据流的标准解耦方式。

# 全局指标存储，使用defaultdict避免KeyError
# Dict[str, int] 表示 {设备ID: 数据包计数}
# defaultdict(int) 意味着当访问不存在的键时，会自动创建值为0的条目
_metrics: Dict[str, int] = defaultdict(int)
# 工程意义：内存计数适合单进程/单服务场景，分布式场景建议用Redis等中间件。


async def aggregator() -> None:
    """
    后台协程：从队列消费包并更新计数
    这是整个系统的核心处理逻辑
    
    工作流程：
    1. 无限循环等待队列中的数据包
    2. 收到数据包后，按设备ID累加计数
    3. 标记任务完成，继续处理下一个数据包
    
    工程意义：
    - 生产者-消费者模式，解耦数据接收和处理
    - 实际大厂多进程/多服务场景建议用Redis等中间件同步状态
    """
    while True:  # 无限循环，持续处理数据
        pkt = await packet_queue.get()  # 异步等待队列中的数据包，如果队列为空会阻塞
        _metrics[pkt.device_id] += 1   # 按设备ID累加计数，如果设备ID不存在会自动创建
        packet_queue.task_done()        # 标记任务完成，用于队列同步


def get_metrics_snapshot() -> List[dict]:
    """
    返回当前计数的浅拷贝
    这个函数被FastAPI调用，提供实时统计数据的查询接口
    
    返回格式：
    [
        {"device_id": "sensor-1", "count": 10},
        {"device_id": "sensor-2", "count": 5},
        ...
    ]
    
    工程意义：
    - 适合单进程/单服务场景，分布式建议用Redis等中间件
    - 提供API端点的标准数据格式
    """
    return [{"device_id": d, "count": c} for d, c in _metrics.items()]
