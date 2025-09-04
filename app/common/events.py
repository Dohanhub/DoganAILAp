import os
import json
import asyncio
import redis.asyncio as redis
from typing import Awaitable, Callable


STREAM = os.getenv("EVENT_STREAM", "compliance.events")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def _client():
    return redis.from_url(REDIS_URL, decode_responses=True)


async def publish(event_type: str, data: dict):
    if os.getenv("FEATURE_EVENTS", "true").lower() not in {"1", "true", "yes"}:
        return
    r = await _client()
    await r.xadd(STREAM, {"type": event_type, "data": json.dumps(data)})


async def consume(group: str, name: str, handler: Callable[[dict], Awaitable[None]]):
    r = await _client()
    try:
        await r.xgroup_create(STREAM, group, id="$", mkstream=True)
    except Exception:
        pass
    while True:
        msgs = await r.xreadgroup(group, name, {STREAM: ">"}, count=100, block=5000)
        for _, entries in msgs or []:
            for id_, kv in entries:
                try:
                    data = json.loads(kv.get("data", "{}"))
                    await handler(data)
                finally:
                    try:
                        await r.xack(STREAM, group, id_)
                    except Exception:
                        pass

