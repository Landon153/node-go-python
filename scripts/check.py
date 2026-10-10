"""Cross-language contracts; run with the Python environment containing Uvicorn."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "greeting": "Hi, Ada", "even": [2, 4], "squared": [1, 4, 9, 16], "total": 10,
    "sorted": [1, 2, 10], "first_two": [1, 2], "original_first": 1, "copied_first": 99,
    "score": 9, "has_missing": False, "unique": [1, 2], "parsed": True,
    "parsed_integer": 42, "error": "division by zero", "regex": True,
    "hex": "6869", "codepoints": 4, "bytes": 6, "big_integer": "1152921504606846977",
    "date": "2024-01-02T03:04:05Z", "file_roundtrip": "hello",
}

def run(command):
    return subprocess.check_output(command, cwd=ROOT, text=True, timeout=60)

def check_programs():
    for language in ("node", "go", "python"):
        for topic in ("syntax", "concurrency"):
            folder = f"examples/{topic}/{language}"
            command = {"node": ["node", f"{folder}/main.mjs"],
                       "go": ["go", "run", f"./{folder}"],
                       "python": [sys.executable, f"{folder}/main.py"]}[language]
            result = json.loads(run(command))
            expected = EXPECTED if topic == "syntax" else {"values": [0, 2, 4, 6, 8, 10], "max_active": 2}
            assert result == expected, (topic, language, result)
            print(f"PASS {topic}/{language}")

def request(base, path, method="GET"):
    try:
        response = urllib.request.urlopen(urllib.request.Request(base + path, method=method), timeout=5)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        assert response.headers.get_content_type() == "application/json"
        return response.status, json.load(response), response.headers.get("Allow")

def check_server(command, name):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    env = {**os.environ, "PORT": str(port)}
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log, start_new_session=True)
        try:
            deadline = time.monotonic() + 15
            while True:
                if process.poll() is not None:
                    raise RuntimeError(f"{name} exited before startup")
                try:
                    assert request(base, "/health")[:2] == (200, {"ok": True})
                    break
                except (OSError, AssertionError):
                    if time.monotonic() >= deadline:
                        raise RuntimeError(f"{name} did not start")
                    time.sleep(0.05)
            cases = [
                ("/sum?a=2&b=3", 200, {"sum": 5}),
                ("/he%61lth", 200, {"ok": True}),
                ("/sum?a=-2&b=3", 200, {"sum": 1}),
                ("/sum?a=-1000000&b=1000000", 200, {"sum": 0}),
                ("/sum?a=1&a=2&b=3", 200, {"sum": 4}),
                ("/sum?ignored=x%3By&a=1&b=3", 200, {"sum": 4}),
                ("/wait", 200, {"waited_ms": 50}),
                ("/wait?ms=0", 200, {"waited_ms": 0}),
                ("/wait?ms=1000", 200, {"waited_ms": 1000}),
                ("/missing", 404, {"error": "not_found"}),
            ]
            for path in ("/sum", "/sum?a=2", "/sum?a=&b=1", "/sum?a=01&b=1",
                         "/sum?a=1.2&b=1", "/sum?a=NaN&b=1", "/sum?a=1e2&b=1",
                         "/sum?a=1000001&b=1", "/sum?a=%20&b=1", "/sum?a=1;x&a=2&b=3",
                         "/sum?ignored=x;y&a=1&b=3", "/sum?ignored=%GG&a=1&b=3", "/sum?a=%D9%A1&b=1",
                         "/wait?ms=", "/wait?ms=-1", "/wait?ms=1001"):
                cases.append((path, 400, {"error": "invalid_query"}))
            for path, status, data in cases:
                assert request(base, path)[:2] == (status, data), (name, path)
            for method in ("POST", "PUT", "DELETE", "OPTIONS"):
                assert request(base, "/health", method) == (405, {"error": "method_not_allowed"}, "GET")
            # Exercises overlapping requests. Intentionally no timing benchmark assertion.
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(lambda _: request(base, "/wait?ms=100")[:2], range(6)))
            assert results == [(200, {"waited_ms": 100})] * 6
            # Verify process shutdown drains an already in-flight response.
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                waiting = pool.submit(request, base, "/wait?ms=1000")
                time.sleep(0.2)  # Give the local server time to accept this request.
                os.killpg(process.pid, signal.SIGTERM)
                assert waiting.result(timeout=5)[:2] == (200, {"waited_ms": 1000}), name
                # Uvicorn may re-raise the captured SIGTERM after a clean drain.
                accepted = (0, -signal.SIGTERM) if name == "python" else (0,)
                assert process.wait(timeout=8) in accepted, name
            print(f"PASS server/{name}: {len(cases)} cases, 4 methods, 6 overlapping requests, graceful drain")
        except Exception:
            log.seek(0)
            print(log.read().decode(), file=sys.stderr)
            raise
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()

def check_docs():
    for path in [*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md")]:
        text = path.read_text()
        assert text.count("```") % 2 == 0, f"Unclosed fence: {path}"
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            local = target.split("#", 1)[0]
            assert (path.parent / local).exists(), f"Broken link: {path}: {target}"
    vi = {str(p.relative_to(ROOT / "docs")).replace(".vi.md", "") for p in (ROOT / "docs").rglob("*.vi.md")}
    en = {str(p.relative_to(ROOT / "docs")).replace(".en.md", "") for p in (ROOT / "docs").rglob("*.en.md")}
    assert vi == en and len(vi) == 13, (vi, en)
    # New guides share executable/illustrative code exactly across editions.
    for path in (ROOT / "docs" / "guides").glob("*.vi.md"):
        counterpart = path.with_name(path.name.replace(".vi.md", ".en.md"))
        fences = lambda p: re.findall(r"```[^\n]*\n(.*?)```", p.read_text(), re.S)
        assert fences(path) == fences(counterpart), f"Guide code parity: {path}"
    assert (ROOT / "README.md").read_text() == (ROOT / "README.vi.md").read_text()
    print("PASS documentation: links, fences, 13 bilingual pairs, guide code parity")

if __name__ == "__main__":
    check_docs()
    check_programs()
    with tempfile.TemporaryDirectory(prefix="node-go-python-check-") as directory:
        binary = str(Path(directory) / "go-server")
        subprocess.run(["go", "build", "-o", binary, "./examples/server/go"], cwd=ROOT, check=True, timeout=60)
        check_server(["node", "examples/server/node/main.mjs"], "node")
        check_server([binary], "go")
        check_server([sys.executable, "examples/server/python/main.py"], "python")
    print("All checks passed.")
