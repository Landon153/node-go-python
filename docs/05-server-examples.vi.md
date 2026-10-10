# 05. Ba server cùng một API

[README](../README.vi.md) · [VI](./05-server-examples.vi.md) · [EN](./05-server-examples.en.md)

## Contract chung

Các server bind `127.0.0.1` để chạy demo tại máy. Đây là ví dụ học runtime; chưa có database, auth, rate limit hay bộ middleware production.

| Request | Status | JSON |
| --- | --- | --- |
| `GET /health` | 200 | `{"ok":true}` |
| `GET /sum?a=2&b=3` | 200 | `{"sum":5}` |
| `GET /wait?ms=100` | 200 | `{"waited_ms":100}` |
| `GET /wait` | 200 | `{"waited_ms":50}` |
| Sai hoặc thiếu query bắt buộc | 400 | `{"error":"invalid_query"}` |
| Route không tồn tại | 404 | `{"error":"not_found"}` |
| Method khác GET | 405, `Allow: GET` | `{"error":"method_not_allowed"}` |

Query là chuỗi integer ASCII có dạng `-?(0|[1-9][0-9]*)`, tối đa 8 ký tự. `a`, `b` thuộc [-1.000.000, 1.000.000]; `ms` thuộc [0, 1000]. Không nhận whitespace, chuỗi rỗng, số thập phân, exponent hoặc leading zero. `-0` được chấp nhận. Nếu key lặp, dùng giá trị đầu tiên; key lạ được bỏ qua. Với `/sum` và `/wait`, toàn bộ query phải có percent escape hợp lệ và không chứa dấu `;` chưa encode; `%3B` vẫn là dữ liệu trong giá trị. So sánh nội dung JSON, không so thứ tự key hoặc whitespace. HEAD không có response body theo ngữ nghĩa HTTP, dù handler trả status 405.

## Cài đặt và chạy

Từ thư mục repo, tạo môi trường Python và cài dependency:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r examples/server/python/requirements.txt
```

Mở ba terminal riêng:

```sh
node examples/server/node/main.mjs
# http://127.0.0.1:3000
```

```sh
go run ./examples/server/go
# http://127.0.0.1:3001
```

```sh
.venv/bin/python examples/server/python/main.py
# http://127.0.0.1:3002
```

```sh
curl 'http://127.0.0.1:3000/sum?a=2&b=3'
curl 'http://127.0.0.1:3001/wait?ms=100'
curl 'http://127.0.0.1:3002/health'
```

Đặt `PORT=...` trước lệnh nếu cổng đang bận. Windows dùng `.venv\Scripts\python.exe`; script kiểm tra tự quản lý process group theo POSIX nên chạy bộ check trong Linux/macOS hoặc WSL.

## Đọc phần xử lý chờ

- [Node source](../examples/server/node/main.mjs): `setTimeout` lập lịch response; callback trả lại loop trong thời gian chờ. Client đóng connection thì timer được dọn qua sự kiện response `close`.
- [Go source](../examples/server/go/main.go): timer + select trên request context; goroutine có thể park. Client hủy request có thể kết thúc phần chờ qua context.
- [Python source](../examples/server/python/main.py): `await asyncio.sleep` nhường loop; app gửi ASGI response qua `send`. Uvicorn sở hữu socket, parser HTTP và loop. Demo không đọc `http.disconnect` trong lúc sleep; nó chưa tương đương cơ chế hủy sớm của Node/Go.

Python dùng API ASGI trực tiếp để thấy contract; app thực tế thường dùng FastAPI hoặc Starlette để routing, validation, exception handling và lifespan dễ bảo trì hơn. Uvicorn chạy với asyncio + h11 tường minh, không cần uvloop/httptools.

## Kiểm tra hành vi

```sh
.venv/bin/python scripts/check.py
go vet ./...
go run -race ./examples/concurrency/go
```

Script kiểm tra 21 trường JSON của syntax, concurrency tối đa 2, cả ba HTTP server, các giá trị biên/không hợp lệ, method và request chồng lấp. Script tự build Go server, chọn cổng tạm, khởi động rồi dọn process. Có timeout cho việc startup và request. Kiểm tra chồng lấp không đặt ngưỡng throughput/latency nên không phải benchmark.

## Chạy Python nhiều worker

```sh
.venv/bin/python -m uvicorn main:app \
  --app-dir examples/server/python \
  --host 127.0.0.1 --port 3002 --workers 2 \
  --loop asyncio --http h11
```

Mỗi worker là một process riêng. Không dùng `--reload` cùng `--workers`; memory cache trong một worker không tự đồng bộ sang worker khác. Reload phục vụ phát triển. Khi deploy, bổ sung proxy/TLS, body limit, timeout, monitoring, auth và shutdown phù hợp workload.

Nguồn: [Node HTTP](https://nodejs.org/api/http.html), [Go HTTP](https://pkg.go.dev/net/http), [ASGI HTTP spec](https://asgi.readthedocs.io/en/latest/specs/www.html), [Uvicorn settings](https://uvicorn.dev/settings/).
