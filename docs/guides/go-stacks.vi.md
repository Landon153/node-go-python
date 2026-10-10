# Go: stack, thư viện và recipe thực tế

[README](../../README.vi.md) · [VI](go-stacks.vi.md) · [EN](go-stacks.en.md)

Go thường bắt đầu từ standard library rồi bổ sung router, driver và công cụ generate. Các fragment dưới đây cần import và instance đã cấu hình. Lựa chọn thư viện phản ánh cách tổ chức code và vận hành, không chỉ số request/giây.

## HTTP và validation

### net/http

**Công dụng và tình huống:** Server/client chuẩn, phù hợp API không cần framework lớn.

**Ví dụ:** `http.NewServeMux()` + `mux.HandleFunc("GET /health", handler)` ở Go ≥1.22.

**Đánh giá:** Tự thêm middleware, validation và error mapping; cấu hình server timeout/body limit. [Docs](https://pkg.go.dev/net/http).

### chi

**Công dụng và tình huống:** Router tương thích net/http với route group và middleware cho service vừa/nhỏ.

**Ví dụ:** `r.Get("/users/{id}", handler)`; `chi.URLParam(r,"id")` lấy path parameter.

**Đánh giá:** Composition rõ, không cung cấp ORM/validation/DI; team cần convention của riêng mình. [Docs](https://github.com/go-chi/chi).

### Gin

**Công dụng và tình huống:** Framework routing, binding, middleware với context riêng cho REST.

**Ví dụ:** `c.ShouldBindJSON(&input)` decode/validate input theo struct tag.

**Đánh giá:** Context framework khác context cancellation; truyền `c.Request.Context()` xuống I/O. [Docs](https://gin-gonic.com/en/docs/).

### Echo

**Công dụng và tình huống:** Routing/binding và error handler tập trung cho API dùng convention của framework.

**Ví dụ:** Route `GET /users/:id` lấy `c.Param("id")`; custom validator kiểm tra DTO.

**Đánh giá:** Bind không đồng nghĩa authorization; không bind thẳng field nhạy cảm vào entity DB. [Docs](https://echo.labstack.com/docs/).

### Fiber

**Công dụng và tình huống:** Framework kiểu Express trên fasthttp, route/middleware cho team thích API fluent.

**Ví dụ:** `app.Get("/health", ...)` trả JSON từ Fiber context.

**Đánh giá:** Không phải drop-in net/http; kiểm tra version/context lifetime và integration của middleware. [Docs](https://docs.gofiber.io/).

### validator

**Công dụng và tình huống:** Validation struct theo tag, cross-field/custom rule cho DTO.

**Ví dụ:** `validate.Struct(input)` với tag `validate:"required,email"` kiểm tra email.

**Đánh giá:** Không decode JSON hay xác minh quyền; map lỗi field thành contract rõ. [Docs](https://github.com/go-playground/validator).

## Database và migrations

### pgx / pgxpool

**Công dụng và tình huống:** Driver PostgreSQL native, context và pooling cho SQL trực tiếp.

**Ví dụ:** `pool.QueryRow(ctx,"select name from users where id=$1",42).Scan(&name)`.

**Đánh giá:** Đóng rows/release connection; transaction cùng connection, có timeout cho acquire/query. [Docs](https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool).

### sqlc

**Công dụng và tình huống:** Generate hàm Go typed từ SQL có tên; team viết SQL và nhận mapping compile-time.

**Ví dụ:** `-- name: GetUser :one` trên query → `queries.GetUser(ctx,id)`.

**Đánh giá:** Cần generation trong workflow, schema/query đồng bộ; không phải migration runner. [Docs](https://docs.sqlc.dev/en/stable/).

### GORM

**Công dụng và tình huống:** ORM model/association/hook cho CRUD và thao tác entity.

**Ví dụ:** `db.WithContext(ctx).Where("email = ?", email).First(&user)` lấy entity.

**Đánh giá:** Kiểm tra query count, preload và zero-value update; dùng migration review thay auto migration tùy tiện. [Docs](https://gorm.io/docs/).

### goose

**Công dụng và tình huống:** Version SQL/Go migration để tạo và thay đổi schema có lịch sử.

**Ví dụ:** File có `-- +goose Up` tạo bảng; `goose postgres "$DB_URL" up` áp dụng.

**Đánh giá:** Backfill/DDL lock cần kế hoạch riêng; Down không bảo đảm khôi phục data đã mất. [Docs](https://github.com/pressly/goose).

## Jobs, cache, RPC và CLI

### go-redis

**Công dụng và tình huống:** Client Redis cho cache, counter, Lua/transaction khi cần coordination.

**Ví dụ:** `rdb.Set(ctx,"profile:42",json,time.Minute)` đặt cache TTL.

**Đánh giá:** Context/pool/retry không thay consistency; thiết kế cache invalidation và fallback. [Docs](https://redis.uptrace.dev/).

### Asynq

**Công dụng và tình huống:** Task queue Redis với worker concurrency/retry cho email, export, thumbnail.

**Ví dụ:** `asynq.NewTask("email:send", payload)` enqueue, handler xử lý payload JSON.

**Đánh giá:** Cần Redis và worker độc lập; side effect phải idempotent khi job retry. [Docs](https://github.com/hibiken/asynq).

### gRPC-Go

**Công dụng và tình huống:** RPC typed từ protobuf giữa services, unary/streaming trên HTTP/2.

**Ví dụ:** Định nghĩa `GetUser` trong proto → generate client/server → gọi với context deadline.

**Đánh giá:** Không tự giải quyết version contract, auth hay browser access; thêm gateway khi cần. [Docs](https://grpc.io/docs/languages/go/).

### Cobra

**Công dụng và tình huống:** Command/subcommand/flag cho CLI vận hành service hoặc công cụ developer.

**Ví dụ:** `cobra.Command{Use:"import", RunE:...}` làm lệnh import dữ liệu.

**Đánh giá:** Giữ business logic ngoài command để test/reuse; không log secrets từ flags/env. [Docs](https://cobra.dev/).

## Tests, logs và AI

### testing + httptest

**Công dụng và tình huống:** Test chuẩn và HTTP recorder/server để kiểm tra handler cùng dependency thật/giả có chủ đích.

**Ví dụ:** `httptest.NewRecorder()` + `handler.ServeHTTP(rec,req)` rồi kiểm tra status/body.

**Đánh giá:** Recorder không đo network/TLS hoặc shutdown; cần integration riêng cho các flow đó. [Docs](https://pkg.go.dev/net/http/httptest).

### Testify

**Công dụng và tình huống:** Assertion và mock giúp test Go dễ đọc cho team thích helper.

**Ví dụ:** `require.NoError(t,err)` dừng test tại precondition lỗi.

**Đánh giá:** Mock quá sát implementation tạo test mong manh; ưu tiên contract hành vi. [Docs](https://github.com/stretchr/testify).

### slog

**Công dụng và tình huống:** Structured logging chuẩn; field requestId/orderId dùng để tìm lỗi.

**Ví dụ:** `slog.Info("created", "order_id", 42)` gửi record có thuộc tính.

**Đánh giá:** Chọn handler JSON/text và mức log; không dùng userId vô hạn làm label metric. [Docs](https://pkg.go.dev/log/slog).

### OpenTelemetry Go

**Công dụng và tình huống:** Span/metric/context propagation cho API, DB, queue để theo dõi request qua services.

**Ví dụ:** `ctx, span := tracer.Start(ctx,"orders.create")`; `defer span.End()`.

**Đánh giá:** Cần exporter/collector/backend; sampling và shutdown exporter ảnh hưởng dữ liệu quan sát. [Docs](https://opentelemetry.io/docs/languages/go/).

### OpenAI Go SDK

**Công dụng và tình huống:** SDK official để Go service gọi model API; tốt cho gateway hoặc backend tích hợp AI.

**Ví dụ:** Truyền context có deadline vào lời gọi Responses, model/key từ cấu hình.

**Đánh giá:** Đây là client inference API, không phải framework training GPU. Imports/API đổi theo major version. [Docs](https://github.com/openai/openai-go).

### Genkit Go

**Công dụng và tình huống:** Định nghĩa AI flow/tool có cấu trúc và integration model cho Go app.

**Ví dụ:** Flow nhận câu hỏi → retrieval → generation → trả output được định nghĩa schema.

**Đánh giá:** Cần plugin phù hợp; guide hiện tại yêu cầu Go ≥1.25. Kiểm tra version, eval và phân quyền tool. [Docs](https://genkit.dev/docs/go/get-started/).

## Recipe 1: API viết SQL rõ

**Stack:** net/http + chi + validator + pgxpool + sqlc + goose + slog + testing. Chi giữ handler dạng net/http; validator kiểm tra DTO; sqlc sinh mapping từ SQL; goose version schema. pgx chịu kết nối; context truyền cancellation xuyên layers. Một module Go là đủ cho service nhỏ, chưa cần DI framework.

Đoạn runnable dưới đây dùng validation thủ công để nhìn rõ boundary. Trong thư mục thử riêng: `go mod init demo`, `go get github.com/go-chi/chi/v5@v5.3.2`, lưu `main.go`, chạy `go run .` (Go ≥1.23 cho chi v5.3.2). Không cần DB.

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

POST payload `{"productId":"book","quantity":2}` nhận `201`; unknown field, quantity `0`, chuỗi `"2"`, hoặc hai JSON value bị từ chối. Error dùng text để code ngắn; ứng dụng thật cần error JSON thống nhất. Demo chỉ tạo id cố định; thêm shutdown như [chương 5](../05-server-examples.vi.md) trước triển khai.

## Recipe 2: CRUD với ORM

**Stack:** Gin hoặc Echo + GORM + migration runner + PostgreSQL + test integration. DTO request tách entity; không cho client ghi `role`, `ownerId`, `isPaid` chỉ vì struct có field đó. Dùng transaction cho invariants liên quan nhiều bảng và constraint để chống race. Giữ SQL raw khi query analytics cần kiểm soát rõ.

## Recipe 3: gateway/worker

**Stack:** net/http/chi hoặc gRPC + context + pgx + Redis/Asynq + OpenTelemetry. Gateway auth, validate, giới hạn concurrency và gọi Python inference/model API. Worker làm import/CPU work có hàng đợi giới hạn. Goroutine nhẹ không đồng nghĩa chi phí downstream nhẹ; semaphore và pool phải phản ánh sức chứa thật.

## Ví dụ deadline tới DB

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

Request hủy sẽ hủy context con; `defer cancel` giải phóng timer. Phân biệt not found, deadline, dependency outage và lỗi nội bộ khi map response. Không trả nguyên driver error hoặc SQL cho client. Dùng context cho HTTP outbound qua `http.NewRequestWithContext`, tái sử dụng client/transport, đặt timeout phù hợp với streaming.

## Kiểm thử và vận hành

Test handler bằng httptest, test query/transaction với Postgres test, chạy race detector cho state dùng chung. Đo CPU/RSS, goroutine đang chạy/chờ, pool acquire, query latency và queue depth. Nếu database là bottleneck, đổi chi sang Gin không giải quyết được. Giữ phiên bản dependency và API major nhất quán trong go.mod.
