import asyncio
import logging

from grpc.aio import server
from . import telemetry_pb2, telemetry_pb2_grpc
from .pipeline import packet_queue

logging.basicConfig(level=logging.INFO)


class TelemetryServicer(telemetry_pb2_grpc.TelemetryIngestServicer):
    async def StreamPackets(self, request_iterator, context):
        async for pkt in request_iterator:
            await packet_queue.put(pkt)
        return telemetry_pb2.Ack(ok=True)


async def serve() -> None:
    s = server()
    telemetry_pb2_grpc.add_TelemetryIngestServicer_to_server(TelemetryServicer(), s)
    s.add_insecure_port("[::]:50051")
    await s.start()
    logging.info("🚚 gRPC ingest on :50051")
    await s.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
