# 08. Stack selection, measurement and migration

[README](../README.en.md) · [VI](./08-choosing-a-stack.vi.md) · [EN](./08-choosing-a-stack.en.md)

## Choose by workload

These are starting points for evaluation, not absolute rankings.

| Need | Starting point | Why | What to check |
| --- | --- | --- | --- |
| React web/BFF with a strong TS team | Node/TypeScript with a scope-appropriate framework | Shared language knowledge and UI/API ecosystem | Client/server boundaries, validation, caching, loop CPU work |
| I/O integration API with compact deployment | Go net/http/chi or Gin/Echo | Explicit standard library, binaries, and concurrency model | CPU quotas, DB pools, shared state, GC, shutdown |
| API near data/ML pipelines | Python FastAPI + Uvicorn | Direct model/data ecosystem access | Sync/async clients, CPU offloading, RAM/VRAM, workers |
| Business app needing admin/auth/ORM | Django, or NestJS for TS teams | Conventions and integrated features reduce repeated decisions | Framework fit, custom flows, transactions, migrations |
| Model training/research | Python + PyTorch/TensorFlow/JAX as appropriate | Data/model/accelerator tools | Reproducibility, datasets, hardware, licenses, evaluation |
| Application CPU is a measured bottleneck | Profile, then evaluate Go/workers/processes | Decisions target a specific bottleneck | End-to-end latency, serialization, algorithms, operation |

Do not migrate a backend solely because of an HTTP microbenchmark. If most time goes to the database or external APIs, changing languages may offer little benefit while adding migration cost. Learning/debugging an unfamiliar language is part of stack cost.

## Example stacks for discussion

| Stack | Components | Assessment |
| --- | --- | --- |
| Compact Node API | Fastify + JSON Schema/Ajv + pg + Pino + Vitest | Explicit contracts/direct SQL; domain organization and migrations remain choices. |
| Node team backend | NestJS + validation pipes + Prisma/Drizzle + integration tests | Conventions/DI help modular teams; inspect abstractions and queries. |
| Go SQL service | net/http/chi + pgx/sqlc + slog + testing/httptest | Reviewable SQL with fewer runtime layers; choose migrations/domain validation separately. |
| Python typed API | FastAPI + Pydantic v2 + SQLAlchemy/Psycopg + pytest + Uvicorn | Connects APIs/data easily; align sync/async drivers and session lifecycle. |
| Python business web | Django + ORM/migrations/admin/auth + integration tests | Integrated features; balance conventions against custom flows. |
| AI product | Familiar API language + provider SDK or inference service | Add orchestration when workflows justify it; measure quality/cost alongside latency. |

Component capability sources: [catalog](./06-ecosystem.en.md), [AI platforms](./07-ai-platforms.en.md). These stacks are workload-based engineering proposals; the runnable demos integrate no databases or AI providers.

## Measure fairly

1. Fix contracts, payloads, HTTP versions, keep-alive, TLS/proxies, and dependency I/O.
2. Record OS/CPU/RAM, container quotas, runtime/framework versions, workers/processes, and DB pools.
3. Warm up and run long enough; place the load generator outside the server where possible.
4. Exercise multiple concurrency levels, normal traffic, and overload; repeat to inspect variability.
5. Report throughput, p50/p95/p99 latency, errors/timeouts, CPU, RSS, queue depth, and DB wait.
6. For AI, add time-to-first-token, tokens/sec, output length, models/hardware, batching, and quality.

Do not compare one Node worker, eight Python workers, and multicore Go and attribute all differences to syntax. Comparing real product configurations is valid, but state resource allocations and costs. `/wait` models a timer, not networking/database performance; `/sum` is a tiny payload rather than a whole application. This repository's checks establish basic contracts and publish no performance measurements.

## Deliberate blocking experiment

In a local branch, add the same bounded CPU task to all three handlers. Send `/health` concurrently and observe latency. Node's event loop and Python's asyncio loop remain occupied during non-yielding computation; Go can use available CPUs but still competes for resources. Then try worker/process pools or a separate compute service and include dispatch/serialization overhead.

Do not substitute synchronous sleep for CPU benchmarking: sleeping blocks/holds a thread without equivalent CPU pressure. Paid external APIs need an explicit benchmark budget. Bound inputs and execution time to keep the experiment manageable.

## Moving from Node to Go/Python

| Node pattern | Go adaptation | Python adaptation |
| --- | --- | --- |
| TypeScript DTO | Structs + explicit optional/null rules + validation | Hints/BaseModel + explicit strict/coercion rules |
| Promise.all | Goroutines + error/cancellation/bounds | gather/TaskGroup + semaphore/error policy |
| Throw/error middleware | Return errors and map statuses at boundaries | Exception types and boundary handlers |
| Request-local state | Context values or explicit parameters | Framework scopes/dependencies/contextvars |
| npm package | Start with standard library, then needed modules | Standard library or PyPI + environments/locks |
| In-memory singleton | Synchronize shared goroutine state | Separate process copies; async interleaving can still race logically |

Port **behavior**, not individual lines. Establish contract tests for validation, missing/null, numeric precision, datetime/timezones, pagination, transactions, and error shapes before replacing a service. Keep business logic outside HTTP contexts and migrate a rollback-friendly boundary first.

## Extension exercises

- Add `POST /users` in all three stacks with identical missing/null/extra-field policies.
- Add PostgreSQL parameterized queries and verify rollback/timeouts.
- Cancel a waiting client and check that upstream work stopped; add ASGI disconnect handling.
- Add a bounded worker queue and measure overload queue delay.
- Build an AI question dataset and compare direct SDK integration with orchestration on real tasks.

These exercises are not implemented or covered by the existing checks. Contributions should update both language editions and place new sources near the associated claims.

## From recipes to operable systems

| Product | Starting point | Reason and next step |
| --- | --- | --- |
| Business web with backoffice | Django/DRF or Nest + UI | Auth/admin conventions or DI/modules; check permissions/transactions |
| Small contract-driven API | Fastify/Zod/pg, chi/pgx/sqlc, FastAPI/Pydantic/SQLAlchemy | Choose by team/integrations; all need schema/error/query checks |
| Tabular ML experiments | pandas/Pandera/sklearn/MLflow | Simple baseline and correct splits/evaluation before DL/distribution |
| Local Parquet analytics | Polars lazy or DuckDB + PyArrow | Aggregate before materialization; measure RAM/scans/query plans |
| AI web/RAG | Node UI/API or Go gateway + Python/model server | Separate auth/retrieval from inference capacity where needed |

Promote recipes by verifying required behavior: invalid inputs rejected, cross-user rows/documents inaccessible, concurrent transactions preserving invariants, consistent dependency-timeout errors, retries avoiding duplicate side effects, bounded request/job shutdown, versioned models with rollback. Demos cover a subset rather than every integration.

Change packages for measured reasons or reduced team costs: query bottlenecks need queries/indexes, model memory needs batching/quantization/topology, maintenance problems may need conventions. Node/Go/Python migrations must preserve status/error, null/coercion/date/large-integer, and cancellation contracts rather than only translate syntax.
