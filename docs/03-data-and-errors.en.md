# 03. Data, I/O and errors

[README](../README.en.md) · [VI](./03-data-and-errors.vi.md) · [EN](./03-data-and-errors.en.md)

## JSON and numbers

| Task | Node.js | Go | Python |
| --- | --- | --- | --- |
| Decode | `JSON.parse(text)` | `json.Unmarshal(data, &value)` | `json.loads(text)` |
| Encode | `JSON.stringify(value)` | `json.Marshal(value)` | `json.dumps(value)` |
| Unicode code points | `[...text].length` | `utf8.RuneCountInString(text)` | `len(text)` |
| UTF-8 bytes | `Buffer.byteLength(text)` | `len(text)` | `len(text.encode("utf-8"))` |
| Bytes → hex | `buffer.toString("hex")` | `hex.EncodeToString(data)` | `data.hex()` |
| Large integers | `BigInt` | `math/big.Int` | `int` |

JavaScript Number cannot represent every integer above `2**53 - 1` precisely; `BigInt` cannot be passed directly to `JSON.stringify`. Python int is not limited to int64; Go int width depends on architecture. Exchange large IDs as strings or define an explicit numeric schema across services.

Go JSON decoding into `any` normally uses float64 for numbers; use structs or Decoder.UseNumber for control. Struct fields need to be exported, with `json` tags for API names. Correct data types do not establish ranges or business validity. Define separate behavior for JSON `null`, missing keys, empty arrays, and empty strings.

`"Việt"` has 4 code points and 6 UTF-8 bytes. Code points do not always equal visible characters: combining marks and emoji may need grapheme processing. JavaScript `.length` counts UTF-16 code units. Do not cut arbitrary text by byte length.

Sources: [JSON.stringify](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify), [Go encoding/json](https://pkg.go.dev/encoding/json), [Python JSON](https://docs.python.org/3.12/library/json.html), [Node Buffer](https://nodejs.org/api/buffer.html).

## File I/O and cleanup

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
# This remains synchronous I/O inside an async handler.
# You can await asyncio.to_thread(path.read_text, encoding="utf-8").
```

Complete examples create temporary directories and clean up with `finally`, `defer`, or a context manager. Whole-file reads suit small data; large files need streaming and size limits. Node streams require respecting `write()`/`drain`; Go provides `io.Copy`; Python supports iterators or framework-specific streaming responses. Proxy buffering and slow clients also affect response streaming.

Sources: [Node fs](https://nodejs.org/api/fs.html), [Node streams](https://nodejs.org/api/stream.html), [Go io](https://pkg.go.dev/io), [Python pathlib](https://docs.python.org/3.12/library/pathlib.html).

## Error semantics go beyond syntax

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
// Callers use errors.Is / errors.As rather than comparing strings.
```

```python
def load():
    try:
        return Path("hello.txt").read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("load failed") from exc
```

JS exceptions/rejected Promises and Python exceptions transfer control; Go returns an error for the caller to handle. `panic/recover` is not the usual response to expected request errors. At HTTP boundaries, map invalid input → 400, unauthenticated → 401, forbidden → 403, missing → 404, and internal failure → 500 according to the API contract. Do not expose stack traces in responses.

Sources: [JS Error](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error), [Go errors](https://pkg.go.dev/errors), [Python exceptions](https://docs.python.org/3.12/tutorial/errors.html).

## Concurrency, limits, and cancellation

| Need | Node.js | Go | Python |
| --- | --- | --- | --- |
| Concurrent I/O | `Promise.all` | goroutines + WaitGroup/channels | `asyncio.gather` / TaskGroup |
| Limit in-flight work | Worker queue/semaphore | Buffered channel/semaphore | `asyncio.Semaphore` |
| Deadline | AbortSignal + signal-aware APIs | `context.WithTimeout` + context-aware APIs | `asyncio.timeout` + cancellation-aware APIs |
| Parallel CPU work | `worker_threads` pool/processes | goroutines + concurrency bounds | ProcessPoolExecutor; suitable native libraries or free-threaded builds |

A rejected `Promise.all` does not cancel the other promises automatically. Default `gather` propagates the first exception without automatically cancelling all siblings; TaskGroup cancels siblings when a task fails. WaitGroup only waits: it neither carries errors nor cancels work. Go's `errgroup.WithContext` can help, but the context must reach clients and databases.

The [three concurrency examples](../examples/concurrency/) run 6 jobs with at most 2 in flight and preserve input order in their output. Sleep simulates waiting for I/O, not CPU computation. Go creates all 6 goroutines before gating with a channel; millions of jobs need a worker queue to bound goroutine count and memory too. Python gather also creates all 6 tasks; its semaphore bounds only the inner region.

Sources: [Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all), [asyncio tasks](https://docs.python.org/3.12/library/asyncio-task.html), [Go context](https://pkg.go.dev/context), [errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup).
