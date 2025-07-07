import time
import grpc
from app import telemetry_pb2, telemetry_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = telemetry_pb2_grpc.TelemetryIngestStub(channel)


def gen_packets(n=10):
    for _ in range(n):
        yield telemetry_pb2.Packet(
            device_id="sensor-1",
            timestamp=int(time.time()),
            payload=b"abcd",
        )


stub.StreamPackets(gen_packets(10))
print("✅ Sent 10 packets")
