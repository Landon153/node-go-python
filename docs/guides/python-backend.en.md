# Python: backends, validation, databases, and workers

[README](../../README.en.md) · [VI](python-backend.vi.md) · [EN](python-backend.en.md)

Python web stacks include full frameworks such as Django and APIs/toolkits such as FastAPI/Starlette or Flask. Select by product/deployment; AI/data libraries do not supply HTTP/auth/transactions automatically. Inline calls are fragments needing instances/imports/configuration; recipes have separate prerequisites below.

## Web frameworks and servers

### FastAPI

**Purpose and scenario:** ASGI API framework with routing, dependency injection, Pydantic validation, and OpenAPI for typed REST/prediction APIs.

**Example:** `@app.post("/orders", response_model=OrderOut)` checks model-defined input/output.

**Assessment:** Needs an ASGI server; async routes do not automatically offload CPU work. Framework/Pydantic integration validates, ordinary type hints do not. [Docs](https://fastapi.tiangolo.com/).

### Starlette

**Purpose and scenario:** ASGI toolkit for routing/middleware/responses/WebSockets/lifespan, underlying FastAPI; useful for small apps with custom contracts.

**Example:** `Route("/health", health)` with a handler returning `JSONResponse({"ok":True})`.

**Assessment:** Does not supply FastAPI-style validation/OpenAPI automatically; check lifecycle/middleware design. [Docs](https://starlette.dev/).

### Django

**Purpose and scenario:** Full web framework with ORM, migrations, auth, admin, and templates for business apps needing a backoffice.

**Example:** Define a Product model, migrate, and register it in admin to manage a catalog.

**Assessment:** Strong conventions require ORM/query/async knowledge; admin is not public-API authorization. [Docs](https://docs.djangoproject.com/en/stable/).

### Django REST Framework

**Purpose and scenario:** Serializers/viewsets/routers/permissions for Django REST APIs leveraging ORM/auth.

**Example:** A `ModelSerializer` selects id/name; `ReadOnlyModelViewSet` provides read endpoints.

**Assessment:** Scope querysets/permissions by tenant and watch N+1 queries; serializer fields do not enforce row access. [Docs](https://www.django-rest-framework.org/).

### Flask

**Purpose and scenario:** Small WSGI framework for APIs/services/dashboards and existing synchronous apps.

**Example:** `@app.get("/health")` returns `{"ok":True}`.

**Assessment:** Choose extensions; async views still occupy WSGI workers. Use an appropriate production server rather than the dev server. [Docs](https://flask.palletsprojects.com/en/stable/).

### Uvicorn

**Purpose and scenario:** ASGI server accepting sockets/parsing HTTP/running loops for FastAPI/Starlette.

**Example:** `python -m uvicorn app:app --host 127.0.0.1 --port 3102` serves a defined app.

**Assessment:** Workers are separate processes duplicating memory/models/pools; do not combine reload with workers. [Docs](https://uvicorn.dev/settings/).

### Gunicorn

**Purpose and scenario:** UNIX process manager/server for WSGI or compatible ASGI workers.

**Example:** `gunicorn app:app -w 2` for WSGI; ASGI uses installed `-k uvicorn_worker.UvicornWorker`.

**Assessment:** Sync workers handle one request at a time; concurrency depends on worker class. Do not choose worker counts from a CPU formula alone. [Docs](https://gunicorn.org/design/).

## Boundary validation and configuration

### Pydantic v2

**Purpose and scenario:** Model validation/serialization for requests/config/domain boundaries, such as constrained quantity/price.

**Example:** An int with `Field(strict=True, ge=1, le=100)` and `ConfigDict(extra="forbid")`.

**Assessment:** Defaults can coerce; choose strict/unknown-field policies. Schema validation does not establish account purchasing rights. [Docs](https://docs.pydantic.dev/latest/concepts/models/).

### pydantic-settings

**Purpose and scenario:** Load typed, validated configuration from env/files/secrets at startup.

**Example:** A `BaseSettings` subclass defines `database_url` and `timeout_seconds:float=3`; instantiate once.

**Assessment:** A separate package in v2; do not dump secret-bearing settings to logs. Env configuration is not secret rotation. [Docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

## Databases and migrations

### SQLAlchemy 2

**Purpose and scenario:** SQL expressions/ORM/sessions/transactions for CRUD models or explicit queries.

**Example:** `await session.execute(text("SELECT id FROM products WHERE id=:id"), {"id":42})`.

**Assessment:** Async needs an async driver and separate sessions per concurrent task. Avoid implicit lazy I/O; inspect SQL and pool limits. [Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).

### Alembic

**Purpose and scenario:** Versioned SQLAlchemy schema migrations, separate from application startup.

**Example:** `alembic revision --autogenerate -m add_status` creates a candidate; review then `alembic upgrade head`.

**Assessment:** Autogeneration does not guarantee correctness; review renames/backfills/DDL locks and rollout stages. [Docs](https://alembic.sqlalchemy.org/en/latest/tutorial.html).

### Psycopg 3

**Purpose and scenario:** Sync/async PostgreSQL driver for explicit SQL and transactions.

**Example:** `cursor.execute("select id from users where email=%s", (email,))` binds values.

**Assessment:** Do not interpolate SQL using Python `%`; select pooling, transaction cleanup, and compatible wheel/system dependencies. [Docs](https://www.psycopg.org/psycopg3/docs/).

### asyncpg

**Purpose and scenario:** Async PostgreSQL driver, directly or underneath SQLAlchemy async.

**Example:** SQLAlchemy DSN `postgresql+asyncpg://...` selects the driver; direct APIs use `$1` parameters.

**Assessment:** Do not run concurrent queries through one connection; bound pool capacity/waiting. [Docs](https://magicstack.github.io/asyncpg/current/).

## HTTP, caches, and background jobs

### HTTPX

**Purpose and scenario:** Sync/async HTTP client with pools/timeouts/test transports for outbound scoring APIs.

**Example:** `await client.get(url)`, then `response.raise_for_status()` and `response.json()`.

**Assessment:** Reuse AsyncClient per worker/lifespan. Read/connect/pool timeouts differ from a total budget; use asyncio.timeout for the latter. [Docs](https://www.python-httpx.org/async/).

### redis-py

**Purpose and scenario:** Sync/async Redis client for TTL caches, counters, and pub/sub.

**Example:** `await redis_client.set("profile:42", json, ex=60)` using an asyncio client.

**Assessment:** Applications own invalidation/fallback/memory policies; pub/sub is not automatically a durable queue. [Docs](https://redis.readthedocs.io/en/stable/).

### Celery

**Purpose and scenario:** Broker-backed task dispatch/workers/retries/schedules move long jobs out of HTTP.

**Example:** `export_report.delay(report_id)` queues a job and returns an ID for status polling.

**Assessment:** Needs a broker/separate workers; configure a result backend when needed. Retry/ack does not ensure exactly-once side effects; make jobs idempotent. [Docs](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html).

## Tests, tooling, observability, and AI

### pytest

**Purpose and scenario:** Test runner with fixtures/parametrization for unit/integration/API checks.

**Example:** `@pytest.mark.parametrize("quantity", [0,101])` checks rejected input.

**Assessment:** Check behavior and real transactions when needed; mocks do not exercise drivers/schemas. [Docs](https://docs.pytest.org/en/stable/).

### Ruff

**Purpose and scenario:** Python linter/formatter for imports/style/bug-prone patterns in CI.

**Example:** `ruff check .` and `ruff format --check .` with selected rules.

**Assessment:** Does not replace type checking, security review, or integration tests; review autofixes. [Docs](https://docs.astral.sh/ruff/).

### uv

**Purpose and scenario:** Package/environment/project tool with lock/sync/run for Python workflows.

**Example:** `uv add fastapi`, then `uv sync --locked`; `uv run` uses the project environment.

**Assessment:** Distinct from Uvicorn; Python dependency locks do not lock system/CUDA/model artifacts. [Docs](https://docs.astral.sh/uv/).

### OpenTelemetry Python

**Purpose and scenario:** Tracing/metrics/instrumentation to correlate API/DB/queue work.

**Example:** An `orders.create` span carries model_version and propagates downstream, exporting OTLP.

**Assessment:** Needs exporters/collectors/backends; avoid unbounded user/prompt labels and private data. [Docs](https://opentelemetry.io/docs/languages/python/).

### OpenAI Python SDK

**Purpose and scenario:** Official sync/async model API client for backend/data workflows.

**Example:** `await client.responses.create(model=os.environ["MODEL"], input="Explain HTTP")` using AsyncOpenAI.

**Assessment:** Requires credentials/model access; reuse clients and bound concurrency/cost with evaluations. It does not train models. [Docs](https://github.com/openai/openai-python).

## Recipe 1: small typed API

**Stack:** FastAPI + Pydantic v2 + Uvicorn + pytest + Ruff. In a separate directory, install `fastapi==0.143.0 uvicorn==0.54.0 pydantic==2.14.0`, save `app.py`, run `python -m uvicorn app:app --host 127.0.0.1 --port 3102`.

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

POST `{"productId":"book","quantity":2}` receives `201`; quantity `0`, string `"2"`, and extra fields receive FastAPI's default `422`. Node/Go recipes choose `400`; this is a framework contract difference, not a safety difference. The fixed ID is illustrative. Strict quantity avoids coercion.

## Recipe 2: CRUD and transactions

**Stack:** FastAPI + Pydantic + SQLAlchemy async + asyncpg + Alembic + PostgreSQL. Create engine/pools per worker, sessions per request/task, and run migrations separately. This fragment needs the table/DB_URL prepared; auth, query deadlines, and operational error mapping are omitted.

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

Bind query values rather than concatenate SQL. Reads need no commit; the session context closes/releases connections. Writes can use `async with session.begin()` for a transactional unit. Do not share one AsyncSession across `asyncio.gather` tasks. Count total replicas × workers × pools, including overflow/background workers. [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).

## Recipe 3: business application with a backoffice

**Stack:** Django + ORM/migrations/auth/admin + DRF for REST when needed + PostgreSQL + Celery. Models/admin accelerate backoffice work; serializers/permissions handle APIs. Use select_related/prefetch_related against N+1 queries and explicit business transactions. ASGI does not automatically make every middleware/ORM flow appropriate for async execution.

## HTTP pooling and total timeouts

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

Keep the client per worker to reuse connections. HTTPX separates connect/read/write/pool timeouts; `asyncio.timeout` imposes a cooperative total budget. Avoid recreating AsyncClient in a hot loop or letting unchecked user URLs choose upstreams. Merge this standalone resource example into one application lifespan. [HTTPX limits](https://www.python-httpx.org/advanced/resource-limits/), [timeouts](https://www.python-httpx.org/advanced/timeouts/).

## Queue illustration

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

Run `celery -A tasks:celery worker --loglevel=INFO` in a separate process with the same broker, then `python tasks.py` to enqueue. The worker computes count=3,total=10; the publisher receives only a job ID. Configure a result backend or status table when the API needs results. Production jobs should pass small IDs, persist status/artifacts, and use retry/idempotency policies; queues do not guarantee exactly-once external side effects.

## Recipe 4: ML-backed API

**Stack:** FastAPI gateway + Pydantic + a model worker or vLLM/ONNX Runtime + artifacts/tracking + metrics/evaluation. Load once, warm up before readiness, and bound batching/concurrency/queues by memory/latency targets. CPU/native/GPU inference behaves differently; an async route does not guarantee loop yielding. See [data](python-data.en.md), [AI/ML](python-ai-ml.en.md), and [server flow](../04-server-runtime.en.md).
