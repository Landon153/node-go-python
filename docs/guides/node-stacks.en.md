# Node.js: stacks, libraries, and practical recipes

[README](../../README.en.md) · [VI](node-stacks.vi.md) · [EN](node-stacks.en.md)

These entries explain each tool, its scenario, and tradeoffs. Inline examples are fragments requiring matching imports/instances/configuration; they are not complete projects. Choices are workload assessments, not speed rankings.

## Web, UI, and APIs

### Express

**Purpose and scenario:** Small router/middleware core for REST or gradual legacy migration. You choose validation, logging, and error handling.

**Example:** `app.get("/health", (req, res) => res.json({ok:true}))` returns health JSON.

**Assessment:** Easy to start; ordering and conventions are team responsibilities, so standardize errors/auth. [Docs](https://expressjs.com/en/guide/routing.html).

### Fastify

**Purpose and scenario:** Plugin-oriented APIs, request/response JSON Schema, integrated logging; useful for explicit service contracts.

**Example:** A route schema with `required:["email"]` rejects a missing email before its handler.

**Assessment:** Ajv can coerce depending on configuration; inspect validated output. Zod needs integration or manual parsing. [Docs](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/).

### NestJS

**Purpose and scenario:** Modules/controllers/services and DI for backends with many domains and contributors; Express/Fastify adapters.

**Example:** A `@Get(":id")` route uses `ParseIntPipe`, a service reads the record, and a guard checks access.

**Assessment:** Clear structure adds decorators/DI and abstraction; often unnecessary for one tiny endpoint. [Docs](https://docs.nestjs.com/).

### React

**Purpose and scenario:** Build browser UI components and state; commonly paired with Node tooling/backends.

**Example:** `useState(0)` plus a button updates a counter and re-renders the view.

**Assessment:** Does not supply a router, DB, or backend by itself; distinguish browser bundles from server code. [Docs](https://react.dev/learn).

### Next.js

**Purpose and scenario:** React framework with routing, server rendering, and server-side endpoints for web apps.

**Example:** `app/api/health/route.ts` exports `GET()` returning `Response.json({ok:true})`.

**Assessment:** Caching/runtime/deployment behavior depends on version and host; endpoints are not automatically suitable for long jobs. [Docs](https://nextjs.org/docs).

## Validation and data

### Zod

**Purpose and scenario:** Runtime schemas with inferred TypeScript types for forms, env, and small/medium payloads.

**Example:** `z.object({age:z.number().int().min(18)}).safeParse({age:17})` returns `success:false`.

**Assessment:** TypeScript types disappear at runtime; Zod checks actual values. Choose coercion intentionally. [Docs](https://zod.dev/).

### Ajv

**Purpose and scenario:** Compile JSON Schema to validate payloads shared across languages/contracts.

**Example:** `const validate=ajv.compile(schema); validate(body)` returns a boolean and exposes `validate.errors`.

**Assessment:** Treat schemas as trusted configuration; compile once and reuse rather than per request. [Docs](https://ajv.js.org/guide/getting-started.html).

### node-postgres / pg

**Purpose and scenario:** PostgreSQL driver with SQL and pooling when the team wants explicit queries.

**Example:** `pool.query("select id from users where email=$1", [email])`; a transaction uses one client throughout.

**Assessment:** You own SQL/mapping/migrations; do not use independent `pool.query` calls for one transaction. [Docs](https://node-postgres.com/features/transactions).

### Prisma

**Purpose and scenario:** Schema and generated client for typed entity queries; useful for CRUD and onboarding.

**Example:** With a generated schema/client: `prisma.user.findUnique({where:{id:42}})` returns a user or null.

**Assessment:** Inspect SQL/query counts and indexes; types do not guarantee transactions or efficient queries. [Docs](https://www.prisma.io/docs/orm).

### Drizzle

**Purpose and scenario:** TypeScript schema and SQL-like queries with explicit projections/joins for lower-abstraction apps.

**Example:** `db.select({id:users.id}).from(users).where(eq(users.id,42))` selects only the ID.

**Assessment:** A raw expression type is a developer assertion; DB values are not automatically cast to match it. [Docs](https://orm.drizzle.team/docs/select).

## Cache, jobs, and communication

### node-redis

**Purpose and scenario:** Redis client for TTL caches, counters, and coordination; it does not replace the source-of-truth DB.

**Example:** `await client.set("profile:42", json, {EX:60})` caches for 60 seconds.

**Assessment:** Plan invalidation, memory bounds, and misses; stale cache should not determine access rights. [Docs](https://redis.io/docs/latest/develop/clients/nodejs/).

### BullMQ

**Purpose and scenario:** Redis queue moves email, exports, and image resizing out of HTTP requests with workers/retries/delays.

**Example:** `queue.add("export", {reportId:42}, {jobId:"report-42", attempts:3})`; a worker creates the file.

**Assessment:** Retries can repeat side effects; jobId deduplication lasts while the job is retained. Use idempotency keys/DB constraints. [Docs](https://docs.bullmq.io/).

### fetch / Undici

**Purpose and scenario:** HTTP client for external APIs; Node provides fetch, with additional client/pooling controls through Undici.

**Example:** `fetch(url,{signal:AbortSignal.timeout(2000)})`; check `response.ok` before reading JSON.

**Assessment:** HTTP 4xx/5xx do not automatically reject fetch; apply timeout/cancellation through the flow. [Docs](https://nodejs.org/api/globals.html#fetch).

### jose

**Purpose and scenario:** Sign/verify JWT/JWS, encrypt/decrypt JWE, and resolve JWKS for identity-provider integrations.

**Example:** `jwtVerify(token, key, {issuer, audience})` verifies signatures and configured claims.

**Assessment:** Decoding does not verify a token; authorization, key rotation, and algorithm choices still matter. [Docs](https://github.com/panva/jose).

## Testing, quality, and observability

### Vitest

**Purpose and scenario:** JS/TS unit/integration tests, mocks, and coverage, convenient in Vite ecosystems.

**Example:** `expect(total([2,3])).toBe(5)`; use a real test DB for transaction behavior when needed.

**Assessment:** Mocking all I/O can hide integration bugs; high coverage does not guarantee meaningful checks. [Docs](https://vitest.dev/guide/).

### Playwright

**Purpose and scenario:** Browser automation for login, forms, and user journeys across UI/API.

**Example:** `await page.getByRole("button",{name:"Save"}).click()` then assert persisted state.

**Assessment:** Use deterministic data and semantic locators; do not replace every unit test with slow UI checks. [Docs](https://playwright.dev/docs/intro).

### Pino

**Purpose and scenario:** Structured JSON logs with request context; Fastify uses a Pino-based logger.

**Example:** `logger.info({orderId:42, durationMs:18}, "order created")` produces searchable fields.

**Assessment:** Redact tokens/passwords; avoid default body/prompt logging and blocking transports. [Docs](https://getpino.io/).

### OpenTelemetry JS

**Purpose and scenario:** Traces/metrics correlate frontend/API/DB work; spans show where time is spent.

**Example:** Create an `orders.create` span, propagate trace context, export OTLP.

**Assessment:** The SDK is not a dashboard/storage backend; configure collection and bound cardinality. [Docs](https://opentelemetry.io/docs/languages/js/).

### TypeScript + ESLint

**Purpose and scenario:** Type checking and lint in CI for large codebases and module contracts.

**Example:** `tsc --noEmit` catches invalid argument types; ESLint enforces configured rules.

**Assessment:** Does not replace runtime validation; assertions/any can remove guarantees. [ESLint](https://eslint.org/docs/latest/). [Docs](https://www.typescriptlang.org/docs/handbook/intro.html).

## AI in Node

### AI SDK

**Purpose and scenario:** Provider abstractions, text streaming, and tool calls for web/JS applications.

**Example:** `streamText({model, prompt})` creates a text stream with a provider model instance.

**Assessment:** Requires a selected adapter/key/model/deployment; validate and authorize tools on the server. [Docs](https://ai-sdk.dev/docs/introduction).

### LangChain.js

**Purpose and scenario:** Compose models, retrievers, tools, and agent workflows in TypeScript.

**Example:** A retriever selects passages; an agent uses a catalog tool to answer product questions.

**Assessment:** Adds abstraction/dependencies; a direct SDK is often easier to debug for one API call. [Docs](https://docs.langchain.com/oss/javascript/langchain/overview).

### OpenAI Node SDK

**Purpose and scenario:** Official Node/TypeScript client for generation, structured output, and supported endpoints.

**Example:** `client.responses.create({model:process.env.MODEL, input:"Explain HTTP"})`; read `output_text`.

**Assessment:** Needs credentials and an accessible model; timeout/retry does not replace budgets, evaluation, or data controls. [Docs](https://github.com/openai/openai-node).

## Recipe 1: small API with explicit validation

**Stack:** Node + Fastify + Zod + pg + Pino + Vitest. Fastify handles HTTP/plugins, Zod validates boundaries, pg persists data, Pino provides structured logs, and Vitest checks domain/request behavior. This example parses Zod manually and chooses `400` in the handler.

In a separate scratch directory, run `npm init -y`, `npm install fastify@5.12.5 zod@4.6.5`, save this as `server.mjs`, and run `node server.mjs`. This snippet needs no DB.

```js
import Fastify from 'fastify';
import { z } from 'zod';
const app = Fastify({ logger: true, bodyLimit: 16 * 1024 });
const Order = z.object({
  productId: z.string().min(1),
  quantity: z.number().int().min(1).max(100),
}).strict();
app.post('/orders', async (request, reply) => {
  const parsed = Order.safeParse(request.body);
  if (!parsed.success) {
    return reply.code(400).send({ error: 'invalid_order' });
  }
  // Replace this demo result with a domain service / DB operation.
  return reply.code(201).send({ id: 'demo-1', ...parsed.data });
});
await app.listen({ host: '127.0.0.1', port: 3100 });
```

Send `curl -X POST http://127.0.0.1:3100/orders -H 'Content-Type: application/json' -d '{"productId":"book","quantity":2}'` to receive `201` with a demo ID. Quantity `0` returns `400`; string `"2"` is also rejected because this schema does not coerce. A fixed ID and in-memory result are not order persistence.

## Recipe 2: backend with many domains

**Stack:** NestJS + DTO/ValidationPipe + Prisma or Drizzle + PostgreSQL + BullMQ + OpenTelemetry. Separate orders/payments/identity modules: controllers handle HTTP, services handle domain logic, repositories handle DB access. Choose one primary ORM to avoid overlapping schema/migration layers. Add queues when work needs retries or background processing.

Nest DTOs can use class-validator with `ValidationPipe`; TypeScript decorators alone do not activate validation. Enable the pipe and choose transform/whitelist deliberately. [Nest validation](https://docs.nestjs.com/techniques/validation).

## Recipe 3: AI-enabled web application

**Stack:** Next.js + React + Zod + AI SDK or provider SDK + PostgreSQL + a vector store when retrieval is needed. UI consumes streams; the server keeps keys, authenticates tenants, and limits tools. For local models or training, call a separate Python/Go service rather than train inside a UI route.

## Transactions and jobs: common mistakes

```js
// pool is a configured pg.Pool; orders(id, amount) already exists.
const client = await pool.connect();
try {
  await client.query('BEGIN');
  const { rows } = await client.query(
    'INSERT INTO orders(amount) VALUES($1) RETURNING id', [1250]
  );
  await client.query('COMMIT');
  console.log(rows[0].id);
} catch (error) {
  await client.query('ROLLBACK');
  throw error;
} finally {
  client.release();
}
```

This DB fragment requires a configured schema/pool. Amount is an integer in the smallest currency unit; avoid floats for money. DB commit and job enqueue can diverge: use a transactional outbox when a job must exist after commit. Consumers still need idempotency because retry/delivery can repeat. Avoid holding DB transactions open while waiting for an AI model.

## Assessing the stack

Measure validation, DB round trips, event-loop lag, pool waiting, and memory with real payloads. Improve queries/indexes before switching frameworks. Choose Nest for team conventions, Fastify for explicit service contracts, and Express when migrating an existing app is expensive. React/Next address UI/rendering; they do not replace backend transaction and authorization design.
