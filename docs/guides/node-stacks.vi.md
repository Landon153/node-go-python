# Node.js: stack, thư viện và recipe thực tế

[README](../../README.vi.md) · [VI](node-stacks.vi.md) · [EN](node-stacks.en.md)

Các mục dưới đây trả lời công cụ làm gì, dùng cho tình huống nào và đánh đổi gì. Ví dụ inline là fragment, cần import/instance/config tương ứng; không phải project chạy đầy đủ. Những lựa chọn này là đánh giá theo workload, không phải bảng xếp hạng tốc độ.

## Web, UI và API

### Express

**Công dụng và tình huống:** Router/middleware nhỏ cho REST hoặc app cũ cần chuyển dần. Bạn chủ động chọn validator, logger và error handler.

**Ví dụ:** `app.get("/health", (req, res) => res.json({ok:true}))` trả JSON health.

**Đánh giá:** Dễ bắt đầu; middleware order và convention phụ thuộc team, cần chuẩn hóa lỗi/auth. [Docs](https://expressjs.com/en/guide/routing.html).

### Fastify

**Công dụng và tình huống:** API theo plugin, JSON Schema cho request/response, logging tích hợp; phù hợp service có contract rõ.

**Ví dụ:** Route schema có `required:["email"]`; body thiếu email bị từ chối trước handler.

**Đánh giá:** Ajv có thể coerce theo cấu hình; kiểm tra output sau validation. Zod cần tích hợp hoặc parse thủ công. [Docs](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/).

### NestJS

**Công dụng và tình huống:** Module/controller/service và DI cho backend nhiều domain, nhiều thành viên. Có adapter Express/Fastify.

**Ví dụ:** `@Get(":id")` route dùng `ParseIntPipe` đổi id, service đọc record; guard kiểm tra quyền.

**Đánh giá:** Structure rõ nhưng thêm decorator/DI và abstraction; không cần thiết cho một endpoint nhỏ. [Docs](https://docs.nestjs.com/).

### React

**Công dụng và tình huống:** Xây component UI và state cho browser; thường đi với Node tooling/backend.

**Ví dụ:** `useState(0)` + button tăng count và render lại view.

**Đánh giá:** Không tự cung cấp router, DB hoặc backend; phân biệt browser bundle và server code. [Docs](https://react.dev/learn).

### Next.js

**Công dụng và tình huống:** React framework với routing, server rendering và server-side endpoints cho web app.

**Ví dụ:** `app/api/health/route.ts` export `GET()` trả `Response.json({ok:true})`.

**Đánh giá:** Caching/runtime/deployment thay đổi theo version và host; endpoint không tự phù hợp job dài. [Docs](https://nextjs.org/docs).

## Validation và dữ liệu

### Zod

**Công dụng và tình huống:** Schema runtime suy ra TypeScript type: form, env, payload nhỏ/ vừa cần code dễ đọc.

**Ví dụ:** `z.object({age:z.number().int().min(18)}).safeParse({age:17})` trả `success:false`.

**Đánh giá:** TypeScript type bị xóa khi chạy; Zod kiểm tra giá trị thật. Chọn coerce có chủ đích. [Docs](https://zod.dev/).

### Ajv

**Công dụng và tình huống:** Compile JSON Schema để kiểm tra payload dùng chung giữa ngôn ngữ/contract.

**Ví dụ:** `const validate=ajv.compile(schema); validate(body)` trả boolean và lỗi ở `validate.errors`.

**Đánh giá:** Schema nên là cấu hình tin cậy; compile một lần rồi tái sử dụng, tránh mỗi request compile lại. [Docs](https://ajv.js.org/guide/getting-started.html).

### node-postgres / pg

**Công dụng và tình huống:** Driver PostgreSQL cho SQL trực tiếp và pool; phù hợp khi team muốn nhìn query rõ.

**Ví dụ:** `pool.query("select id from users where email=$1", [email])`; transaction dùng cùng một client.

**Đánh giá:** Tự viết SQL/mapping/migration; không dùng `pool.query` cho các bước thuộc cùng transaction. [Docs](https://node-postgres.com/features/transactions).

### Prisma

**Công dụng và tình huống:** Schema + generated client để truy vấn entity có types; phù hợp CRUD và onboarding.

**Ví dụ:** Với client/schema đã tạo: `prisma.user.findUnique({where:{id:42}})` trả user hoặc null.

**Đánh giá:** Phải đọc SQL/query count và index; types không bảo đảm transaction hay query tối ưu. [Docs](https://www.prisma.io/docs/orm).

### Drizzle

**Công dụng và tình huống:** Schema TypeScript và query gần SQL, kiểm soát projection/join cho app muốn ít abstraction hơn.

**Ví dụ:** `db.select({id:users.id}).from(users).where(eq(users.id,42))` chỉ lấy cột id.

**Đánh giá:** Type của expression raw là lời khai của developer; DB value không tự được runtime cast đúng type. [Docs](https://orm.drizzle.team/docs/select).

## Cache, job và giao tiếp

### node-redis

**Công dụng và tình huống:** Client Redis cho cache TTL, counter và coordination; không thay DB nguồn dữ liệu.

**Ví dụ:** `await client.set("profile:42", json, {EX:60})` cache 60 giây.

**Đánh giá:** Cần invalidation, giới hạn memory và xử lý cache miss; tránh dùng cache để quyết định quyền khi stale. [Docs](https://redis.io/docs/latest/develop/clients/nodejs/).

### BullMQ

**Công dụng và tình huống:** Queue Redis tách email, export, resize ảnh khỏi HTTP request, có worker/retry/delay.

**Ví dụ:** `queue.add("export", {reportId:42}, {jobId:"report-42", attempts:3})`; worker tạo file.

**Đánh giá:** Retry có thể lặp side effect; jobId chỉ dedupe khi job còn được lưu. Dùng key idempotency/DB constraint. [Docs](https://docs.bullmq.io/).

### fetch / Undici

**Công dụng và tình huống:** HTTP client cho gọi API; Node cung cấp fetch, Undici cung cấp thêm client/pooling control.

**Ví dụ:** `fetch(url,{signal:AbortSignal.timeout(2000)})`; kiểm tra `response.ok` trước đọc JSON.

**Đánh giá:** HTTP 4xx/5xx không tự reject fetch; timeout/cancel phải áp dụng xuyên flow. [Docs](https://nodejs.org/api/globals.html#fetch).

### jose

**Công dụng và tình huống:** Ký/xác minh JWT/JWS, mã hóa/giải mã JWE và xử lý JWKS khi tích hợp identity provider.

**Ví dụ:** `jwtVerify(token, key, {issuer, audience})` kiểm tra chữ ký và claim đã cấu hình.

**Đánh giá:** Decode JWT không xác minh; vẫn cần authorization, key rotation và lựa chọn thuật toán. [Docs](https://github.com/panva/jose).

## Kiểm thử, chất lượng và quan sát

### Vitest

**Công dụng và tình huống:** Unit/integration test cho JS/TS, mock và coverage, tiện trong hệ Vite.

**Ví dụ:** `expect(total([2,3])).toBe(5)`; test DB transaction với DB test thật khi cần.

**Đánh giá:** Mock tất cả I/O có thể bỏ qua lỗi tích hợp; coverage cao không đồng nghĩa test tốt. [Docs](https://vitest.dev/guide/).

### Playwright

**Công dụng và tình huống:** Browser automation để kiểm tra login, form và hành trình user qua UI/API.

**Ví dụ:** `await page.getByRole("button",{name:"Save"}).click()` rồi kiểm tra trạng thái đã lưu.

**Đánh giá:** Tạo data ổn định, dùng locator semantic; không thay tất cả unit test bằng UI test chậm. [Docs](https://playwright.dev/docs/intro).

### Pino

**Công dụng và tình huống:** Structured JSON logs có request context; Fastify dùng logger dựa trên Pino.

**Ví dụ:** `logger.info({orderId:42, durationMs:18}, "order created")` tạo field để search.

**Đánh giá:** Redact token/password; tránh log body/model prompt mặc định và chặn event loop bằng transport. [Docs](https://getpino.io/).

### OpenTelemetry JS

**Công dụng và tình huống:** Trace/metric nối frontend/API/DB; span cho biết thời gian nằm ở đâu.

**Ví dụ:** Tạo span `orders.create`, truyền trace context tới HTTP downstream, export OTLP.

**Đánh giá:** SDK không tự cung cấp dashboard/storage; cần collector/backend và kiểm soát cardinality. [Docs](https://opentelemetry.io/docs/languages/js/).

### TypeScript + ESLint

**Công dụng và tình huống:** Type checking và lint trong CI cho code lớn, kiểm soát contract giữa module.

**Ví dụ:** `tsc --noEmit` phát hiện gọi hàm sai kiểu; ESLint áp dụng rule đã chọn.

**Đánh giá:** Không thay validation runtime; type assertions/any có thể làm mất bảo vệ. [ESLint](https://eslint.org/docs/latest/). [Docs](https://www.typescriptlang.org/docs/handbook/intro.html).

## AI trong Node

### AI SDK

**Công dụng và tình huống:** Chuẩn hóa gọi nhiều provider, text streaming và tool call cho web/JS application.

**Ví dụ:** `streamText({model, prompt})` tạo text stream với model instance từ provider adapter.

**Đánh giá:** Cần adapter/key/model/deployment đã chọn; tool call phải validate và được phân quyền phía server. [Docs](https://ai-sdk.dev/docs/introduction).

### LangChain.js

**Công dụng và tình huống:** Ghép model, retriever, tool và agent workflow trong TypeScript.

**Ví dụ:** Retriever chọn đoạn tài liệu theo query; agent dùng tool đọc catalog để trả lời câu hỏi sản phẩm.

**Đánh giá:** Thêm abstraction và dependency; với một API call, SDK trực tiếp thường dễ debug hơn. [Docs](https://docs.langchain.com/oss/javascript/langchain/overview).

### OpenAI Node SDK

**Công dụng và tình huống:** Client official gọi API model từ Node/TypeScript: generation, structured output và các endpoint hỗ trợ.

**Ví dụ:** `client.responses.create({model:process.env.MODEL, input:"Explain HTTP"})`; đọc `output_text`.

**Đánh giá:** Cần key và model có quyền truy cập; API timeout/retry không thay budget, eval hay bảo vệ dữ liệu. [Docs](https://github.com/openai/openai-node).

## Recipe 1: API nhỏ, validation rõ

**Stack:** Node + Fastify + Zod + pg + Pino + Vitest. Fastify làm HTTP/plugin; Zod kiểm tra boundary; pg lưu data; Pino log có field; Vitest kiểm tra domain và request. Ví dụ dùng Zod thủ công nên lỗi là `400` do handler chọn.

Trong thư mục thử riêng, `npm init -y`, `npm install fastify@5.12.5 zod@4.6.5`, lưu đoạn sau thành `server.mjs`, chạy `node server.mjs`. Không cần DB cho đoạn này.

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

Gửi `curl -X POST http://127.0.0.1:3100/orders -H 'Content-Type: application/json' -d '{"productId":"book","quantity":2}'` nhận `201` với id demo. Quantity `0` trả `400`; chuỗi `"2"` cũng bị từ chối vì schema không coerce. Id cố định và result nằm trong memory không phải lưu đơn hàng thật.

## Recipe 2: backend nhiều domain

**Stack:** NestJS + DTO/ValidationPipe + Prisma hoặc Drizzle + PostgreSQL + BullMQ + OpenTelemetry. Dùng module tách orders/payments/identity; controller xử lý HTTP, service xử lý nghiệp vụ, repository xử lý DB. Chọn một ORM chính để tránh hai tầng schema/migration chồng nhau. Chỉ thêm queue khi công việc cần retry hoặc xử lý nền.

DTO dùng class-validator với `ValidationPipe` là một hướng của Nest; không nhầm decorator TypeScript với validation tự động. Bật pipe và cấu hình transform/whitelist có chủ đích. [Nest validation](https://docs.nestjs.com/techniques/validation).

## Recipe 3: web có AI

**Stack:** Next.js + React + Zod + AI SDK hoặc SDK provider + PostgreSQL + vector store khi có retrieval. UI đọc stream; server giữ key, xác thực tenant và giới hạn tool. Nếu model local hoặc cần training, gọi service Python/Go riêng qua API thay vì đưa training vào route UI.

## Transaction và job: điểm dễ sai

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

Đây là fragment DB có schema/pool được cấu hình trước. Đơn vị amount là integer nhỏ nhất của tiền; không dùng float cho tiền. DB commit và enqueue job là hai thao tác có thể lệch nhau: dùng transactional outbox nếu cần bảo đảm job tồn tại sau commit. Consumer vẫn cần idempotency vì retry/delivery có thể lặp. Tránh giữ DB transaction mở trong lúc đợi model AI trả lời.

## Cách đánh giá stack

Đo request validation, DB round trip, event-loop lag, pool wait và memory dưới payload thật. Tối ưu query/index trước khi thay framework. Chọn Nest khi cần convention cho team, Fastify cho service contract rõ, Express khi chi phí chuyển app hiện có lớn. React/Next giải quyết UI/rendering; chúng không thay thế thiết kế transaction và authorization của backend.
