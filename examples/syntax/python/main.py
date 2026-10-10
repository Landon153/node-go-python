import json
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass
class User:
    name: str
    def greet(self) -> str:
        return f"Hi, {self.name}"

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b

xs = [1, 2, 3, 4]
copy = xs.copy()
copy[0] = 99
scores = {"Ada": 9}
try:
    divide(1, 0)
except ValueError as exc:
    error = str(exc)
with tempfile.TemporaryDirectory(prefix="node-go-python-") as directory:
    path = Path(directory) / "hello.txt"
    path.write_text("hello", encoding="utf-8")
    file = path.read_text(encoding="utf-8")
print(json.dumps({
    "greeting": User("Ada").greet(), "even": [x for x in xs if x % 2 == 0],
    "squared": [x * x for x in xs], "total": sum(xs),
    "sorted": sorted([10, 2, 1]), "first_two": xs[:2],
    "original_first": xs[0], "copied_first": copy[0], "score": scores["Ada"],
    "has_missing": "Bob" in scores, "unique": list(dict.fromkeys([1, 1, 2])),
    "parsed": json.loads('{"active":true}')["active"], "parsed_integer": int("42"),
    "error": error, "regex": re.fullmatch(r"[a-z]+", "hello") is not None,
    "hex": b"hi".hex(), "codepoints": len("Việt"), "bytes": len("Việt".encode("utf-8")),
    "big_integer": str(2**60 + 1),
    "date": datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    "file_roundtrip": file,
}))
