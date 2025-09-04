import os
import asyncio
import json
from typing import AsyncIterator, Tuple, Any, Callable, Awaitable

_q: "asyncio.Queue[Tuple[str, Any]]]" = asyncio.Queue()


async def publish(topic: str, data: Any) -> None:
    # If feature events on, publish to Redis Streams via common.events
    if os.getenv("FEATURE_EVENTS", "true").lower() in {"1", "true", "yes"}:
        try:
            from ..common.events import publish as bus_publish  # type: ignore
            await bus_publish(topic, data if isinstance(data, dict) else {"value": data})
            return
        except Exception:
            pass
    await _q.put((topic, data))


async def sse_stream() -> AsyncIterator[str]:
    # If feature events on, consume from Redis Streams and fan-in to a local queue
    if os.getenv("FEATURE_EVENTS", "true").lower() in {"1", "true", "yes"}:
        try:
            from ..common.events import consume  # type: ignore

            out: "asyncio.Queue[Tuple[str, Any]]" = asyncio.Queue()

            async def handler(data: dict):
                await out.put((data.get("type", "compliance.update"), data))

            loop = asyncio.get_event_loop()
            loop.create_task(consume("sse", os.getenv("HOSTNAME", "client"), handler))

            while True:
                topic, data = await out.get()
                yield f"event: {topic}\n" + f"data: {json.dumps(data)}\n\n"
        except Exception:
            pass
    # Fallback to in-memory queue
    while True:
        topic, data = await _q.get()
        payload = data if isinstance(data, str) else json.dumps(data)
        yield f"event: {topic}\n" + f"data: {payload}\n\n"
