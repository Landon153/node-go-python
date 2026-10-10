# 04. Server hoạt động như thế nào

[README](../README.vi.md) · [VI](./04-server-runtime.vi.md) · [EN](./04-server-runtime.en.md)

## Request đi qua những lớp nào?

```mermaid
flowchart LR
    C[Client] --> P[Proxy / load balancer]
    P --> N[Node: socket → event loop → handler]
    P --> G[Go: socket → netpoll / goroutine → handler]
    P --> Y[Python: server → WSGI hoặc ASGI → app]
    N --> D[Database / external API / queue]
    G --> D
    Y --> D
```

Proxy nhận TLS/routing; server nhận và parse HTTP; middleware xử lý auth/validation; handler gọi domain logic và I/O; serializer tạo response. Chỗ chờ database và chỗ tính toán CPU cần được phân biệt: thay runtime sẽ không tự sửa query chậm, thiếu index hoặc giới hạn connection pool.

## Node: V8, event loop và libuv

Trong một worker thông thường, callback JavaScript chạy trên một thread event loop. Process vẫn có thread khác. Network I/O thường dùng cơ chế readiness của OS; libuv worker pool dùng cho một số API như filesystem, DNS lookup, crypto và compression. Không phải mọi `await` đều chạy trên worker pool. [Node blocking guide](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop).

Khi chờ I/O async, callback có thể nhường loop để xử lý request khác. Vòng lặp CPU, JSON lớn hoặc API sync giữ loop bận và làm request khác tăng latency. Thêm `async` trước hàm không offload phần tính toán. Dùng pool `worker_threads` cho CPU JavaScript; child process/replica dùng để tăng số worker và cô lập lỗi. Worker thread JS và native pool libuv là hai cơ chế khác nhau. [Worker threads](https://nodejs.org/api/worker_threads.html).

## Go: goroutine, scheduler và net/http

Code handler có thể trông như blocking, nhưng network wait có thể park goroutine để scheduler chạy goroutine khác. Runtime ghép goroutine lên OS thread; CPU work có thể chạy song song. `GOMAXPROCS` giới hạn mức thực thi Go đồng thời, không giới hạn tổng số goroutine hay OS thread. Goroutine không miễn phí: cần giới hạn job, queue và connection. [Runtime](https://pkg.go.dev/runtime#GOMAXPROCS).

`net/http` nhận connection và tạo service goroutine; không nên học thuộc “mỗi request đúng một goroutine” cho mọi giao thức. Các handler có thể truy cập dữ liệu dùng chung đồng thời; bảo vệ mutable map bằng mutex hoặc thiết kế ownership. Chạy race detector khi có shared state. [net/http](https://pkg.go.dev/net/http#Server.Serve), [race detector](https://go.dev/doc/articles/race_detector).

Go 1.25+ có mặc định GOMAXPROCS nhận biết CPU affinity/cgroup quota. Hành vi phụ thuộc phiên bản khai báo trong `go.mod` và GODEBUG; mốc ngôn ngữ ≤1.24 có thể giữ mặc định cũ. Repo này khai báo 1.22 để thể hiện mức code yêu cầu, nên không giả định tự nhận quota như module mới. Đặt `GOMAXPROCS` tường minh cũng ảnh hưởng tự cập nhật. Kiểm tra cấu hình thực tế trong container. [Container-aware GOMAXPROCS](https://go.dev/blog/container-aware-gomaxprocs).

## Python: “core” nào thường dùng?

**CPython** là implementation đang được bàn ở đây. Với build GIL mặc định, trong một interpreter chỉ một thread thực thi Python bytecode tại một thời điểm. Thread vẫn hữu ích cho I/O; thư viện native có thể giải phóng GIL. CPU thuần Python thường dùng process pool hoặc service compute riêng. Không suy ra rằng cả hệ thống Python chỉ dùng được một CPU. [threading](https://docs.python.org/3.14/library/threading.html).

Python có build free-threaded tùy chọn từ 3.13; không có nghĩa mọi Python đã bỏ GIL. Extension không hỗ trợ có thể bật GIL trở lại. Cần kiểm tra compatibility của dependency và đo thực tế. Một event loop `asyncio` vẫn chạy từng task trên thread loop; free-threading không tự biến coroutine CPU thành chạy song song. [Free threading](https://docs.python.org/3.14/howto/free-threading-python.html), [asyncio](https://docs.python.org/3.14/library/asyncio-task.html).

| Thành phần | Vai trò | Nhầm lẫn cần tránh |
| --- | --- | --- |
| CPython | Chạy Python bytecode, quản lý object/memory | Không phải web framework |
| asyncio | Coroutine, task, event loop, async I/O | Không tự chuyển hàm sync sang thread |
| WSGI | Interface đồng bộ giữa server và app | Không quy định duy nhất mô hình thread/process |
| ASGI | Interface async `scope, receive, send`, HTTP/WebSocket/lifespan | Là interface, không phải server |
| Uvicorn | ASGI server; socket, HTTP parsing, loop, worker manager | Không phải FastAPI và không phải uv package manager |
| Gunicorn | UNIX master/worker server; worker class quyết định concurrency | Worker WSGI sync không tự chạy ASGI |
| Starlette / FastAPI | Routing, middleware, response; FastAPI thêm validation/OpenAPI | `async def` vẫn có thể block nếu gọi I/O sync |
| Django / Flask | Framework web; deployment interface tùy framework | Flask async view không biến WSGI thành ASGI |

Nguồn interface: [WSGI / PEP 3333](https://peps.python.org/pep-3333/), [ASGI](https://asgi.readthedocs.io/en/latest/specs/main.html).

Uvicorn `--workers N` tạo nhiều process; mỗi process có loop và memory riêng. `--reload` và `--workers` không dùng cùng nhau. `uvicorn.workers` đã deprecated; nếu cần Gunicorn + ASGI, dùng package `uvicorn-worker` riêng. Gunicorn sync worker mặc định xử lý một request tại một thời điểm trong một process; gthread và async worker thay đổi cách thực thi. [Uvicorn deployment](https://uvicorn.dev/deployment/), [Gunicorn design](https://gunicorn.org/design/).

FastAPI đưa route/dependency khai báo `def` qua thread pool; helper sync gọi trực tiếp bên trong `async def` không tự được offload. Flask async view vẫn giữ WSGI worker trong suốt request. Django hỗ trợ ASGI/async nhưng sync middleware và transaction cần xem xét; ví dụ Django 5.2 chưa hỗ trợ transaction async. [FastAPI concurrency](https://fastapi.tiangolo.com/async/), [Flask async](https://flask.palletsprojects.com/en/stable/async-await/), [Django 5.2 async](https://docs.djangoproject.com/en/5.2/topics/async/).

## So sánh vận hành

| Tình huống | Node.js | Go | Python |
| --- | --- | --- | --- |
| Nhiều request chờ API | Async client, giới hạn concurrency | Goroutine + context + pool | ASGI + async client, semaphore |
| CPU work trong handler | Có thể chặn loop của worker | Có thể chạy song song nhưng tranh CPU với request khác | Chặn async loop; GIL ảnh hưởng thread CPU thuần Python |
| Scale trên nhiều CPU | Nhiều process hoặc worker thread pool | Một process có thể dùng nhiều CPU | Nhiều process; native/free-threaded tùy workload |
| State trong memory | Replica/process không tự chia sẻ | Goroutine cùng process có thể chia sẻ | Process không tự chia sẻ; thread/task có thể chia sẻ |
| Hủy công việc | Signal cần API hợp tác | Context cần được truyền xuống | Task cancellation cần await/API hợp tác |
| Shutdown | Ngừng nhận và drain request; deadline | Server.Shutdown + context; xử lý connection hijacked riêng | Lifespan + worker shutdown; drain queue tùy thiết kế |

Mọi stack đều cần timeout outbound, pool limit, queue bound, graceful shutdown và metric. Backpressure là quyết định nhận/hoãn/từ chối công việc khi tài nguyên hết; không chỉ là thêm `async` hoặc thêm worker. Với retry, tính cả idempotency và tổng deadline. Đếm số connection database trên toàn bộ replica × worker × pool trước khi tăng worker.

## Theo dõi một request từ đầu đến cuối

Ví dụ dưới đây là `POST /orders`: người dùng gửi JSON, server kiểm tra quyền, ghi PostgreSQL rồi trả `201`. Sơ đồ là một kiến trúc có thể triển khai; thứ tự middleware cụ thể còn tùy framework và cấu hình. Proxy có thể buffer body/response; client nhận header không đồng nghĩa đã nhận toàn bộ body.

```mermaid
flowchart TD
    Client[Client sends method URL headers body] --> Edge[Proxy: TLS routing body limits]
    Edge --> Server[Server reads socket and parses HTTP]
    Server --> Route[Match route and middleware]
    Route --> Auth[Authenticate and authorize]
    Auth --> Valid[Validate input]
    Valid --> Handler[Handler and domain service]
    Handler --> Pool[Acquire bounded DB or API capacity]
    Pool --> IO[Wait for DB or external API]
    IO --> Result[Map domain result]
    Result --> Encode[Serialize status headers body]
    Encode --> Write[Write response respecting backpressure]
    Write --> Client
    Auth -->|denied| Error[Map error to HTTP response]
    Valid -->|invalid| Error
    Pool -->|deadline or overloaded| Error
    IO -->|failure| Error
    Error --> Encode
```

### Node.js + Fastify: `await` nhường event loop ở đâu?

```mermaid
sequenceDiagram
    participant C as Client
    participant H as Node HTTP and Fastify
    participant L as JS event loop
    participant D as DB pool and PostgreSQL
    C->>H: POST /orders with JSON
    H->>L: Route matched, onRequest / preParsing
    L->>L: Parse body, preValidation, schema validation
    L->>L: preHandler, handler starts
    L->>D: Acquire client, send parameterized query
    Note over L,D: Promise pending: loop can execute request B
    D-->>L: Query result, schedule continuation
    L->>L: Map result, preSerialization, serialize, onSend
    L->>H: Status + response bytes
    H-->>C: HTTP response
    L->>L: onResponse after response is sent
```

Fastify tìm route trước các hook `onRequest` và `preParsing`; body chưa được parse trong `onRequest`. Auth đọc header có thể chạy sớm ở đây; auth cần body phải chạy sau parse. Validation mặc định dựa trên JSON Schema/Ajv, không tự dùng Zod. Route này giữ một Promise trong lúc DB xử lý, nhưng không giữ event loop để đợi DB. Khi kết quả tới, phần tiếp theo của handler lại chạy JavaScript trên loop. [Fastify lifecycle](https://fastify.dev/docs/latest/Reference/Lifecycle/).

Nếu chạy `JSON.stringify` trên dữ liệu rất lớn hoặc tính toán nặng trước/sau `await`, request khác vẫn có thể bị chậm. DB pool hết chỗ cũng tạo thời gian chờ; tăng số Node worker có thể làm tổng số connection tăng và DB quá tải. Đặt giới hạn body, thời gian lấy connection và tổng deadline; đo event-loop lag cùng thời gian query.

Với NestJS, thứ tự thông thường là **middleware → guards → interceptors chiều vào → pipes → controller/service → interceptors chiều ra**. Exception filter xử lý exception chưa được bắt, không phải bước luôn chạy của một request thành công. Guard làm quyền truy cập; pipe biến đổi/validate input. [Nest lifecycle](https://docs.nestjs.com/faq/request-lifecycle).

### Go + net/http/chi: code tuần tự, nhiều goroutine cùng tiến triển

```mermaid
sequenceDiagram
    participant C as Client
    participant H as net/http and router
    participant G as Handler goroutine
    participant S as Go scheduler
    participant D as pgx pool and PostgreSQL
    C->>H: POST /orders
    H->>G: Middleware then handler
    G->>G: Decode, validate, authorize
    G->>D: Acquire(ctx), Query(ctx, ...)
    G->>S: Park while waiting for network or pool
    Note over S: Other runnable goroutines can execute
    D-->>S: Socket ready or context cancelled
    S->>G: Resume goroutine
    G->>G: Handle result/error, encode JSON
    G->>H: WriteHeader + Write
    H-->>C: HTTP response
```

`Query(ctx, ...)` nhìn như lời gọi chặn, nhưng network wait thường park goroutine để scheduler chạy công việc khác. Acquire pool cũng có thể chờ và cần deadline. `context` phải được truyền từ `r.Context()` xuống DB và HTTP client; tạo `context.Background()` trong service sẽ cắt đường hủy request. Driver vẫn cần hợp tác để việc hủy có tác dụng. [Context](https://pkg.go.dev/context), [pgxpool](https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool).

Sơ đồ thể hiện goroutine xử lý handler, không khẳng định mỗi request tạo đúng một goroutine. HTTP/1 keep-alive tái sử dụng connection; HTTP/2 có nhiều stream trên cùng connection. Nếu handler giữ map dùng chung, `await` không liên quan: phải bảo vệ map bằng mutex hoặc thiết kế ownership. CPU work có thể chạy song song nhưng vẫn tranh CPU với request khác.

### Python + Uvicorn/FastAPI: ASGI task, thread pool và DB async

```mermaid
sequenceDiagram
    participant C as Client
    participant U as Uvicorn HTTP protocol
    participant A as ASGI task and FastAPI
    participant T as Thread pool
    participant D as Async DB or HTTP client
    C->>U: POST /orders
    U->>A: app(scope, receive, send)
    A->>A: Middleware, route, dependencies, Pydantic validation
    alt async def route with async client
        A->>D: await query / request
        Note over A,D: Task suspends, loop can run another task
        D-->>A: I/O ready, task resumes
    else def route or sync dependency
        A->>T: Framework schedules synchronous callable
        T-->>A: Return result
    end
    A->>A: Response model and serialization
    A->>U: send(http.response.start)
    A->>U: send(http.response.body)
    U-->>C: HTTP response bytes
```

Uvicorn tạo HTTP scope và giao `receive/send` cho ASGI app. FastAPI/Starlette xử lý routing, dependency và response; chi tiết thứ tự phụ thuộc vị trí middleware/dependency. `async def` nên gọi async driver như `asyncpg` qua SQLAlchemy async hoặc `httpx.AsyncClient`. `requests.get()`, `time.sleep()` hay helper đồng bộ được gọi trực tiếp trong `async def` sẽ giữ loop. Chỉ route/dependency `def` được framework tự đưa vào thread pool; helper gọi trực tiếp không được tự đổi cách chạy. [FastAPI concurrency](https://fastapi.tiangolo.com/async/), [ASGI HTTP](https://asgi.readthedocs.io/en/latest/specs/www.html).

Thread pool có giới hạn; không phải cứ chuyển sang `def` là tăng vô hạn throughput. SQLAlchemy `AsyncSession` chứa state của transaction: mỗi task đồng thời dùng session riêng. Tạo model ML nặng một lần khi startup/lifespan thay vì mỗi request; nhiều process sẽ có bản model/memory riêng. [SQLAlchemy async sessions](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).

### Python + Gunicorn sync/WSGI: worker bị chiếm ở đâu?

```mermaid
flowchart LR
    P[Proxy] --> W[Sync worker accepts connections]
    M[Gunicorn master] -. manages lifecycle .-> W
    W --> E[HTTP parsed into WSGI environ]
    E --> A[Flask or Django sync app]
    A --> D[Blocking DB call occupies this worker]
    D --> R[start_response and body iterable]
    R --> C[Client response]
```

Master quản lý vòng đời process; mũi tên qua master biểu diễn quản lý, không phải master chạy application handler. Một sync worker xử lý một request tại một thời điểm. Khi chờ DB blocking, worker đó chưa phục vụ request kế tiếp; worker khác vẫn có thể làm việc. Với `gthread`, có nhiều thread trong worker; với ASGI cần server/worker tương thích. Không suy ra Flask, Django hoặc Python luôn tuần tự từ cấu hình sync này. [Gunicorn design](https://gunicorn.org/design/), [WSGI](https://peps.python.org/pep-3333/).

## Cùng một tình huống: A chờ 100 ms, B tính tổng

| Thời điểm | Node async | Go network wait | Python ASGI async | Gunicorn sync, 1 worker |
| --- | --- | --- | --- | --- |
| A bắt đầu chờ I/O | Handler nhường loop | Goroutine park | Task nhường loop | Worker đang bị chiếm |
| B đến | Loop có thể xử lý B | Goroutine khác có thể chạy B | Loop có thể xử lý B | B chờ worker rảnh |
| I/O của A xong | Continuation được lập lịch | Goroutine runnable trở lại | Task được lập lịch | Worker tiếp tục A |

Đây là mô hình giải thích concurrency, không phải phép đo latency. Nếu A chạy vòng lặp CPU thay cho I/O, Node/Python async sẽ giữ loop; Go tranh ngân sách CPU. Nếu B cũng cần DB nhưng pool hết chỗ, cả ba đều có thể phải đợi.

## Timeout, disconnect, backpressure và shutdown

1. **Deadline:** xác định tổng thời gian request, rồi chia ngân sách cho pool acquire/query/API; timeout của từng bước không tự tạo giới hạn tổng.
2. **Disconnect:** nhận tín hiệu client đóng kết nối và truyền hủy xuống lời gọi có hỗ trợ. Response đã gửi không thể “thu hồi”; query đã commit không tự rollback vì client bỏ đi.
3. **Backpressure:** giới hạn công việc đang chạy và chờ, trả lỗi quá tải phù hợp hoặc đưa job dài sang queue. Khi stream, phải chờ khả năng ghi của transport; không đẩy vô hạn chunk vào bộ nhớ.
4. **Shutdown:** bỏ readiness/stop admission, drain request đang chạy với deadline, đóng pool/consumer. Job queue cần quy tắc retry/idempotency riêng.

Các metric cần gắn theo cùng một request ID: thời gian ở proxy, route, pool acquire, DB/API, serialize; số request đang chạy, pool waiters, event-loop lag hoặc scheduler/CPU, RSS và lỗi timeout. p95/p99 cao không cho biết ngay lỗi nằm ở ngôn ngữ nào.
