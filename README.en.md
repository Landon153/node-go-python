# Node.js · Go · Python

[Tiếng Việt](README.vi.md) · [English](README.en.md)

Compare syntax through examples, server execution models, and web/backend/validation/AI ecosystems. Both editions share the same chapter structure.

| Chapter | Contents |
| --- | --- |
| 01 | [Foundations and reading guide](docs/01-foundations.en.md) |
| 02 | [Syntax comparison](docs/02-syntax.en.md) |
| 03 | [Data, I/O and errors](docs/03-data-and-errors.en.md) |
| 04 | [How servers execute](docs/04-server-runtime.en.md) |
| 05 | [Three servers, one API](docs/05-server-examples.en.md) |
| 06 | [Libraries and ecosystems](docs/06-ecosystem.en.md) |
| 07 | [AI, ML and model serving](docs/07-ai-platforms.en.md) |
| 08 | [Stack selection, measurement and migration](docs/08-choosing-a-stack.en.md) |

## Detailed guides

| Guide | Coverage |
| --- | --- |
| [Node stacks](docs/guides/node-stacks.en.md) | Web/UI, validation, SQL/ORM, caches/jobs, tests, observability, AI, and 3 recipes |
| [Go stacks](docs/guides/go-stacks.en.md) | HTTP/routers, DTOs, pgx/sqlc/GORM, migrations, RPC/jobs, tests, and 3 recipes |
| [Python backend](docs/guides/python-backend.en.md) | FastAPI/Django/Flask, ASGI/WSGI, Pydantic, DBs, HTTP pools, Celery, and 4 recipes |
| [Python data](docs/guides/python-data.en.md) | 12 numerical/tabular/analytics/distributed/visualization tools and an offline lab |
| [Python AI/ML](docs/guides/python-ai-ml.en.md) | 31 classical ML, deep learning, NLP/CV/audio/time-series, RAG/serving, and MLOps tools |

Profiles explain purpose, scenarios, examples/results, tradeoffs, and official docs. [Chapter 4](docs/04-server-runtime.en.md) diagrams request flows and explains I/O, CPU, pools, cancellation, and backpressure.

## What is included?

- 44 side-by-side syntax tasks and semantic differences.
- 10 runnable programs: syntax, concurrency, HTTP servers, and a Python data/ML lab.
- Core comparison catalogue plus detailed library profiles and complete stack recipes.
- 8 chapters + 5 detailed guides × 2 languages, official sources, and GitHub Actions checks.

## Quick start

Requires Node 24, Go ≥1.22, and Python ≥3.12. Clone and run on Linux/macOS or WSL:

```sh
git clone https://github.com/Landon153/node-go-python.git
cd node-go-python
python3 -m venv .venv
.venv/bin/python -m pip install -r examples/server/python/requirements.txt
.venv/bin/python scripts/check.py
```

```sh
node examples/syntax/node/main.mjs
go run ./examples/syntax/go
.venv/bin/python examples/syntax/python/main.py
```

[Chapter 5](docs/05-server-examples.en.md) covers server commands, endpoint contracts, and Python workers. Demos bind loopback, require no database/API keys, and make no benchmark claims.

## Sources, versions, and contributions

Inspired by [Miguel Mota's comparison format](https://github.com/miguelmota/golang-for-nodejs-developers); code/content here are newly written. Sources/assessments checked on 2026-10-10. The representative shortlist is not a measured popularity ranking. See [scope](docs/01-foundations.en.md), [contributing](CONTRIBUTING.en.md), and [MIT License](LICENSE).

The optional [offline data lab](docs/guides/python-data.en.md) has a separate environment and dependency file. Framework/model snippets in guides are illustrative; CI checks the complete programs rather than every optional integration.
