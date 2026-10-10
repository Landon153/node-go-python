# 01. Foundations and reading guide

[README](../README.en.md) · [VI](./01-foundations.vi.md) · [EN](./01-foundations.en.md)

## Goal

This guide helps someone who knows one language read and write the other two. Node.js is a JavaScript runtime; Go and Python are languages. Server comparisons use ordinary GIL-enabled CPython and JavaScript ESM on Node. TypeScript appears when discussing types and ecosystem choices.

The side-by-side task format is inspired by Miguel Mota's [golang-for-nodejs-developers](https://github.com/miguelmota/golang-for-nodejs-developers). This repository contains newly written examples and adds Python, server execution models, and ecosystem assessments. The reference project's older API examples are not treated as current-version guidance.

## Keep the layers separate

| Layer | Node.js | Go | Python |
| --- | --- | --- | --- |
| Language | JavaScript; TypeScript adds development-time type checking | Go, static types | Python, dynamic types; optional type hints |
| Runtime | V8 + libuv + Node APIs | Scheduler, GC and networking runtime | CPython; `asyncio` provides an event loop library |
| HTTP server | `node:http` or a framework-created server | `net/http.Server` | Uvicorn/Hypercorn for ASGI; Gunicorn with an appropriate worker model |
| Framework | Express, Fastify, NestJS | chi, Gin, Echo, Fiber | FastAPI, Starlette, Django, Flask |
| Tooling | npm/pnpm, `package.json` | `go.mod`, Go toolchain | pip/uv, virtualenv, `pyproject.toml` |

A framework does not inherently replace its runtime's execution model. NestJS still uses Node, FastAPI still needs an ASGI server, and Go still needs resource limits despite having goroutines.

## Version scope

Examples target Node 24, Go 1.22 or newer, and Python 3.12 or newer. Initial checks run on Node 24.14.0, Go 1.26.5, and CPython 3.12.4; CI uses Node 24 / Go 1.26.x / Python 3.12. `go.mod` retains 1.22 because the code needs only that baseline; the declared language version also affects some runtime compatibility defaults. Python dependencies are recorded in requirements.

Sources and library assessments were checked on **2026-10-10**. “Commonly encountered” means a representative shortlist for different needs, not a download-based or survey-based popularity ranking. Strengths and limitations are engineering judgments about simplicity, integration, and operating cost. Check releases, licenses, and toolchain requirements before selecting production dependencies.

## Reading path

1. Chapters 2–3: syntax, collections, types, JSON, errors, and I/O.
2. Chapter 4: event loops, goroutines, the GIL, WSGI/ASGI, and workers.
3. Chapter 5: run three servers and check their shared contract.
4. Chapters 6–7: libraries, AI applications, and model serving.
5. Chapter 8: architecture selection, workload measurement, and migration pitfalls.

Syntax table cells are fragments that require an appropriate surrounding context. Files under `examples/` are complete runnable programs. The checks need no cloud account, database, or API key.

## Foundation sources

[Node documentation](https://nodejs.org/api/), [Go specification](https://go.dev/ref/spec), [Python tutorial](https://docs.python.org/3.12/tutorial/), [TypeScript handbook](https://www.typescriptlang.org/docs/handbook/intro.html).
