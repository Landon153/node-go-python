# Go: stacks, libraries, and practical recipes

[README](../../README.en.md) · [VI](go-stacks.vi.md) · [EN](go-stacks.en.md)

Go often starts with the standard library and adds routers, drivers, and generation tools. Fragments below need imports and configured instances. Library choices affect organization and operations, beyond requests per second.

## HTTP and validation

### net/http

**Purpose and scenario:** Standard server/client for APIs that do not need a large framework.

**Example:** `http.NewServeMux()` plus `mux.HandleFunc("GET /health", handler)` on Go ≥1.22.

**Assessment:** Add middleware, validation, and error mapping yourself; configure server timeouts/body limits. [Docs](https://pkg.go.dev/net/http).

### chi

**Purpose and scenario:** A net/http-compatible router with groups/middleware for small and medium services.

**Example:** `r.Get("/users/{id}", handler)`; `chi.URLParam(r,"id")` reads a path parameter.

**Assessment:** Explicit composition without ORM/validation/DI; establish team conventions. [Docs](https://github.com/go-chi/chi).

### Gin

**Purpose and scenario:** REST framework with routing, binding, middleware, and its own context.

**Example:** `c.ShouldBindJSON(&input)` decodes/validates input using struct tags.

**Assessment:** Framework context differs from cancellation context; pass `c.Request.Context()` to I/O. [Docs](https://gin-gonic.com/en/docs/).

### Echo

**Purpose and scenario:** Routing/binding and central error handling for APIs using framework conventions.

**Example:** A `GET /users/:id` route reads `c.Param("id")`; a custom validator checks DTOs.

**Assessment:** Binding is not authorization; do not bind sensitive fields directly into DB entities. [Docs](https://echo.labstack.com/docs/).

### Fiber

**Purpose and scenario:** Express-inspired fasthttp framework with fluent route/middleware APIs.

**Example:** `app.Get("/health", ...)` returns JSON through a Fiber context.

**Assessment:** Not a net/http drop-in; check version, context lifetimes, and middleware integrations. [Docs](https://docs.gofiber.io/).

### validator

**Purpose and scenario:** Struct-tag validation with cross-field/custom rules for DTOs.

**Example:** `validate.Struct(input)` with `validate:"required,email"` checks email.

**Assessment:** Does not decode JSON or authorize; map field errors to a clear contract. [Docs](https://github.com/go-playground/validator).

## Databases and migrations

### pgx / pgxpool

**Purpose and scenario:** Native PostgreSQL driver with contexts/pooling for explicit SQL.

**Example:** `pool.QueryRow(ctx,"select name from users where id=$1",42).Scan(&name)`.

**Assessment:** Close rows/release connections; keep transactions on one connection and bound acquire/query time. [Docs](https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool).

### sqlc

**Purpose and scenario:** Generate typed Go functions from named SQL; teams own SQL with compile-time mappings.

**Example:** A `-- name: GetUser :one` query generates `queries.GetUser(ctx,id)`.

**Assessment:** Requires generation and synchronized schemas/queries; it is not a migration runner. [Docs](https://docs.sqlc.dev/en/stable/).

### GORM

**Purpose and scenario:** ORM models/associations/hooks for CRUD and entity operations.

**Example:** `db.WithContext(ctx).Where("email = ?", email).First(&user)` loads an entity.

**Assessment:** Inspect query counts, preloads, and zero-value updates; review migrations instead of blindly auto-migrating. [Docs](https://gorm.io/docs/).

### goose

**Purpose and scenario:** Versioned SQL/Go migrations for schema creation and evolution.

**Example:** A file with `-- +goose Up` creates a table; `goose postgres "$DB_URL" up` applies it.

**Assessment:** Backfills/DDL locks need planning; Down does not guarantee recovery of lost data. [Docs](https://github.com/pressly/goose).

## Jobs, caches, RPC, and CLIs

### go-redis

**Purpose and scenario:** Redis client for caching, counters, Lua/transactions when coordination is needed.

**Example:** `rdb.Set(ctx,"profile:42",json,time.Minute)` sets a TTL cache.

**Assessment:** Contexts/pools/retries do not replace consistency; design invalidation and fallback. [Docs](https://redis.uptrace.dev/).

### Asynq

**Purpose and scenario:** Redis task queue with worker concurrency/retries for email, exports, and thumbnails.

**Example:** Enqueue `asynq.NewTask("email:send", payload)` and process JSON in its handler.

**Assessment:** Requires Redis and separate workers; side effects must remain idempotent on retries. [Docs](https://github.com/hibiken/asynq).

### gRPC-Go

**Purpose and scenario:** Protobuf-generated typed RPC across services, with unary/streaming over HTTP/2.

**Example:** Define `GetUser` in proto, generate client/server, call with a context deadline.

**Assessment:** Does not solve contract evolution, auth, or browser access automatically; add a gateway when needed. [Docs](https://grpc.io/docs/languages/go/).

### Cobra

**Purpose and scenario:** Commands/subcommands/flags for service administration and developer CLIs.

**Example:** `cobra.Command{Use:"import", RunE:...}` implements a data-import command.

**Assessment:** Keep business logic outside commands for tests/reuse; do not log secrets from flags/env. [Docs](https://cobra.dev/).

## Tests, logs, and AI

### testing + httptest

**Purpose and scenario:** Standard tests and HTTP recorders/servers for handlers with deliberately real/fake dependencies.

**Example:** `httptest.NewRecorder()` plus `handler.ServeHTTP(rec,req)` then assert status/body.

**Assessment:** A recorder does not exercise networking/TLS or shutdown; use integration checks for those flows. [Docs](https://pkg.go.dev/net/http/httptest).

### Testify

**Purpose and scenario:** Assertions/mocks make Go tests easier to read for teams preferring helpers.

**Example:** `require.NoError(t,err)` stops a test when a precondition fails.

**Assessment:** Implementation-shaped mocks make fragile tests; prefer behavioral contracts. [Docs](https://github.com/stretchr/testify).

### slog

**Purpose and scenario:** Standard structured logging; requestId/orderId fields help diagnose failures.

**Example:** `slog.Info("created", "order_id", 42)` emits an attributed record.

**Assessment:** Choose JSON/text handlers and levels; avoid unbounded user IDs as metric labels. [Docs](https://pkg.go.dev/log/slog).

### OpenTelemetry Go

**Purpose and scenario:** Spans/metrics/context propagation across APIs, DBs, and queues.

**Example:** `ctx, span := tracer.Start(ctx,"orders.create")`; `defer span.End()`.

**Assessment:** Needs exporters/collectors/backends; sampling and exporter shutdown affect visibility. [Docs](https://opentelemetry.io/docs/languages/go/).

### OpenAI Go SDK

**Purpose and scenario:** Official SDK for model API calls from Go services; useful for gateways and AI-enabled backends.

**Example:** Pass a deadline-bearing context to a Responses call with configured model/credentials.

**Assessment:** An inference API client rather than a GPU-training framework; imports/APIs vary by major version. [Docs](https://github.com/openai/openai-go).

### Genkit Go

**Purpose and scenario:** Define structured AI flows/tools with model integrations in Go apps.

**Example:** A flow takes a question, retrieves, generates, and returns schema-defined output.

**Assessment:** Choose compatible plugins; the referenced guide requires Go ≥1.25. Check versions, evaluations, and tool authorization. [Docs](https://genkit.dev/docs/go/get-started/).

## Recipe 1: API with explicit SQL

**Stack:** net/http + chi + validator + pgxpool + sqlc + goose + slog + testing. Chi preserves net/http handlers; validator checks DTOs; sqlc generates mappings; goose versions schemas. pgx manages connections and contexts propagate cancellation through layers. A small service can use one Go module without a DI framework.

The runnable example uses manual validation to expose the boundary. In a separate scratch directory: `go mod init demo`, `go get github.com/go-chi/chi/v5@v5.3.2`, save `main.go`, run `go run .` (Go ≥1.23 for chi v5.3.2). No DB required.

```go
package main
import (
    "encoding/json"
    "io"
    "log"
    "net/http"
    "time"
    "github.com/go-chi/chi/v5"
)
type Order struct {
    ProductID string `json:"productId"`
    Quantity int `json:"quantity"`
}
func createOrder(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, 16*1024)
    defer r.Body.Close()
    dec := json.NewDecoder(r.Body)
    dec.DisallowUnknownFields()
    var input Order
    if err := dec.Decode(&input); err != nil {
        http.Error(w, "invalid JSON", http.StatusBadRequest); return
    }
    if err := dec.Decode(new(any)); err != io.EOF {
        http.Error(w, "one JSON value required", http.StatusBadRequest); return
    }
    if input.ProductID == "" || input.Quantity < 1 || input.Quantity > 100 {
        http.Error(w, "invalid order", http.StatusBadRequest); return
    }
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    if err := json.NewEncoder(w).Encode(map[string]any{
        "id": "demo-1", "productId": input.ProductID, "quantity": input.Quantity,
    }); err != nil { log.Printf("response write: %v", err) }
}
func main() {
    router := chi.NewRouter()
    router.Post("/orders", createOrder)
    server := &http.Server{Addr:"127.0.0.1:3101", Handler:router,
        ReadHeaderTimeout:5*time.Second, ReadTimeout:10*time.Second,
        WriteTimeout:10*time.Second, IdleTimeout:60*time.Second}
    log.Fatal(server.ListenAndServe())
}
```

POST `{"productId":"book","quantity":2}` receives `201`; unknown fields, quantity `0`, string `"2"`, and multiple JSON values are rejected. Errors are text for brevity; real applications need a consistent JSON error contract. The demo returns a fixed ID; add shutdown as in [chapter 5](../05-server-examples.en.md) before deployment.

## Recipe 2: ORM-backed CRUD

**Stack:** Gin or Echo + GORM + migration runner + PostgreSQL + integration tests. Separate request DTOs from entities; clients must not write `role`, `ownerId`, or `isPaid` merely because a struct has those fields. Use transactions for cross-table invariants and constraints against races. Keep raw SQL where analytics need explicit control.

## Recipe 3: gateway/worker

**Stack:** net/http/chi or gRPC + context + pgx + Redis/Asynq + OpenTelemetry. The gateway authenticates, validates, bounds concurrency, and calls Python inference/model APIs. Workers perform imports/CPU jobs with bounded queues. Cheap goroutines do not make downstream work cheap; semaphores/pools must reflect real capacity.

## Deadline propagation to the DB

```go
// pool is an initialized *pgxpool.Pool; this fragment belongs in a handler/service.
ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
defer cancel()
var name string
err := pool.QueryRow(ctx, "SELECT name FROM users WHERE id=$1", id).Scan(&name)
if errors.Is(err, pgx.ErrNoRows) {
    // Map to 404 only if this endpoint exposes absence to this caller.
} else if err != nil {
    // Log internal cause; return the endpoint's safe error contract.
}
```

Request cancellation cancels the child context; `defer cancel` releases timer resources. Distinguish absence, deadlines, dependency outages, and internal errors when mapping responses. Do not expose raw driver errors or SQL. Use `http.NewRequestWithContext` for outbound calls, reuse clients/transports, and select streaming-appropriate timeouts.

## Testing and operations

Use httptest for handlers, a test Postgres for queries/transactions, and the race detector for shared state. Measure CPU/RSS, runnable/waiting goroutines, pool acquisition, query latency, and queue depth. If the DB is the bottleneck, switching chi to Gin cannot fix it. Keep dependency versions and major APIs consistent in go.mod.
