# 02. So sánh cú pháp

[README](../README.vi.md) · [VI](./02-syntax.vi.md) · [EN](./02-syntax.en.md)

## Tra cứu nhanh

| Tác vụ | Node.js / JavaScript | Go | Python |
| --- | --- | --- | --- |
| Chú thích | `// note`, `/* note */` | `// note`, `/* note */` | `# note` |
| In ra console | `console.log("hi")` | `fmt.Println("hi")` | `print("hi")` |
| Biến | `let count = 1` | `count := 1` | `count = 1` |
| Hằng số | `const LIMIT = 10` | `const Limit = 10` | `LIMIT = 10` (quy ước) |
| Boolean | `true`, `false` | `true`, `false` | `True`, `False` |
| Thiếu / null | `undefined`, `null` | `nil` (kiểu hỗ trợ nil) | `None` |
| Kiểm tra kiểu | `typeof x`; `Array.isArray(x)` | `fmt.Printf("%T", x)` | `type(x)`, `isinstance(x, int)` |
| Chèn biến vào chuỗi | `` `Hi, ${name}` `` | `fmt.Sprintf("Hi, %s", name)` | `f"Hi, {name}"` |
| Chuyển kiểu | `Number("42")` | `strconv.Atoi("42")` → `(int, error)` | `int("42")` → `ValueError` khi lỗi |
| Điều kiện | `if (x > 0) { ... } else { ... }` | `if x > 0 { ... } else { ... }` | `if x > 0:` / `else:` |
| Giá trị điều kiện | `ok ? "yes" : "no"` | `if` + gán biến | `"yes" if ok else "no"` |
| Vòng lặp đếm | `for (let i = 0; i < 3; i++) { ... }` | `for i := 0; i < 3; i++ { ... }` | `for i in range(3):` |
| Vòng lặp while | `while (ok) { ... }` | `for ok { ... }` | `while ok:` |
| Duyệt collection | `for (const x of xs) { ... }` | `for _, x := range xs { ... }` | `for x in xs:` |
| Index và giá trị | `for (const [i, x] of xs.entries()) { ... }` | `for i, x := range xs { ... }` | `for i, x in enumerate(xs):` |
| Rẽ nhánh | `switch (x) { case 1: break; }` | `switch x { case 1: ... }` | `match x:` / `case 1:` (3.10+) |
| Danh sách | `const xs = [1, 2]` | `xs := []int{1, 2}` (slice) | `xs = [1, 2]` |
| Thêm phần tử | `xs.push(3)` | `xs = append(xs, 3)` | `xs.append(3)` |
| Độ dài | `xs.length` | `len(xs)` | `len(xs)` |
| Lấy đoạn | `xs.slice(1, 3)` | `xs[1:3]` | `xs[1:3]` |
| Copy nông | `[...xs]` | `slices.Clone(xs)` (1.21+) | `xs.copy()` |
| Biến đổi phần tử | `xs.map(x => x * 2)` | `for` + `append` | `[x * 2 for x in xs]` |
| Lọc phần tử | `xs.filter(x => x > 0)` | `for` + `if` + `append` | `[x for x in xs if x > 0]` |
| Tổng hợp / tổng | `xs.reduce((a, b) => a + b, 0)` | `for _, x := range xs { total += x }` | `sum(xs)` |
| Sắp xếp số | `xs.sort((a, b) => a - b)` | `slices.Sort(xs)` | `sorted(xs)` / `xs.sort()` |
| Dictionary | `new Map([["a", 1]])` | `map[string]int{"a": 1}` | `{"a": 1}` |
| Đọc map | `m.get("a")`; `m.has("a")` | `v, ok := m["a"]` | `m.get("a")`; `"a" in m` |
| Xóa key | `m.delete("a")` | `delete(m, "a")` | `m.pop("a", None)` |
| Tập hợp | `new Set([1, 2])` | `map[int]struct{}{1: {}, 2: {}}` | `{1, 2}` |
| Hàm | `function add(a, b) { return a + b; }` | `func add(a, b int) int { return a + b }` | `def add(a, b): return a + b` |
| Nhiều kết quả | `return [value, error]` (quy ước) | `return value, err` | `return value, error` (tuple) |
| Số đối số biến đổi | `function f(...xs) { ... }` | `func f(xs ...int) { ... }` | `def f(*xs):` |
| Hàm ẩn danh | `x => x * 2` | `func(x int) int { return x * 2 }` | `lambda x: x * 2` |
| Đối số mặc định | `function f(x = 1) { ... }` | wrapper hoặc options | `def f(x=1):` |
| Tách giá trị | `const [a, b] = xs` | `a, b := xs[0], xs[1]` | `a, b = xs` |
| Đổi chỗ | `[a, b] = [b, a]` | `a, b = b, a` | `a, b = b, a` |
| Object / record | `{ name: "Ada" }` | `User{Name: "Ada"}` (struct) | `User(name="Ada")` (dataclass) |
| Lỗi | `throw new Error("bad")` | `return errors.New("bad")` | `raise ValueError("bad")` |
| Bắt / kiểm tra lỗi | `try { ... } catch (e) { ... }` | `if err != nil { ... }` | `try:` / `except ValueError as e:` |
| Dọn tài nguyên | `try { ... } finally { ... }` | `defer file.Close()` | `with open(...) as f:` |
| Import | `import { readFile } from "node:fs/promises"` | `import "os"` | `from pathlib import Path` |
| Export | `export function f() { ... }` | `func Exported() { ... }` (viết hoa) | tên trong module; `__all__` tùy chọn |
| Hàm async | `async function f() { await work(); }` | `go f()` + đồng bộ tường minh | `async def f(): await work()` |
| Byte | `Buffer.from("hi")` | `[]byte("hi")` | `b"hi"` |


## Ví dụ đầy đủ: collection và method

Chạy [Node](../examples/syntax/node/main.mjs), [Go](../examples/syntax/go/main.go), [Python](../examples/syntax/python/main.py). Ba file trả cùng 21 trường JSON, gồm map/filter/sum, lookup, copy, Unicode, số lớn, ngày UTC và file round trip. Xem [script kiểm tra](../scripts/check.py) để biết kết quả mong đợi.

```javascript
const xs = [1, 2, 3, 4];
const even = xs.filter(x => x % 2 === 0); // [2, 4]
const squared = xs.map(x => x * x);      // [1, 4, 9, 16]
```

```go
xs := []int{1, 2, 3, 4}
even := []int{}
for _, x := range xs {
    if x % 2 == 0 { even = append(even, x) }
}
```

```python
xs = [1, 2, 3, 4]
even = [x for x in xs if x % 2 == 0]
squared = [x * x for x in xs]
```

Go ưu tiên vòng lặp trực tiếp cho biến đổi slice đơn giản; không cần xây bộ helper functional chỉ để giống JavaScript. Python comprehension tạo list mới; generator expression dùng dấu ngoặc tròn phù hợp khi muốn duyệt lười.

## Những cú pháp trông giống nhưng nghĩa khác

| Trường hợp | Điều cần nhớ |
| --- | --- |
| `const` | JavaScript khóa binding, không đóng băng object; hằng Go là giá trị hằng tại compile time; tên viết hoa Python chỉ là quy ước. |
| Điều kiện | `[]` là truthy trong JavaScript, falsy trong Python; Go yêu cầu biểu thức boolean. |
| Equality | JavaScript dùng `===` tránh coercion, object so sánh identity; Python `==` thường so sánh giá trị, `is` so sánh identity. Go chỉ so sánh `==` với kiểu comparable; slice/map không so sánh trực tiếp với nhau. |
| Chia số nguyên âm | JS `Math.trunc(-3 / 2)` và Go `-3 / 2` (integer) cho `-1`; Python `-3 // 2` cho `-2`. Chọn quy tắc làm tròn tường minh. |
| Copy và slice | JS `slice()` và Python list slice tạo container mới; Go subslice dùng chung backing array. Copy nông vẫn chia sẻ object/pointer lồng nhau. |
| Sort | JS `sort()` mặc định theo chuỗi: `[10, 2]` có thể ra `[10, 2]`; truyền comparator số. Python `sorted()` tạo list mới, `list.sort()` sửa tại chỗ; Go `slices.Sort()` sửa slice. |
| Map | JS Map và Python dict giữ thứ tự insertion; Go map không bảo đảm thứ tự. Không dùng thứ tự map làm contract. |
| Default mutable | Python `def f(xs=[]):` tái dùng cùng list giữa lần gọi. Dùng `None` rồi tạo list trong hàm. |
| Null | Go zero value (`0`, `false`, `""`) không có nghĩa là thiếu. Dùng pointer hoặc type biểu diễn optional khi API cần phân biệt. |
| Pattern matching | Python `match` có destructuring/pattern; không chỉ là bản sao `switch`. Trong Go, case không tự fallthrough; JS thường cần `break`. |

## Kiểu tĩnh, type hint và validation

```typescript
// Chỉ là kiểm tra compile-time; dữ liệu HTTP vẫn cần validation runtime.
type User = { name: string };
const user: User = { name: "Ada" };
```

```go
type User struct { Name string }
func (u User) Greet() string { return "Hi, " + u.Name }
// Interface được đáp ứng ngầm thông qua method set, không cần 'implements'.
type Greeter interface { Greet() string }
```

```python
from dataclasses import dataclass
@dataclass
class User:
    name: str
    def greet(self) -> str:
        return f"Hi, {self.name}"
# dataclass và type hint không tự validate dữ liệu JSON đầu vào.
```

Go có generics cho kiểu/hàm tham số hóa nhưng method không tự khai báo type parameter mới. TypeScript generic bị xóa khi chuyển sang JS; Python annotation cần type checker như mypy/Pyright và validation riêng ở biên dữ liệu. Không đồng nhất “code có kiểu” với “request hợp lệ”.

Nguồn: [JavaScript guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide), [Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array), [Go spec](https://go.dev/ref/spec), [Effective Go](https://go.dev/doc/effective_go), [Python built-in types](https://docs.python.org/3.12/library/stdtypes.html), [Python functions](https://docs.python.org/3.12/tutorial/controlflow.html#defining-functions).
