"""A small ASGI application. Uvicorn owns sockets and the asyncio event loop."""
import asyncio
import json
import os
import re
from urllib.parse import parse_qs
import uvicorn

def integer(value, minimum, maximum):
    if value is None or len(value) > 8 or re.fullmatch(r"-?(0|[1-9][0-9]*)", value) is None:
        raise ValueError("invalid_query")
    number = int(value)
    if not minimum <= number <= maximum:
        raise ValueError("invalid_query")
    return number

async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            event = await receive()
            if event["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif event["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    if scope["type"] != "http":
        return
    headers = [(b"content-type", b"application/json")]
    status = 200
    if scope["method"] != "GET":
        status, data = 405, {"error": "method_not_allowed"}
        headers.append((b"allow", b"GET"))
    else:
        try:
            raw_query = scope["query_string"].decode("ascii")
            if scope["path"] in ("/sum", "/wait") and re.search(r"[;]|%(?![0-9a-fA-F]{2})", raw_query):
                raise ValueError("invalid_query")
            query = parse_qs(raw_query, keep_blank_values=True)
            def first(key, default=None):
                return query.get(key, [default])[0]
            if scope["path"] == "/health":
                data = {"ok": True}
            elif scope["path"] == "/sum":
                a = integer(first("a"), -1000000, 1000000)
                b = integer(first("b"), -1000000, 1000000)
                data = {"sum": a + b}
            elif scope["path"] == "/wait":
                ms = integer(first("ms", "50"), 0, 1000)
                await asyncio.sleep(ms / 1000)
                data = {"waited_ms": ms}
            else:
                status, data = 404, {"error": "not_found"}
        except ValueError:
            status, data = 400, {"error": "invalid_query"}
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": json.dumps(data).encode("utf-8")})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "3002")),
                loop="asyncio", http="h11", timeout_graceful_shutdown=5)
