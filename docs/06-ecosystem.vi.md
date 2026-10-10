# 06. Thư viện và hệ sinh thái

[README](../README.vi.md) · [VI](./06-ecosystem.vi.md) · [EN](./06-ecosystem.en.md)

## Cách đọc đánh giá

Danh sách dưới đây là **công cụ đại diện thường gặp**, không phải thứ hạng phổ biến theo số lượt tải. Mỗi hàng liên kết nguồn chính thức; mô tả capability dựa trên nguồn, còn lời khuyên lựa chọn là đánh giá kỹ thuật. Framework, runtime, driver, ORM và tool quản lý package được ghi rõ loại để tránh so sánh nhầm lớp.

Đọc theo nhu cầu: API nhỏ → router gọn; backend nhiều module → convention/DI; relational SQL → quyết định driver/query builder/ORM; dữ liệu ngoài hệ thống → validation runtime; AI → phân biệt gọi provider với train/serve model. Chỉ cài phần cần dùng; các ví dụ repo không cài toàn bộ thư viện trong danh sách.

## Node.js / JavaScript / TypeScript

| Công cụ / nguồn | Nhóm | Điểm mạnh và khi dùng | Giới hạn và đánh giá |
| --- | --- | --- | --- |
| [Express](https://expressjs.com/) | Web / API | Router/middleware gọn, dễ nhìn luồng request. Phù hợp API nhỏ hoặc team muốn tự chọn kiến trúc. | Phải bổ sung validation, DI, OpenAPI theo nhu cầu. Đừng trộn ví dụ Express 4 và 5. |
| [Fastify](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/) | Web / API | Plugin encapsulation, schema validation và serialization tạo contract API rõ ràng. | Schema là code đáng tin của ứng dụng; không nhận schema tùy ý từ user. Rule cần database nên chạy sau structural validation. |
| [NestJS](https://docs.nestjs.com/) | BE architecture | Module/controller/provider, DI, guard và pipe phù hợp backend nhiều module và team đông. | Nhiều convention hơn router nhỏ. Mặc định dùng Express hoặc cấu hình Fastify adapter; vẫn là Node runtime. |
| [React](https://react.dev/) | Frontend | Component và state cho UI browser; dùng chung JavaScript/TypeScript với backend. | React không phải HTTP server. Cần framework/tooling, data fetching và accessibility phù hợp sản phẩm. |
| [Next.js](https://nextjs.org/docs) | Full-stack web | React routing/rendering, server/client component và route handler; tốt cho web có BFF. | Cần hiểu caching và ranh giới server/client. API service độc lập đôi khi dùng framework BE riêng đơn giản hơn. |
| [Zod](https://zod.dev/) | Validation | Schema code-first và TypeScript inference; thuận tiện cho request, form và tool input. | TypeScript type không validate runtime. Chọn coercion/default tường minh; browser schema không thay kiểm tra server. |
| [Ajv](https://ajv.js.org/) | Validation | JSON Schema phù hợp contract trao đổi đa ngôn ngữ và API specification. | Dialect và option quan trọng; coercion/default/removal có thể sửa input. Schema compilation không phải sandbox. |
| [Prisma](https://www.prisma.io/docs) | Database / ORM | Schema khai báo, generated typed client và migration dễ tiếp cận CRUD relational. | Thêm bước generate và convention schema. Kiểm tra query, transaction và query phức tạp thay vì tin ORM tự tối ưu. |
| [Drizzle](https://orm.drizzle.team/docs/overview) | Database / ORM | Schema TypeScript và query gần SQL; hợp team muốn giữ SQL dễ nhìn. | Type safety không thay constraint/index DB. Driver và migration vẫn cần cấu hình, review. |
| [node-postgres / pg](https://node-postgres.com/) | Database driver | SQL trực tiếp, parameterized query và pooling cho PostgreSQL. | Tự quản lý mapping/migration. Transaction phải dùng một checked-out client, không nhiều pool.query rời rạc. |
| [Vitest](https://vitest.dev/guide/) | Testing | Unit/integration, mock, coverage và watch; hợp project dùng Vite/TypeScript. | Môi trường giả browser không chứng minh hành vi browser thật. Test public behavior và boundary quan trọng. |
| [Playwright](https://playwright.dev/docs/intro) | E2E | Browser thật, nhiều engine và trace giúp kiểm chứng flow UI. | Browser binary, fixture và isolation tăng chi phí CI. Chọn flow quan trọng để suite không phình quá mức. |
| [Pino](https://github.com/pinojs/pino) | Logging | JSON logging và integration framework; phù hợp log có cấu trúc. | Redaction/transport/retention là thiết kế riêng; tránh log secret hoặc request body nhạy cảm. |
| [AI SDK](https://ai-sdk.dev/docs/introduction) | AI application | Text, structured output, tool và streaming với TypeScript; tiện nối UI chat với backend. | Provider không có feature parity tuyệt đối. Vẫn cần timeout, budget, evaluation và quyền gọi tool. |
| [LangChain.js](https://docs.langchain.com/oss/javascript/langchain/overview) | AI orchestration | Model/tool integration và agent; LangGraph cung cấp khả năng điều phối execution. | Thêm abstraction và package. Một call đơn giản có thể dùng provider SDK dễ debug hơn. |
| [OpenAI Node SDK](https://github.com/openai/openai-node) | AI provider SDK | Client chính thức JavaScript/TypeScript, typed API và streaming. | Phụ thuộc provider; giữ key phía server. Cấu hình retry/cancel/timeout theo request budget. |

## Go

| Công cụ / nguồn | Nhóm | Điểm mạnh và khi dùng | Giới hạn và đánh giá |
| --- | --- | --- | --- |
| [net/http](https://pkg.go.dev/net/http) | Web / standard library | HTTP client/server, routing, request context và shutdown; điểm khởi đầu tốt cho Go server. | Không cung cấp ORM/DI/business validation. Cấu hình timeout/limit và tái dùng client/transport. |
| [chi](https://github.com/go-chi/chi) | Web / router | Router nhẹ, middleware theo interface net/http; dễ ghép với standard library. | Team tự chọn validation, DB, dependency wiring và API docs. |
| [Gin](https://gin-gonic.com/en/docs/) | Web / API | Routing, middleware, binding và validation phù hợp xây REST API nhanh. | Context riêng của framework tạo coupling; binding không thay authorization hay business rule. |
| [Echo](https://echo.labstack.com/guide/quickstart/) | Web / API | Routing, middleware, binding và centralized error handling; thuận tiện API. | Giữ domain logic độc lập với context framework để dễ test và chuyển đổi. |
| [Fiber](https://docs.gofiber.io/) | Web / API | API gợi nhớ Express trên fasthttp; có routing và middleware. | v3 có adapter net/http nhưng runtime HTTP vẫn là fasthttp. Chú ý compatibility và lifetime buffer request khi giữ dữ liệu sau handler. |
| [go-playground/validator](https://github.com/go-playground/validator) | Validation | Struct tag, nested field và custom rule tiện cho payload typed. | Rule reflection/tag phức tạp khó đọc; business validation nên có code rõ. Xem option required nested struct. |
| [pgx](https://github.com/jackc/pgx) | Database driver | PostgreSQL toolkit, pool và native feature; có interoperability database/sql. | Chuyên PostgreSQL; SQL, mapping, transaction và migration vẫn thuộc ứng dụng. |
| [sqlc](https://docs.sqlc.dev/en/latest/) | SQL code generation | Sinh query method typed từ SQL, giảm scanning/mapping bằng tay. | Là generator, không phải runtime ORM hay migration runner. Kiểm tra dialect và generated code. |
| [GORM](https://gorm.io/docs/) | Database / ORM | CRUD, association, hook và transaction; dễ tiếp cận app business. | Cẩn thận implicit query và association loading. AutoMigrate không thay chiến lược migration production được review. |
| [testing + httptest](https://pkg.go.dev/net/http/httptest) | Testing / standard library | Test runner chuẩn và HTTP recorder/server; ít dependency cho handler test. | Recorder không mô phỏng hết network behavior; test integration thật ở boundary cần thiết. |
| [Testify](https://github.com/stretchr/testify) | Testing | Assertion/require/mock/suite trên testing chuẩn giúp assertion dễ đọc. | Tránh mock chi tiết implementation; testing chuẩn có thể đủ cho suite nhỏ. |
| [log/slog](https://pkg.go.dev/log/slog) | Logging / standard library | Structured log, attribute và handler có sẵn trong standard library. | Cần thiết kế redaction, routing, retention và trace correlation riêng. |
| [OpenTelemetry Go](https://opentelemetry.io/docs/languages/go/) | Observability | Trace/metric để quan sát distributed system và export sang backend phù hợp. | Stability theo signal/component; exporter và vận hành backend tách biệt instrumentation. |
| [OpenAI Go SDK](https://github.com/openai/openai-go) | AI provider SDK | SDK chính thức, request typed, context và streaming; phù hợp AI gateway Go. | Major module path/toolchain có thể đổi; pin release tương thích. Không phải framework train tensor. |
| [Genkit Go](https://genkit.dev/docs/go/get-started/) | AI orchestration | AI flow, typed input/output, plugin và tracing. | Kiểm tra plugin/deployment riêng cho Go; không giả định mọi language có cùng feature hoặc status. |

## Python

| Công cụ / nguồn | Nhóm | Điểm mạnh và khi dùng | Giới hạn và đánh giá |
| --- | --- | --- | --- |
| [FastAPI](https://fastapi.tiangolo.com/) | Web / API | Type hint + Pydantic, DI, OpenAPI và docs tương tác; phù hợp API typed. | Cần ASGI server riêng; async endpoint không được gọi I/O sync hoặc CPU nặng trực tiếp trên loop. |
| [Django](https://docs.djangoproject.com/en/stable/) | Full-stack web | ORM, migration, admin, auth, form/template và convention đầy đủ cho app business. | Surface lớn hơn microframework. Async theo component; hiểu middleware, ORM và deployment interface. |
| [Flask](https://flask.palletsprojects.com/en/stable/) | Web / WSGI | Routing/template gọn và extension ecosystem; hợp app nhỏ, ghép tính năng tường minh. | Validation/ORM/OpenAPI cần thêm thư viện. Async view vẫn nằm trong mô hình WSGI worker. |
| [Starlette](https://starlette.dev/) | Web / ASGI | Routing, middleware, WebSocket, response và lifespan; lớp web nền của FastAPI. | Thấp hơn FastAPI; typed body validation và automatic OpenAPI không phải chức năng chủ đạo. |
| [Uvicorn](https://uvicorn.dev/) | ASGI server | Event-loop HTTP serving, hỗ trợ worker process và FastAPI/Starlette. | Là server, không phải framework. Reload/workers loại trừ nhau; cần limit và deployment config. |
| [Gunicorn](https://gunicorn.org/) | HTTP / process manager | UNIX master/worker, WSGI deployment hoặc ASGI qua worker package phù hợp. | Worker class quyết định concurrency; WSGI sync không chạy ASGI tự động. Không dành cho Windows native. |
| [Pydantic v2](https://pydantic.dev/docs/validation/latest/) | Validation | Type-driven validation/serialization, JSON Schema, strict/lax mode và Rust core. | Lax parsing có coercion; dùng strict khi contract yêu cầu. v2 dùng model_dump/field_validator, khác v1. |
| [SQLAlchemy](https://docs.sqlalchemy.org/en/20/intro.html) | Database / ORM | SQL Core + ORM, transaction, pooling và integration sync/async. | Cần hiểu session/identity map/lazy load. Không chia một session giữa các concurrent task; migration cần tool riêng. |
| [Psycopg 3](https://www.psycopg.org/psycopg3/docs/) | Database driver | PostgreSQL trực tiếp với API sync/async và feature native. | Không phải ORM; tự quản lý SQL/mapping/transaction/pooling. Phân biệt package và ví dụ psycopg2. |
| [pytest](https://docs.pytest.org/en/stable/) | Testing | Fixture, parametrization và assertion gọn cho unit/integration. | Plugin và fixture lifetime có thể tăng độ ẩn; isolation và external service phải có chủ đích. |
| [Ruff](https://docs.astral.sh/ruff/) | Lint / format | Lint và format Python trong một công cụ với rule/fix cấu hình được. | Không thay type checker hay runtime test. Review fix có thể ảnh hưởng semantics. |
| [uv](https://docs.astral.sh/uv/) | Package tooling | Quản lý project/dependency/environment, lockfile và interpreter. | Không phải Uvicorn. Học lock workflow và kiểm tra reproducibility trên target platform. |
| [Celery](https://docs.celeryq.dev/en/stable/) | Job queue | Distributed task và scheduling để tách việc lâu khỏi request HTTP. | Cần broker/worker và failure policy; thiết kế idempotency khi task retry/delivery lặp. |
| [NumPy](https://numpy.org/doc/stable/) | Numerical computing | Array nhiều chiều, vectorization và linear algebra; nền cho scientific Python. | Dtype/shape/view/copy ảnh hưởng kết quả và RAM. Không phải web framework hay distributed processing engine. |
| [pandas](https://pandas.pydata.org/docs/) | Data processing | DataFrame, join, aggregation và I/O cho dữ liệu bảng. | Cần RAM cho xử lý in-memory; tránh loop từng row khi có vectorization. Quy định schema/missing value. |
| [scikit-learn](https://scikit-learn.org/stable/) | Classical ML | Preprocessing, pipeline, model selection, classification/regression/clustering. | Tránh data leakage và đánh giá trên data train. Không phải lựa chọn mặc định để train LLM neural lớn. |
| [PyTorch](https://docs.pytorch.org/docs/stable/index.html) | Deep learning | Tensor, autograd, neural network và accelerator cho training/inference. | Cần thiết kế hardware, memory và batching. Có API ổn định và thử nghiệm; framework không bảo đảm model tốt. |
| [Transformers](https://huggingface.co/docs/transformers/index) | Pretrained models | Model definition, tokenizer/preprocessor, pipeline và generation/training cho nhiều modality. | License theo từng model, kiểm tra trust và RAM/VRAM. Pipeline tiện không đồng nghĩa serving production đã tối ưu. |
| [vLLM](https://docs.vllm.ai/en/latest/) | LLM inference serving | Continuous batching, KV-cache, streaming, parallelism và HTTP API compatibility. | Support phụ thuộc model/hardware/API. Cần admission control và budget; không phải universal training framework. |
| [LangChain Python](https://docs.langchain.com/oss/python/langchain/overview) | AI orchestration | Provider interface, tool và agent; nối với LangGraph để điều phối nhiều bước. | Orchestration không bảo đảm chất lượng output hay tool an toàn. Direct SDK có thể đủ cho workflow đơn giản. |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | AI provider SDK | Client chính thức sync/async, streaming và typed response. | Provider API client, không phải local neural runtime. Chọn AsyncClient nếu server cần async I/O. |

## Các nhu cầu xung quanh backend

| Nhu cầu | Node.js | Go | Python | Tiêu chí chọn |
| --- | --- | --- | --- | --- |
| HTTP outbound | [fetch](https://nodejs.org/api/globals.html#fetch) | [net/http](https://pkg.go.dev/net/http) | [HTTPX](https://www.python-httpx.org/) | Reuse client/pool; timeout tổng và cancellation; sync/async phải hợp server. |
| Redis/cache | [node-redis](https://redis.io/docs/latest/develop/clients/nodejs/) | [go-redis](https://redis.io/docs/latest/develop/clients/go/) | [redis-py](https://redis.io/docs/latest/develop/clients/redis-py/) | TTL, cache invalidation, pool và failure policy; cache không thay database truth. |
| Job queue | [BullMQ](https://docs.bullmq.io/) | [Asynq](https://github.com/hibiken/asynq) | [Celery](https://docs.celeryq.dev/en/stable/) | Broker, retry, idempotency, visibility và dead-letter; queue không tự bảo đảm exactly-once. |
| Migration SQL | [Knex migrations](https://knexjs.org/guide/migrations.html) | [golang-migrate](https://github.com/golang-migrate/migrate) | [Alembic](https://alembic.sqlalchemy.org/en/latest/) | Version migration và rollback/roll-forward theo DB; tránh schema update tự phát lúc startup. |
| Observability | [OpenTelemetry JS](https://opentelemetry.io/docs/languages/js/) | [OpenTelemetry Go](https://opentelemetry.io/docs/languages/go/) | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) | Trace propagation, cardinality metric, sampling và dữ liệu nhạy cảm; stability theo component. |
| Authentication | [Passport](https://www.passportjs.org/) hoặc OIDC integration | [go-oidc](https://github.com/coreos/go-oidc) | [Authlib](https://docs.authlib.org/) / Django auth | Xác thực identity khác authorization business; chọn flow phù hợp browser/API, verify issuer/audience. |
| Type/lint/format | [TypeScript](https://www.typescriptlang.org/docs/), [ESLint](https://eslint.org/), [Prettier](https://prettier.io/) | gofmt, go vet, [Staticcheck](https://staticcheck.dev/) | [mypy](https://mypy.readthedocs.io/), Ruff | Không thay test và validation runtime; rule nên giúp phát hiện lỗi thực. |

## Ví dụ chọn thư viện validation

**TypeScript + Zod** (snippet minh họa, cần cài Zod):

```typescript
import { z } from 'zod';
const User = z.object({ name: z.string().min(1), age: z.number().int().min(0) });
const user = User.parse({ name: 'Ada', age: 28 });
```

**Go**: JSON decode vào struct rồi validate domain bằng code hoặc struct-tag validator. Cần phân biệt field thiếu với zero value khi field bắt buộc.

```go
type User struct { Name string `json:"name"`; Age *int `json:"age"` }
func validate(u User) error {
    if u.Name == "" || u.Age == nil || *u.Age < 0 { return errors.New("invalid user") }
    return nil
}
```

**Python + Pydantic v2** (snippet minh họa, cần cài Pydantic v2):

```python
from pydantic import BaseModel, ConfigDict, Field
class User(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
user = User.model_validate({"name": "Ada", "age": 28})
print(user.model_dump())
```

Đây không phải ba schema hoàn toàn tương đương: chính sách extra field, Unicode, coercion và missing/null cần khai báo nếu muốn chung contract. Validation cấu trúc xong vẫn cần kiểm tra quyền và quy tắc business. Với API public, OpenAPI/JSON Schema và contract test giảm lệch giữa các service.
