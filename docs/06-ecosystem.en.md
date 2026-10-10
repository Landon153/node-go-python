# 06. Libraries and ecosystems

[README](../README.en.md) · [VI](./06-ecosystem.vi.md) · [EN](./06-ecosystem.en.md)

## How to read the assessments

This is a **representative shortlist of commonly encountered tools**, not a download-based popularity ranking. Every row links an official source; capabilities come from documentation, while selection advice is an engineering assessment. Categories distinguish frameworks, runtimes, drivers, ORMs, and package tools so comparisons stay at the correct layer.

Read by need: compact APIs → small routers; modular team backends → conventions/DI; relational SQL → choose driver/query builder/ORM; external input → runtime validation; AI → distinguish provider calls from model training/serving. Install what the application needs; this repository does not install the entire catalog.

## Node.js / JavaScript / TypeScript

| Tool / source | Category | Strengths and fit | Limitations and assessment |
| --- | --- | --- | --- |
| [Express](https://expressjs.com/) | Web / API | Small router/middleware layer with visible request flow; suits compact APIs or teams choosing their own architecture. | Validation, DI, and OpenAPI need additional choices. Do not mix Express 4 and 5 examples. |
| [Fastify](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/) | Web / API | Plugin encapsulation, schema validation, and serialization make API contracts explicit. | Schemas are trusted application code, not arbitrary user input. Database-dependent rules belong after structural validation. |
| [NestJS](https://docs.nestjs.com/) | BE architecture | Modules/controllers/providers, DI, guards, and pipes suit modular team backends. | More conventions than a small router. Uses Express by default or a Fastify adapter; still runs on Node. |
| [React](https://react.dev/) | Frontend | Components and state for browser UI, sharing JavaScript/TypeScript knowledge with backend code. | React is not an HTTP server. Choose framework/tooling, data fetching, and product-appropriate accessibility. |
| [Next.js](https://nextjs.org/docs) | Full-stack web | React routing/rendering, server/client components, and route handlers; useful for web apps with a BFF. | Understand caching and server/client boundaries. A standalone API service may be simpler with a backend framework. |
| [Zod](https://zod.dev/) | Validation | Code-first schemas with TypeScript inference for requests, forms, and tool inputs. | TypeScript types do not validate at runtime. Make coercion/defaults explicit; browser schemas do not replace server checks. |
| [Ajv](https://ajv.js.org/) | Validation | JSON Schema supports interoperable contracts and API specifications. | Dialects/options matter; coercion/default/removal may mutate data. Schema compilation is not a sandbox. |
| [Prisma](https://www.prisma.io/docs) | Database / ORM | Declarative schemas, generated typed clients, and migrations provide accessible relational CRUD. | Adds generation steps and schema conventions. Inspect queries, transactions, and complex access rather than assuming automatic optimization. |
| [Drizzle](https://orm.drizzle.team/docs/overview) | Database / ORM | TypeScript schemas and SQL-oriented query construction suit teams wanting visible SQL. | Types do not replace database constraints/indexes. Drivers and migrations still need configuration and review. |
| [node-postgres / pg](https://node-postgres.com/) | Database driver | Direct SQL, parameterized queries, and PostgreSQL pooling. | Own mapping/migrations. A transaction must use one checked-out client, not unrelated pool.query calls. |
| [Vitest](https://vitest.dev/guide/) | Testing | Unit/integration tests, mocks, coverage, and watch mode suit Vite/TypeScript projects. | Simulated browser environments do not establish real browser behavior. Test public behavior and important boundaries. |
| [Playwright](https://playwright.dev/docs/intro) | E2E | Real browsers, multiple engines, and traces verify UI flows. | Browser binaries, fixtures, and isolation increase CI cost. Focus on important flows to keep suites manageable. |
| [Pino](https://github.com/pinojs/pino) | Logging | Structured JSON logging with framework integrations. | Redaction, transports, and retention need separate design; avoid secrets or sensitive request bodies. |
| [AI SDK](https://ai-sdk.dev/docs/introduction) | AI application | TypeScript text, structured output, tools, and streaming connect chat UI and backend code. | Provider features differ. Timeouts, budgets, evaluation, and tool authorization remain necessary. |
| [LangChain.js](https://docs.langchain.com/oss/javascript/langchain/overview) | AI orchestration | Model/tool integrations and agents, with LangGraph execution capabilities. | Adds abstractions and packages. A direct provider SDK can be easier to debug for a single call. |
| [OpenAI Node SDK](https://github.com/openai/openai-node) | AI provider SDK | Official JavaScript/TypeScript client with typed APIs and streaming. | Provider-specific; keep keys server-side. Configure retries/cancellation/timeouts around request budgets. |

## Go

| Tool / source | Category | Strengths and fit | Limitations and assessment |
| --- | --- | --- | --- |
| [net/http](https://pkg.go.dev/net/http) | Web / standard library | HTTP client/server, routing, request contexts, and shutdown; a useful Go-server starting point. | No ORM/DI/business validation. Configure timeouts/limits and reuse clients/transports. |
| [chi](https://github.com/go-chi/chi) | Web / router | Lightweight routing with standard net/http middleware interfaces. | The team chooses validation, database access, dependency wiring, and API docs. |
| [Gin](https://gin-gonic.com/en/docs/) | Web / API | Routing, middleware, binding, and validation support practical REST APIs. | Framework-specific contexts create coupling; binding does not replace authorization or business rules. |
| [Echo](https://echo.labstack.com/guide/quickstart/) | Web / API | Routing, middleware, binding, and centralized error handling suit APIs. | Keep domain logic independent of framework contexts for testing and migration. |
| [Fiber](https://docs.gofiber.io/) | Web / API | Express-inspired API on fasthttp with routing and middleware. | v3 adapts net/http handlers but still uses fasthttp. Check compatibility and request-buffer lifetimes before retaining data. |
| [go-playground/validator](https://github.com/go-playground/validator) | Validation | Struct tags, nested fields, and custom rules validate typed payloads. | Complex reflection/tag rules can be opaque; use explicit business checks. Review required-nested-struct options. |
| [pgx](https://github.com/jackc/pgx) | Database driver | PostgreSQL toolkit with pooling, native features, and database/sql interoperability. | PostgreSQL-specific; the application still owns SQL, mapping, transactions, and migrations. |
| [sqlc](https://docs.sqlc.dev/en/latest/) | SQL code generation | Generates typed query methods from SQL, reducing manual scanning/mapping. | A generator, not a runtime ORM or migration runner. Review supported dialects and generated code. |
| [GORM](https://gorm.io/docs/) | Database / ORM | CRUD, associations, hooks, and transactions suit business apps. | Inspect implicit queries and association loading. AutoMigrate is not a reviewed production migration strategy. |
| [testing + httptest](https://pkg.go.dev/net/http/httptest) | Testing / standard library | Standard test runner plus HTTP recorders/servers minimize handler-test dependencies. | Recorders do not simulate every network behavior; use real integration tests at relevant boundaries. |
| [Testify](https://github.com/stretchr/testify) | Testing | Assertions, requirements, mocks, and suites improve readability on standard testing. | Avoid mocking implementation details; standard testing may suffice for small suites. |
| [log/slog](https://pkg.go.dev/log/slog) | Logging / standard library | Standard-library structured logs, attributes, and handlers. | Redaction, routing, retention, and trace correlation require separate design. |
| [OpenTelemetry Go](https://opentelemetry.io/docs/languages/go/) | Observability | Traces/metrics for distributed systems with interoperable export. | Stability differs by signal/component; exporters/backend operation are separate from instrumentation. |
| [OpenAI Go SDK](https://github.com/openai/openai-go) | AI provider SDK | Official typed requests, contexts, and streaming suit Go AI gateways. | Major module paths/toolchain requirements can change; pin compatible releases. Not a tensor-training framework. |
| [Genkit Go](https://genkit.dev/docs/go/get-started/) | AI orchestration | AI flows, typed inputs/outputs, plugins, and tracing. | Check Go-specific plugin/deployment coverage; language implementations do not necessarily share features/status. |

## Python

| Tool / source | Category | Strengths and fit | Limitations and assessment |
| --- | --- | --- | --- |
| [FastAPI](https://fastapi.tiangolo.com/) | Web / API | Type hints, Pydantic, DI, OpenAPI, and interactive docs suit typed APIs. | Needs an ASGI server; async endpoints must not perform blocking I/O or heavy CPU work directly on the loop. |
| [Django](https://docs.djangoproject.com/en/stable/) | Full-stack web | ORM, migrations, admin, auth, forms/templates, and conventions support business web apps. | Broader than a microframework. Async is component-specific; understand middleware, ORM, and deployment interfaces. |
| [Flask](https://flask.palletsprojects.com/en/stable/) | Web / WSGI | Compact routing/templates with extensions suit small apps and explicit composition. | Validation/ORM/OpenAPI require additions. Async views remain within WSGI worker behavior. |
| [Starlette](https://starlette.dev/) | Web / ASGI | Routing, middleware, WebSockets, responses, and lifespan form FastAPI's underlying web layer. | Lower-level than FastAPI; typed body validation and automatic OpenAPI are not its primary contract. |
| [Uvicorn](https://uvicorn.dev/) | ASGI server | Event-loop HTTP serving, worker processes, and FastAPI/Starlette integration. | A server, not a framework. Reload/workers are exclusive; resource limits and deployment settings need configuration. |
| [Gunicorn](https://gunicorn.org/) | HTTP / process manager | UNIX master/worker serving for WSGI or ASGI through a suitable worker package. | Concurrency depends on worker class; sync WSGI does not run ASGI automatically. Not native Windows serving. |
| [Pydantic v2](https://pydantic.dev/docs/validation/latest/) | Validation | Type-driven validation/serialization, JSON Schema, strict/lax modes, and a Rust core. | Lax parsing may coerce; use strict rules when required. v2 model_dump/field_validator differs from v1 APIs. |
| [SQLAlchemy](https://docs.sqlalchemy.org/en/20/intro.html) | Database / ORM | SQL Core plus ORM, transactions, pooling, and sync/async integrations. | Learn sessions/identity maps/lazy loading. Do not share one session across concurrent tasks; migrations need separate tooling. |
| [Psycopg 3](https://www.psycopg.org/psycopg3/docs/) | Database driver | Direct PostgreSQL access with sync/async APIs and native features. | Not an ORM; own SQL/mapping/transactions/pooling. Distinguish packages/examples from psycopg2. |
| [pytest](https://docs.pytest.org/en/stable/) | Testing | Fixtures, parametrization, and concise assertions for unit/integration tests. | Plugins/fixture lifetimes can hide complexity; make isolation and external services intentional. |
| [Ruff](https://docs.astral.sh/ruff/) | Lint / format | Python linting/formatting with configurable rules and fixes. | Does not replace type checking or runtime tests. Review fixes that can affect semantics. |
| [uv](https://docs.astral.sh/uv/) | Package tooling | Project/dependency/environment management, lockfiles, and interpreters. | Not Uvicorn. Learn lock workflows and verify reproducibility on target platforms. |
| [Celery](https://docs.celeryq.dev/en/stable/) | Job queue | Distributed tasks and scheduling move long work outside HTTP requests. | Needs broker/workers and failure policies; design idempotency for repeated delivery/retries. |
| [NumPy](https://numpy.org/doc/stable/) | Numerical computing | Multidimensional arrays, vectorization, and linear algebra underpin scientific Python. | Dtype/shape/views/copies affect results and memory. Neither a web framework nor a distributed processing engine. |
| [pandas](https://pandas.pydata.org/docs/) | Data processing | DataFrames, joins, aggregation, and I/O support tabular data processing. | Plan memory; avoid per-row loops when vectorization fits. Define schemas and missing-value behavior. |
| [scikit-learn](https://scikit-learn.org/stable/) | Classical ML | Preprocessing, pipelines, model selection, classification/regression/clustering. | Avoid data leakage and training-set evaluation. Not the usual framework for training large neural LLMs. |
| [PyTorch](https://docs.pytorch.org/docs/stable/index.html) | Deep learning | Tensors, autograd, neural networks, and accelerators support training/inference. | Design hardware, memory, and batching. Stable/experimental APIs coexist; the framework does not establish model quality. |
| [Transformers](https://huggingface.co/docs/transformers/index) | Pretrained models | Model definitions, tokenizers/preprocessors, pipelines, and generation/training for multiple modalities. | Check per-model licenses, trust settings, and RAM/VRAM. Convenient pipelines are not automatically tuned production serving. |
| [vLLM](https://docs.vllm.ai/en/latest/) | LLM inference serving | Continuous batching, KV caches, streaming, parallelism, and compatible HTTP APIs. | Support depends on models/hardware/APIs. Needs admission control/budgets; not a universal training framework. |
| [LangChain Python](https://docs.langchain.com/oss/python/langchain/overview) | AI orchestration | Provider interfaces, tools, and agents with LangGraph multi-step execution. | Orchestration does not ensure output quality or safe tools. Direct SDKs can suffice for simple workflows. |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | AI provider SDK | Official sync/async clients, streaming, and typed responses. | A provider API client, not a local neural runtime. Choose an async client for async server I/O. |

## Surrounding backend needs

| Need | Node.js | Go | Python | Selection criteria |
| --- | --- | --- | --- | --- |
| Outbound HTTP | [fetch](https://nodejs.org/api/globals.html#fetch) | [net/http](https://pkg.go.dev/net/http) | [HTTPX](https://www.python-httpx.org/) | Reuse clients/pools, set total timeouts/cancellation, and match sync/async to the server. |
| Redis/cache | [node-redis](https://redis.io/docs/latest/develop/clients/nodejs/) | [go-redis](https://redis.io/docs/latest/develop/clients/go/) | [redis-py](https://redis.io/docs/latest/develop/clients/redis-py/) | TTLs, invalidation, pools, and failure policies; caches do not replace database truth. |
| Job queues | [BullMQ](https://docs.bullmq.io/) | [Asynq](https://github.com/hibiken/asynq) | [Celery](https://docs.celeryq.dev/en/stable/) | Brokers, retries, idempotency, visibility, and dead letters; queues do not inherently guarantee exactly-once execution. |
| SQL migrations | [Knex migrations](https://knexjs.org/guide/migrations.html) | [golang-migrate](https://github.com/golang-migrate/migrate) | [Alembic](https://alembic.sqlalchemy.org/en/latest/) | Versioned changes and database-appropriate rollback/roll-forward; avoid ad hoc startup schema changes. |
| Observability | [OpenTelemetry JS](https://opentelemetry.io/docs/languages/js/) | [OpenTelemetry Go](https://opentelemetry.io/docs/languages/go/) | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) | Trace propagation, metric cardinality, sampling, sensitive data, and per-component stability. |
| Authentication | [Passport](https://www.passportjs.org/) or OIDC integration | [go-oidc](https://github.com/coreos/go-oidc) | [Authlib](https://docs.authlib.org/) / Django auth | Identity verification differs from business authorization; choose browser/API flows and verify issuer/audience. |
| Types/lint/format | [TypeScript](https://www.typescriptlang.org/docs/), [ESLint](https://eslint.org/), [Prettier](https://prettier.io/) | gofmt, go vet, [Staticcheck](https://staticcheck.dev/) | [mypy](https://mypy.readthedocs.io/), Ruff | Do not replace tests/runtime validation; rules should help find real errors. |

## Validation library examples

**TypeScript + Zod** (illustrative snippet, install Zod separately):

```typescript
import { z } from 'zod';
const User = z.object({ name: z.string().min(1), age: z.number().int().min(0) });
const user = User.parse({ name: 'Ada', age: 28 });
```

**Go**: decode into a struct and validate the domain with code or a struct-tag validator. Required fields may need to distinguish missing values from zero values.

```go
type User struct { Name string `json:"name"`; Age *int `json:"age"` }
func validate(u User) error {
    if u.Name == "" || u.Age == nil || *u.Age < 0 { return errors.New("invalid user") }
    return nil
}
```

**Python + Pydantic v2** (illustrative snippet, install Pydantic v2 separately):

```python
from pydantic import BaseModel, ConfigDict, Field
class User(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
user = User.model_validate({"name": "Ada", "age": 28})
print(user.model_dump())
```

These are not fully equivalent schemas: extra fields, Unicode, coercion, and missing/null policies need explicit definitions for a shared contract. Structural validation still needs authorization and business rules afterward. OpenAPI/JSON Schema and contract tests reduce drift across public services.
