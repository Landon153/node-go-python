# Python: backend, validation, database và workers

[README](../../README.vi.md) · [VI](python-backend.vi.md) · [EN](python-backend.en.md)

Python web có hai hướng nổi bật: full framework như Django và API/toolkit như FastAPI/Starlette hoặc Flask. Chọn theo sản phẩm và deployment; AI/data libraries không tự cung cấp HTTP/auth/transaction. Inline calls là fragment cần instance/import/config; recipe chạy riêng với prerequisites nêu bên dưới.

## Web framework và server

### FastAPI

**Công dụng và tình huống:** ASGI API framework có routing, dependency injection, Pydantic validation và OpenAPI. Dùng REST/prediction API có typed contract.

**Ví dụ:** `@app.post("/orders", response_model=OrderOut)` kiểm tra input/output theo model.

**Đánh giá:** Cần ASGI server; async route không tự offload CPU. Pydantic integration validate, type hint trong Python thường không tự validate. [Docs](https://fastapi.tiangolo.com/).

### Starlette

**Công dụng và tình huống:** ASGI toolkit cho routing/middleware/response/WebSocket/lifespan, nền cho FastAPI. Dùng app nhỏ muốn tự thiết kế contract.

**Ví dụ:** `Route("/health", health)` với handler trả `JSONResponse({"ok":True})`.

**Đánh giá:** Không có đầy đủ validation/OpenAPI như FastAPI; lifecycle và middleware phải được kiểm tra. [Docs](https://starlette.dev/).

### Django

**Công dụng và tình huống:** Full web framework có ORM, migration, auth, admin, template. Dùng business web app cần backoffice nhanh.

**Ví dụ:** Định nghĩa Product model → migrate → đăng ký admin để nhân viên quản lý catalog.

**Đánh giá:** Convention đầy đủ nhưng cần hiểu ORM/query/async compatibility; admin không thay authorization của public API. [Docs](https://docs.djangoproject.com/en/stable/).

### Django REST Framework

**Công dụng và tình huống:** Serializer/viewset/router/permission cho REST trên Django, tận dụng ORM/auth.

**Ví dụ:** `ModelSerializer` chọn fields id/name, `ReadOnlyModelViewSet` tạo endpoints đọc.

**Đánh giá:** Kiểm soát queryset/permission theo tenant và N+1; serializer field không tự lọc quyền row. [Docs](https://www.django-rest-framework.org/).

### Flask

**Công dụng và tình huống:** WSGI framework gọn cho API/service/dashboard nhỏ và app đồng bộ sẵn có.

**Ví dụ:** `@app.get("/health")` trả `{"ok":True}`.

**Đánh giá:** Tự chọn extensions; async view vẫn giữ WSGI worker cho request. Dùng production server phù hợp thay dev server. [Docs](https://flask.palletsprojects.com/en/stable/).

### Uvicorn

**Công dụng và tình huống:** ASGI server nhận socket/parse HTTP/chạy loop cho FastAPI/Starlette.

**Ví dụ:** `python -m uvicorn app:app --host 127.0.0.1 --port 3102` chạy app đã định nghĩa.

**Đánh giá:** Worker là process riêng, nhân bản memory/model/pool; không gộp reload với workers. [Docs](https://uvicorn.dev/settings/).

### Gunicorn

**Công dụng và tình huống:** Process manager/server trên UNIX cho WSGI hoặc worker ASGI tương thích.

**Ví dụ:** `gunicorn app:app -w 2` cho WSGI; ASGI dùng `-k uvicorn_worker.UvicornWorker` đã cài.

**Đánh giá:** Sync worker xử lý một request tại một thời điểm; worker class thay concurrency. Không mặc định chọn workers theo công thức CPU. [Docs](https://gunicorn.org/design/).

## Boundary validation và config

### Pydantic v2

**Công dụng và tình huống:** Model validation/serialization cho request/config/domain boundary. Dùng constrain quantity hoặc price.

**Ví dụ:** `Field(strict=True, ge=1, le=100)` trên int và `ConfigDict(extra="forbid")`.

**Đánh giá:** Default có coercion; chọn strict/unknown-field policy rõ. Validation schema không kiểm tra account có quyền mua. [Docs](https://docs.pydantic.dev/latest/concepts/models/).

### pydantic-settings

**Công dụng và tình huống:** Load config từ env/files/secrets có type và validate khi startup.

**Ví dụ:** Subclass `BaseSettings` có `database_url` và `timeout_seconds:float=3`; tạo instance một lần.

**Đánh giá:** Package riêng trong hệ v2. Không dump settings chứa secret ra log; env config không thay secret rotation. [Docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

## Database và migration

### SQLAlchemy 2

**Công dụng và tình huống:** SQL expression/ORM/session/transaction; dùng model CRUD hoặc query explicit.

**Ví dụ:** `await session.execute(text("SELECT id FROM products WHERE id=:id"), {"id":42})`.

**Đánh giá:** Async cần driver async; mỗi task đồng thời session riêng. Tránh implicit lazy I/O, review SQL và pool limit. [Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).

### Alembic

**Công dụng và tình huống:** Migration version schema cho SQLAlchemy, tách deploy schema khỏi startup app.

**Ví dụ:** `alembic revision --autogenerate -m add_status` tạo candidate; review rồi `alembic upgrade head`.

**Đánh giá:** Autogenerate không bảo đảm migration đúng; rename/backfill/DDL lock cần review và rollout stages. [Docs](https://alembic.sqlalchemy.org/en/latest/tutorial.html).

### Psycopg 3

**Công dụng và tình huống:** PostgreSQL driver sync/async cho SQL trực tiếp và transaction.

**Ví dụ:** `cursor.execute("select id from users where email=%s", (email,))` bind giá trị.

**Đánh giá:** Không format `%` vào SQL bằng Python; chọn pooling/config/transaction cleanup và wheel/system deps đúng. [Docs](https://www.psycopg.org/psycopg3/docs/).

### asyncpg

**Công dụng và tình huống:** PostgreSQL driver async, dùng trực tiếp hoặc bên dưới SQLAlchemy async.

**Ví dụ:** DSN SQLAlchemy `postgresql+asyncpg://...` chọn driver; API trực tiếp dùng `$1` params.

**Đánh giá:** Không dùng một connection cho nhiều query đồng thời; pool cần giới hạn và thời gian chờ. [Docs](https://magicstack.github.io/asyncpg/current/).

## HTTP, cache và background jobs

### HTTPX

**Công dụng và tình huống:** HTTP client sync/async có pooling, timeout và test transport. Dùng gọi scoring API từ backend.

**Ví dụ:** `await client.get(url)` rồi `response.raise_for_status()` và `response.json()`.

**Đánh giá:** Tái sử dụng AsyncClient theo worker/lifespan. Timeout read/connect/pool khác total budget; asyncio.timeout bổ sung tổng. [Docs](https://www.python-httpx.org/async/).

### redis-py

**Công dụng và tình huống:** Redis client sync/async cho cache TTL, counter và pub/sub.

**Ví dụ:** `await redis_client.set("profile:42", json, ex=60)` dùng asyncio client.

**Đánh giá:** Invalidate/fallback và memory policy là việc của app; pub/sub không tự là durable queue. [Docs](https://redis.readthedocs.io/en/stable/).

### Celery

**Công dụng và tình huống:** Task dispatch/worker/retry/schedule với broker, tách job dài khỏi HTTP.

**Ví dụ:** `export_report.delay(report_id)` enqueue job, trả job id để client poll trạng thái.

**Đánh giá:** Cần broker và worker riêng; result backend chỉ khi cần. Retry/ack không có exactly-once side effect, phải idempotent. [Docs](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html).

## Tests, tooling, observability và AI

### pytest

**Công dụng và tình huống:** Test runner với fixture/parametrize cho unit/integration và API tests.

**Ví dụ:** `@pytest.mark.parametrize("quantity", [0,101])` kiểm tra input bị từ chối.

**Đánh giá:** Test behavior và transaction thật khi cần; dependency mocks không kiểm tra driver/schema. [Docs](https://docs.pytest.org/en/stable/).

### Ruff

**Công dụng và tình huống:** Linter/formatter Python cho import, style và bug-prone patterns trong CI.

**Ví dụ:** `ruff check .` và `ruff format --check .` với rules được chọn.

**Đánh giá:** Không thay type checker, security review hay integration tests; autofix cần review. [Docs](https://docs.astral.sh/ruff/).

### uv

**Công dụng và tình huống:** Package/environment/project tool với lock/sync/run cho workflow Python.

**Ví dụ:** `uv add fastapi` rồi `uv sync --locked`; `uv run` chạy trong env project.

**Đánh giá:** Không phải Uvicorn; lock Python deps không tự khóa system/CUDA/model artifacts. [Docs](https://docs.astral.sh/uv/).

### OpenTelemetry Python

**Công dụng và tình huống:** Trace/metrics và instrumentation để nhìn API/DB/queue qua request context.

**Ví dụ:** Span `orders.create`, gắn model_version và trace downstream, export OTLP.

**Đánh giá:** Cần exporter/collector/backend; tránh labels user/prompt không giới hạn và thông tin riêng tư. [Docs](https://opentelemetry.io/docs/languages/python/).

### OpenAI Python SDK

**Công dụng và tình huống:** Client official sync/async gọi model APIs, tiện trong backend/data workflows.

**Ví dụ:** `await client.responses.create(model=os.environ["MODEL"], input="Explain HTTP")` với AsyncOpenAI.

**Đánh giá:** Cần key/model access; reuse client, bounded concurrency/cost và eval. Client không train model. [Docs](https://github.com/openai/openai-python).

## Recipe 1: API typed nhỏ

**Stack:** FastAPI + Pydantic v2 + Uvicorn + pytest + Ruff. Trong thư mục thử riêng, cài `fastapi==0.143.0 uvicorn==0.54.0 pydantic==2.14.0`, lưu `app.py`, chạy `python -m uvicorn app:app --host 127.0.0.1 --port 3102`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
app = FastAPI()
class OrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    productId: str = Field(min_length=1)
    quantity: int = Field(strict=True, ge=1, le=100)
class OrderOut(OrderIn):
    id: str
@app.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(order: OrderIn):
    return OrderOut(id="demo-1", **order.model_dump())
```

POST `{"productId":"book","quantity":2}` nhận `201`; quantity `0`, chuỗi `"2"` và extra field nhận `422` theo validation mặc định FastAPI. So với Node/Go recipe trả `400`, đây là khác contract framework, không khác mức an toàn. Id cố định chỉ minh họa. Input không có coercion quantity vì chọn strict.

## Recipe 2: CRUD và transaction

**Stack:** FastAPI + Pydantic + SQLAlchemy async + asyncpg + Alembic + PostgreSQL. Tạo engine/pool theo worker, session theo request/task, migrations chạy tách app. Dưới đây là fragment có table/DB_URL chuẩn bị trước; chưa có auth, query deadline hoặc operational error mapping.

```python
# Dependencies: FastAPI, Pydantic v2, SQLAlchemy 2, asyncpg, Uvicorn.
# DATABASE_URL=postgresql+asyncpg://...; existing products(id, name) table.
import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
engine = create_async_engine(os.environ["DATABASE_URL"],
    pool_size=5, max_overflow=0, pool_timeout=1)
sessions = async_sessionmaker(engine, expire_on_commit=False)
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await engine.dispose()
app = FastAPI(lifespan=lifespan)
async def get_session():
    async with sessions() as session:
        yield session
class ProductOut(BaseModel):
    id: int
    name: str
@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: Annotated[int, Path(ge=1)],
    session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(
        text("SELECT id, name FROM products WHERE id=:id"), {"id":product_id})
    row = result.mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)
```

Query bind parameter thay string concatenation. Read không commit; session context đóng và giải phóng connection. Với write dùng `async with session.begin()` để commit/rollback một unit nghiệp vụ. Không chia một AsyncSession cho các task trong `asyncio.gather`. Chọn pool size bằng tổng replicas × workers × pool (kể cả overflow/background), không chỉ traffic của một process. [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).

## Recipe 3: business app có backoffice

**Stack:** Django + ORM/migrations/auth/admin + DRF khi cần REST + PostgreSQL + Celery. Model/admin giúp giao diện quản trị nhanh; serializer và permissions cho API. Tối ưu select_related/prefetch_related để tránh N+1; transaction của nghiệp vụ viết riêng. ASGI không tự biến mọi middleware/ORM flow thành async phù hợp.

## Pool HTTP và total timeout

```python
# Separate illustrative lifespan, merge resource ownership into the real app's lifespan.
import asyncio
import httpx
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app):
    async with httpx.AsyncClient(
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        timeout=httpx.Timeout(3.0, connect=1.0, pool=1.0),
    ) as client:
        app.state.http = client
        yield
# Fragment inside an async route; request and trusted upstream_url already exist:
# async with asyncio.timeout(4.0):
#     response = await request.app.state.http.get(upstream_url)
#     response.raise_for_status()
#     payload = response.json()
```

Client lifetime theo worker để tái sử dụng connections. HTTPX timeout theo connect/read/write/pool; `asyncio.timeout` đặt tổng budget khi code hợp tác. Không tạo AsyncClient mới trong vòng lặp nóng, không để URL user nhập tự quyết định upstream mà chưa kiểm soát. Snippet trên là resource ownership riêng; merge vào một lifespan của app. [HTTPX limits](https://www.python-httpx.org/advanced/resource-limits/), [timeouts](https://www.python-httpx.org/advanced/timeouts/).

## Queue minh họa

```python
# tasks.py; install celery[redis]; CELERY_BROKER_URL points to a running broker.
import os
from celery import Celery
celery = Celery("reports", broker=os.environ["CELERY_BROKER_URL"])
@celery.task(name="reports.summarize")
def summarize(values: list[int]) -> dict[str, int]:
    return {"count":len(values), "total":sum(values)}
if __name__ == "__main__":
    job = summarize.delay([2,3,5])
    print(job.id)
```

Chạy `celery -A tasks:celery worker --loglevel=INFO` ở process khác với cùng broker, rồi `python tasks.py` enqueue. Worker tính count=3,total=10; publisher chỉ nhận job id. Cần result backend hoặc bảng trạng thái nếu API phải đọc kết quả. Production job nên gửi id nhỏ, lưu status/artifact và có retry/idempotency; queue không bảo đảm external side effect chỉ xảy ra một lần.

## Recipe 4: ML-backed API

**Stack:** FastAPI gateway + Pydantic + model worker hoặc vLLM/ONNX Runtime + artifact/tracking + metric/eval. Load model một lần, warmup rồi readiness; batch/concurrency/queue theo memory và latency mục tiêu. CPU/native/GPU inference có hành vi riêng; async route không bảo đảm inference nhường loop. Xem [data](python-data.vi.md), [AI/ML](python-ai-ml.vi.md) và [luồng server](../04-server-runtime.vi.md).
