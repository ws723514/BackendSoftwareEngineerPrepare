import asyncio
from fastapi import FastAPI
from .pipeline import aggregator, get_metrics_snapshot

app = FastAPI(title="RealTime Packet Monitor Demo")


@app.on_event("startup")
async def startup() -> None:
    asyncio.get_event_loop().create_task(aggregator())


@app.get("/metrics")
async def metrics():
    return get_metrics_snapshot()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
