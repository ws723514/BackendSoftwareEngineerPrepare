import asyncio
from collections import defaultdict
from typing import Dict, List

packet_queue: asyncio.Queue = asyncio.Queue(maxsize=10_000)
_metrics: Dict[str, int] = defaultdict(int)


async def aggregator() -> None:
    """后台协程：从队列消费包并更新计数"""
    while True:
        pkt = await packet_queue.get()
        _metrics[pkt.device_id] += 1
        packet_queue.task_done()


def get_metrics_snapshot() -> List[dict]:
    """返回当前计数的浅拷贝"""
    return [{"device_id": d, "count": c} for d, c in _metrics.items()]
