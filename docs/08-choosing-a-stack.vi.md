# 08. Chọn stack, đo hiệu năng và chuyển đổi

[README](../README.vi.md) · [VI](./08-choosing-a-stack.vi.md) · [EN](./08-choosing-a-stack.en.md)

## Ma trận quyết định theo workload

Các lựa chọn dưới đây là điểm bắt đầu để đánh giá, không phải xếp hạng tuyệt đối.

| Nhu cầu | Điểm bắt đầu | Lý do | Điều cần kiểm tra |
| --- | --- | --- | --- |
| Web có React và BFF, team mạnh TS | Node/TypeScript + framework hợp scope | Một hệ ngôn ngữ, ecosystem UI và API | Boundary client/server, validation, caching, CPU trong loop |
| API tích hợp I/O, service triển khai gọn | Go net/http/chi hoặc Gin/Echo | Standard library rõ, binary và concurrency model | CPU quota, DB pool, shared state, GC, shutdown |
| API sát pipeline data/ML | Python FastAPI + Uvicorn | Dùng trực tiếp ecosystem model/data | Sync/async client, CPU offload, RAM/VRAM, worker model |
| Business app cần admin/auth/ORM sẵn | Django; hoặc NestJS theo team TS | Convention và tính năng tích hợp giảm quyết định lặp | Custom requirement có hợp framework, transaction, migration |
| Training/research model | Python + PyTorch/TensorFlow/JAX theo model/team | Tool model/data/accelerator sẵn | Reproducibility, dataset, hardware, license, evaluation |
| CPU thuần application là bottleneck | Profile rồi đánh giá Go/worker/process | Lựa chọn dựa chỗ nghẽn cụ thể | End-to-end latency, serialization, algorithm, vận hành |

Không chuyển backend chỉ vì microbenchmark HTTP. Nếu phần lớn thời gian ở database hoặc external API, thay ngôn ngữ có thể đem lại rất ít lợi ích nhưng tăng chi phí chuyển đổi. Nếu team chưa có kinh nghiệm Go/Python, thời gian học và debug là một phần chi phí stack.

## Stack mẫu để thảo luận

| Stack | Thành phần | Đánh giá |
| --- | --- | --- |
| Node API nhỏ | Fastify + JSON Schema/Ajv + pg + Pino + Vitest | Contract rõ và SQL trực tiếp; cần tự tổ chức domain và migration. |
| Node team backend | NestJS + validation pipe + Prisma/Drizzle + integration tests | Convention/DI hữu ích khi nhiều module; review abstraction và query. |
| Go service SQL | net/http/chi + pgx/sqlc + slog + testing/httptest | SQL dễ review, ít lớp runtime; migration/domain validation chọn riêng. |
| Python typed API | FastAPI + Pydantic v2 + SQLAlchemy/Psycopg + pytest + Uvicorn | Dễ nối API/data; cần thống nhất sync hoặc async driver/session lifecycle. |
| Python business web | Django + ORM/migration/admin/auth + integration tests | Tính năng tích hợp tốt; convention và custom flow phải cân bằng. |
| AI product | API ngôn ngữ team biết + provider SDK hoặc inference service | Chỉ thêm orchestration khi workflow cần; đo quality và cost cùng latency. |

Nguồn capability của các thành phần: [catalog](./06-ecosystem.vi.md), [AI platforms](./07-ai-platforms.vi.md). “Stack mẫu” là đề xuất kỹ thuật theo workload; repo demo không tích hợp database/AI provider.

## Cách đo công bằng

1. Cố định endpoint contract, payload, HTTP version, keep-alive, TLS/proxy và dependency I/O.
2. Ghi OS/CPU/RAM, container quota, runtime/framework version, worker/process count và DB pool.
3. Warm up rồi chạy đủ lâu; đặt load generator ngoài server khi có thể.
4. Thử nhiều mức concurrency, cả tải bình thường lẫn overload; lặp lại để thấy độ dao động.
5. Báo cáo throughput, p50/p95/p99 latency, error/timeout, CPU, RSS, queue depth và DB wait.
6. Với AI: thêm time-to-first-token, token/sec, output length, model/hardware, batching và quality.

Đừng so Node 1 worker với Python 8 worker hay Go nhiều core rồi kết luận chỉ về cú pháp. Có thể đo cấu hình sản phẩm thực tế, nhưng phải ghi rõ phân bổ tài nguyên và chi phí. `/wait` mô phỏng chờ timer, không đo networking/database; `/sum` là payload nhỏ, không đại diện toàn ứng dụng. Bộ check trong repo chứng minh contract cơ bản, không đưa ra số liệu hiệu năng.

## Thí nghiệm blocking có chủ đích

Trong một branch local, thêm cùng tác vụ CPU nặng vào handler của cả ba demo. Chạy `/health` đồng thời và quan sát latency. Node event loop và Python asyncio loop bị giữ khi compute không nhường; Go có thể dùng các CPU khả dụng nhưng vẫn tranh tài nguyên. Sau đó thử worker/process pool hoặc compute service riêng, ghi cả overhead dispatch/serialization.

Không dùng sleep đồng bộ thay cho benchmark CPU: sleep giữ/block thread nhưng không tạo cùng áp lực CPU. Không gọi external API trả phí trong benchmark nếu chưa có budget. Giới hạn input và thời gian compute để bài tập không vô tình làm máy quá tải.

## Chuyển đổi từ Node sang Go/Python

| Mẫu Node | Chuyển sang Go | Chuyển sang Python |
| --- | --- | --- |
| TypeScript DTO | Struct + optional/null rõ + validation | Type hint/BaseModel + strict/coercion rõ |
| Promise.all | Goroutine + error/cancel/bounds | gather/TaskGroup + semaphore/error policy |
| Throw và middleware lỗi | Return error, boundary map status | Exception type, handler map status |
| Request-local state | Context/value hoặc parameter tường minh | Scope/dependency/contextvars theo framework |
| npm package | Standard library trước, rồi module cần thiết | Standard library hoặc PyPI + environment/lock |
| In-memory singleton | Shared goroutine state cần synchronization | Mỗi process có bản riêng; async interleaving vẫn có race logic |

Port theo **hành vi**, không theo từng dòng. Viết contract test cho validation, missing/null, numeric precision, datetime/timezone, pagination, transaction và error shape trước khi đổi service. Giữ business logic ngoài HTTP context; dịch dần một boundary dễ rollback.

## Bài tập mở rộng

- Thêm `POST /users` trong cả ba stack với cùng chính sách missing/null/extra field.
- Thêm PostgreSQL bằng parameterized query; kiểm tra rollback và timeout.
- Hủy client đang chờ và kiểm tra compute/I/O upstream đã dừng; bổ sung ASGI disconnect handling.
- Thêm worker queue bounded và đo queue delay khi overload.
- Tạo bộ câu hỏi AI với output kỳ vọng; so integration direct SDK và orchestration theo task thực tế.

Đây là bài tập chưa triển khai, không thuộc các ví dụ đã được bộ check xác nhận. Khi đóng góp, cập nhật cả hai bản ngôn ngữ và ghi nguồn mới gần claim tương ứng.

## Từ recipe đến hệ thống có thể vận hành

| Sản phẩm | Điểm khởi đầu | Lý do và bước tiếp theo |
| --- | --- | --- |
| Web business có backoffice | Django/DRF hoặc Nest + UI | Convention/auth/admin hoặc DI/modules; kiểm tra permission và transaction |
| API nhỏ có contract rõ | Fastify/Zod/pg, chi/pgx/sqlc, FastAPI/Pydantic/SQLAlchemy | Chọn theo team và integration; cả ba cần schema/error/query checks |
| Bảng/ML thử nghiệm | pandas/Pandera/sklearn/MLflow | Baseline đơn giản, split/eval đúng trước DL/distributed |
| Analytics Parquet local | Polars lazy hoặc DuckDB + PyArrow | Aggregate trước materialize; đo RAM/scan/query plan |
| AI web/RAG | Node UI/API hoặc Go gateway + Python/model server | Tách app auth/retrieval khỏi inference capacity khi cần |

Đưa recipe vào production theo hành vi cần chứng minh: input sai bị từ chối; user khác không đọc được row/document; transaction giữ invariant khi concurrent; dependency timeout có lỗi thống nhất; retry không lặp side effect; shutdown drain được request/job; model có version và rollback. Demo kiểm tra một phần các hành vi này, không mặc định đã hoàn thành mọi integration.

Thay package chỉ khi có lý do đo được hoặc giảm chi phí team: query bottleneck cần query/index, RAM model cần batch/quantization/topology, code khó maintain có thể cần convention. Migration giữa Node/Go/Python phải giữ contract status/error, null/coercion/date/large-int và cancellation, không chỉ dịch cú pháp.
