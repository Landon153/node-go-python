# 01. Nền tảng và cách đọc

[README](../README.vi.md) · [VI](./01-foundations.vi.md) · [EN](./01-foundations.en.md)

## Mục tiêu

Tài liệu giúp người đã biết một ngôn ngữ đọc và viết hai ngôn ngữ còn lại. Node.js là runtime của JavaScript; Go và Python là ngôn ngữ. Khi so sánh server, Python trong tài liệu là CPython có GIL mặc định, còn Node chạy JavaScript ESM. TypeScript chỉ xuất hiện khi nói về kiểu dữ liệu và hệ sinh thái.

Ý tưởng trình bày cùng tác vụ bằng nhiều ngôn ngữ được tham khảo từ [golang-for-nodejs-developers](https://github.com/miguelmota/golang-for-nodejs-developers) của Miguel Mota. Các ví dụ ở repo này được viết mới, mở rộng thêm Python, mô hình thực thi server và đánh giá hệ sinh thái. Không coi các API trong repo tham khảo là hướng dẫn phiên bản hiện hành.

## Các lớp cần phân biệt

| Lớp | Node.js | Go | Python |
| --- | --- | --- | --- |
| Ngôn ngữ | JavaScript; TypeScript bổ sung kiểm tra kiểu khi phát triển | Go, kiểu tĩnh | Python, kiểu động; type hint tùy chọn |
| Runtime | V8 + libuv + API Node | Scheduler, GC, netpoll trong runtime Go | CPython; `asyncio` là thư viện event loop |
| HTTP server | `node:http` hoặc server do framework khởi tạo | `net/http.Server` | Uvicorn/Hypercorn cho ASGI; Gunicorn cho mô hình worker phù hợp |
| Framework | Express, Fastify, NestJS | chi, Gin, Echo, Fiber | FastAPI, Starlette, Django, Flask |
| Tool quản lý | npm/pnpm, `package.json` | `go.mod`, Go toolchain | pip/uv, virtualenv, `pyproject.toml` |

Một framework không tự thay đổi cơ chế thực thi của runtime. NestJS vẫn dùng Node; FastAPI vẫn cần ASGI server; Go vẫn cần giới hạn tài nguyên dù có goroutine.

## Phạm vi phiên bản

Ví dụ dùng Node 24, Go 1.22 trở lên và Python 3.12 trở lên. Bộ kiểm tra ban đầu chạy trên Node 24.14.0, Go 1.26.5, CPython 3.12.4; CI dùng Node 24 / Go 1.26.x / Python 3.12. `go.mod` giữ mốc 1.22 vì code chỉ cần mức này; điều đó cũng ảnh hưởng một số mặc định runtime có cơ chế tương thích theo phiên bản. Dependency Python được ghi trong requirements.

Nguồn và đánh giá thư viện được kiểm tra ngày **10/10/2026**. “Thường gặp” ở đây là danh sách công cụ đại diện cho từng nhu cầu, không phải bảng xếp hạng dựa trên số lượt tải hay khảo sát. Đánh giá ưu/nhược điểm là nhận định kỹ thuật theo tiêu chí độ đơn giản, cách tích hợp và chi phí vận hành. Kiểm tra release, license và yêu cầu toolchain trước khi chọn cho dự án thật.

## Lộ trình

1. Chương 2–3: cú pháp, collection, kiểu dữ liệu, JSON, lỗi và I/O.
2. Chương 4: event loop, goroutine, GIL, WSGI/ASGI và worker.
3. Chương 5: chạy ba server, dùng cùng contract để kiểm tra.
4. Chương 6–7: lựa chọn thư viện, AI application và model serving.
5. Chương 8: chọn kiến trúc, đo workload và tránh chuyển đổi máy móc.

Các ô trong bảng cú pháp là mảnh code trong ngữ cảnh phù hợp. File trong `examples/` là chương trình đầy đủ chạy được. Không cần tài khoản cloud, database hoặc API key để chạy bộ kiểm tra.

## Nguồn nền tảng

[Node documentation](https://nodejs.org/api/), [Go specification](https://go.dev/ref/spec), [Python tutorial](https://docs.python.org/3.12/tutorial/), [TypeScript handbook](https://www.typescriptlang.org/docs/handbook/intro.html).
