# 03. Dữ liệu, I/O và xử lý lỗi

[README](../README.vi.md) · [VI](./03-data-and-errors.vi.md) · [EN](./03-data-and-errors.en.md)

## JSON và số

| Tác vụ | Node.js | Go | Python |
| --- | --- | --- | --- |
| Decode | `JSON.parse(text)` | `json.Unmarshal(data, &value)` | `json.loads(text)` |
| Encode | `JSON.stringify(value)` | `json.Marshal(value)` | `json.dumps(value)` |
| Unicode code point | `[...text].length` | `utf8.RuneCountInString(text)` | `len(text)` |
| Số byte UTF-8 | `Buffer.byteLength(text)` | `len(text)` | `len(text.encode("utf-8"))` |
| Bytes → hex | `buffer.toString("hex")` | `hex.EncodeToString(data)` | `data.hex()` |
| Số nguyên rất lớn | `BigInt` | `math/big.Int` | `int` |

JavaScript Number không biểu diễn chính xác mọi integer lớn hơn `2**53 - 1`; `BigInt` không được `JSON.stringify` trực tiếp. Python int không bị giới hạn như int64; Go int có độ rộng phụ thuộc kiến trúc. Truyền ID rất lớn dưới dạng chuỗi hoặc chọn schema số tường minh giữa các service.

Go decode JSON vào `any` thường cho number dạng float64; dùng struct hoặc Decoder.UseNumber khi cần kiểm soát. Struct field phải export và dùng `json` tag nếu cần tên API. Kiểu dữ liệu đúng vẫn chưa bảo đảm range hoặc quy tắc business đúng. JSON `null`, key vắng mặt, empty array và empty string cần contract riêng.

`"Việt"` có 4 code point và 6 byte UTF-8. Code point không luôn là ký tự nhìn thấy: dấu kết hợp và emoji có thể cần xử lý grapheme. JavaScript `.length` đếm UTF-16 code unit. Đừng dùng độ dài byte để cắt chuỗi văn bản tùy ý.

Nguồn: [JSON.stringify](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify), [Go encoding/json](https://pkg.go.dev/encoding/json), [Python JSON](https://docs.python.org/3.12/library/json.html), [Node Buffer](https://nodejs.org/api/buffer.html).

## File I/O và cleanup

```javascript
import { readFile } from 'node:fs/promises';
const text = await readFile('hello.txt', 'utf8');
```

```go
data, err := os.ReadFile("hello.txt")
if err != nil { return err }
text := string(data)
```

```python
from pathlib import Path
text = Path("hello.txt").read_text(encoding="utf-8")
# Trong async handler, đây vẫn là I/O đồng bộ.
# Có thể await asyncio.to_thread(path.read_text, encoding="utf-8").
```

Ví dụ đầy đủ dùng thư mục tạm rồi dọn trong `finally`, `defer`, hoặc context manager. Đọc cả file tiện cho dữ liệu nhỏ; file lớn nên stream và giới hạn dung lượng. Node stream cần tôn trọng `write()`/`drain`; Go có `io.Copy`; Python có iterator hoặc streaming response tùy framework. Việc server trả stream còn phụ thuộc proxy buffering và client đọc chậm.

Nguồn: [Node fs](https://nodejs.org/api/fs.html), [Node streams](https://nodejs.org/api/stream.html), [Go io](https://pkg.go.dev/io), [Python pathlib](https://docs.python.org/3.12/library/pathlib.html).

## Lỗi không chỉ khác cú pháp

```javascript
async function load() {
  try { return await readFile('hello.txt', 'utf8'); }
  catch (cause) { throw new Error('load failed', { cause }); }
}
```

```go
func load() ([]byte, error) {
    data, err := os.ReadFile("hello.txt")
    if err != nil { return nil, fmt.Errorf("load failed: %w", err) }
    return data, nil
}
// Caller dùng errors.Is / errors.As; không so sánh chuỗi lỗi.
```

```python
def load():
    try:
        return Path("hello.txt").read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("load failed") from exc
```

JS exception/rejected Promise và Python exception chuyển control flow; Go trả error để caller quyết định. `panic/recover` không phải mặc định cho lỗi request dự kiến. Tại HTTP boundary, map lỗi nhập liệu → 400, chưa đăng nhập → 401, không có quyền → 403, không tồn tại → 404, lỗi nội bộ → 500 theo contract. Không trả stack trace vào response.

Nguồn: [JS Error](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error), [Go errors](https://pkg.go.dev/errors), [Python exceptions](https://docs.python.org/3.12/tutorial/errors.html).

## Chờ đồng thời, giới hạn và hủy

| Nhu cầu | Node.js | Go | Python |
| --- | --- | --- | --- |
| Chờ nhiều I/O | `Promise.all` | goroutine + WaitGroup/channel | `asyncio.gather` / TaskGroup |
| Giới hạn đang chạy | Worker queue/semaphore | Buffered channel/semaphore | `asyncio.Semaphore` |
| Deadline | AbortSignal + API hỗ trợ signal | `context.WithTimeout` + API nhận context | `asyncio.timeout` + cancellation-aware API |
| CPU song song | `worker_threads` pool/process | goroutine + giới hạn concurrency | ProcessPoolExecutor; native library hoặc free-threaded build phù hợp |

`Promise.all` reject không tự hủy các promise khác. `gather` mặc định truyền exception đầu tiên nhưng không tự hủy tất cả sibling task; TaskGroup có cơ chế hủy sibling khi task lỗi. WaitGroup chỉ chờ, không truyền lỗi và không hủy. Trong Go có thể dùng `errgroup.WithContext`; vẫn phải truyền context xuống client/database.

[Ba ví dụ concurrency](../examples/concurrency/) xử lý 6 job, tối đa 2 job đang chạy, giữ kết quả theo thứ tự đầu vào. Đây là workload sleep mô phỏng chờ I/O, không mô phỏng tính toán CPU. Go tạo goroutine cho cả 6 job rồi chặn bằng channel; khi hàng triệu job, dùng worker pool/queue để giới hạn cả số goroutine và bộ nhớ. Python gather cũng tạo cả 6 task; semaphore chỉ giới hạn vùng bên trong.

Nguồn: [Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all), [asyncio tasks](https://docs.python.org/3.12/library/asyncio-task.html), [Go context](https://pkg.go.dev/context), [errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup).
