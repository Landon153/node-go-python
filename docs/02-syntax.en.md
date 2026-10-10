# 02. Syntax comparison

[README](../README.en.md) · [VI](./02-syntax.vi.md) · [EN](./02-syntax.en.md)

## Quick reference

| Task | Node.js / JavaScript | Go | Python |
| --- | --- | --- | --- |
| Comment | `// note`, `/* note */` | `// note`, `/* note */` | `# note` |
| Output | `console.log("hi")` | `fmt.Println("hi")` | `print("hi")` |
| Variable | `let count = 1` | `count := 1` | `count = 1` |
| Constant | `const LIMIT = 10` | `const Limit = 10` | `LIMIT = 10` (convention) |
| Boolean | `true`, `false` | `true`, `false` | `True`, `False` |
| Missing / null | `undefined`, `null` | `nil` (nullable types) | `None` |
| Type inspection | `typeof x`; `Array.isArray(x)` | `fmt.Printf("%T", x)` | `type(x)`, `isinstance(x, int)` |
| Interpolation | `` `Hi, ${name}` `` | `fmt.Sprintf("Hi, %s", name)` | `f"Hi, {name}"` |
| Conversion | `Number("42")` | `strconv.Atoi("42")` → `(int, error)` | `int("42")` → `ValueError` on failure |
| Conditional | `if (x > 0) { ... } else { ... }` | `if x > 0 { ... } else { ... }` | `if x > 0:` / `else:` |
| Conditional value | `ok ? "yes" : "no"` | `if` + assignment | `"yes" if ok else "no"` |
| Counting loop | `for (let i = 0; i < 3; i++) { ... }` | `for i := 0; i < 3; i++ { ... }` | `for i in range(3):` |
| While loop | `while (ok) { ... }` | `for ok { ... }` | `while ok:` |
| Iteration | `for (const x of xs) { ... }` | `for _, x := range xs { ... }` | `for x in xs:` |
| Index and value | `for (const [i, x] of xs.entries()) { ... }` | `for i, x := range xs { ... }` | `for i, x in enumerate(xs):` |
| Branching | `switch (x) { case 1: break; }` | `switch x { case 1: ... }` | `match x:` / `case 1:` (3.10+) |
| Sequence | `const xs = [1, 2]` | `xs := []int{1, 2}` (slice) | `xs = [1, 2]` |
| Append | `xs.push(3)` | `xs = append(xs, 3)` | `xs.append(3)` |
| Length | `xs.length` | `len(xs)` | `len(xs)` |
| Slice | `xs.slice(1, 3)` | `xs[1:3]` | `xs[1:3]` |
| Shallow copy | `[...xs]` | `slices.Clone(xs)` (1.21+) | `xs.copy()` |
| Map transform | `xs.map(x => x * 2)` | `for` + `append` | `[x * 2 for x in xs]` |
| Filter | `xs.filter(x => x > 0)` | `for` + `if` + `append` | `[x for x in xs if x > 0]` |
| Reduce / sum | `xs.reduce((a, b) => a + b, 0)` | `for _, x := range xs { total += x }` | `sum(xs)` |
| Numeric sort | `xs.sort((a, b) => a - b)` | `slices.Sort(xs)` | `sorted(xs)` / `xs.sort()` |
| Dictionary | `new Map([["a", 1]])` | `map[string]int{"a": 1}` | `{"a": 1}` |
| Map lookup | `m.get("a")`; `m.has("a")` | `v, ok := m["a"]` | `m.get("a")`; `"a" in m` |
| Delete key | `m.delete("a")` | `delete(m, "a")` | `m.pop("a", None)` |
| Set | `new Set([1, 2])` | `map[int]struct{}{1: {}, 2: {}}` | `{1, 2}` |
| Function | `function add(a, b) { return a + b; }` | `func add(a, b int) int { return a + b }` | `def add(a, b): return a + b` |
| Multiple results | `return [value, error]` (convention) | `return value, err` | `return value, error` (tuple) |
| Variadic arguments | `function f(...xs) { ... }` | `func f(xs ...int) { ... }` | `def f(*xs):` |
| Anonymous function | `x => x * 2` | `func(x int) int { return x * 2 }` | `lambda x: x * 2` |
| Default argument | `function f(x = 1) { ... }` | explicit wrapper/options | `def f(x=1):` |
| Unpack / destructure | `const [a, b] = xs` | `a, b := xs[0], xs[1]` | `a, b = xs` |
| Swap | `[a, b] = [b, a]` | `a, b = b, a` | `a, b = b, a` |
| Object / record | `{ name: "Ada" }` | `User{Name: "Ada"}` (struct) | `User(name="Ada")` (dataclass) |
| Error | `throw new Error("bad")` | `return errors.New("bad")` | `raise ValueError("bad")` |
| Catch / inspect error | `try { ... } catch (e) { ... }` | `if err != nil { ... }` | `try:` / `except ValueError as e:` |
| Cleanup | `try { ... } finally { ... }` | `defer file.Close()` | `with open(...) as f:` |
| Import | `import { readFile } from "node:fs/promises"` | `import "os"` | `from pathlib import Path` |
| Export | `export function f() { ... }` | `func Exported() { ... }` (capitalized) | module names; `__all__` optional |
| Async function | `async function f() { await work(); }` | `go f()` + explicit coordination | `async def f(): await work()` |
| Bytes | `Buffer.from("hi")` | `[]byte("hi")` | `b"hi"` |


## Complete examples: collections and methods

Run [Node](../examples/syntax/node/main.mjs), [Go](../examples/syntax/go/main.go), and [Python](../examples/syntax/python/main.py). They return the same 21 JSON fields covering map/filter/sum, lookup, copying, Unicode, large integers, UTC dates, and a file round trip. The [check script](../scripts/check.py) defines the expected results.

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

Go commonly uses direct loops for simple slice transformations; there is no need to build functional helpers solely to resemble JavaScript. Python comprehensions create a list; a parenthesized generator expression is useful for lazy iteration.

## Similar appearance, different meaning

| Case | What to remember |
| --- | --- |
| `const` | JavaScript fixes the binding, not the object's contents; Go constants are compile-time constant values; uppercase Python names are conventions. |
| Conditions | `[]` is truthy in JavaScript and falsy in Python; Go requires a boolean expression. |
| Equality | JavaScript `===` avoids coercion and compares objects by identity; Python `==` usually compares values and `is` checks identity. Go `==` requires comparable types; slices/maps cannot be compared directly with each other. |
| Negative integer division | JS `Math.trunc(-3 / 2)` and Go integer `-3 / 2` produce `-1`; Python `-3 // 2` produces `-2`. Choose rounding rules explicitly. |
| Copying and slicing | JS `slice()` and Python list slicing create containers; Go subslices share a backing array. Shallow copies still share nested objects/pointers. |
| Sorting | JS defaults to string ordering: `[10, 2]` may remain `[10, 2]`; provide a numeric comparator. Python `sorted()` creates a list and `list.sort()` mutates; Go `slices.Sort()` mutates the slice. |
| Maps | JS Map and Python dict preserve insertion order; Go map iteration has no guaranteed order. Do not make map iteration order part of a contract. |
| Mutable defaults | Python `def f(xs=[]):` reuses one list across calls. Use `None` and create a list inside the function. |
| Nullability | Go zero values (`0`, `false`, `""`) do not mean missing. Use pointers or an explicit optional representation when an API needs the distinction. |
| Pattern matching | Python `match` includes structural patterns, rather than being a direct switch equivalent. Go cases do not fall through automatically; JS usually needs `break`. |

## Static types, hints, and validation

```typescript
// Compile-time checks only; HTTP input still needs runtime validation.
type User = { name: string };
const user: User = { name: "Ada" };
```

```go
type User struct { Name string }
func (u User) Greet() string { return "Hi, " + u.Name }
// Interfaces are satisfied implicitly by method sets; no 'implements' keyword.
type Greeter interface { Greet() string }
```

```python
from dataclasses import dataclass
@dataclass
class User:
    name: str
    def greet(self) -> str:
        return f"Hi, {self.name}"
# A dataclass and type hints do not validate incoming JSON automatically.
```

Go supports parameterized types/functions, but methods cannot declare fresh type parameters of their own. TypeScript generics disappear when converted to JS; Python annotations need a checker such as mypy/Pyright and separate boundary validation. Typed code and valid requests are separate properties.

Sources: [JavaScript guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide), [Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array), [Go spec](https://go.dev/ref/spec), [Effective Go](https://go.dev/doc/effective_go), [Python built-in types](https://docs.python.org/3.12/library/stdtypes.html), [Python functions](https://docs.python.org/3.12/tutorial/controlflow.html#defining-functions).
