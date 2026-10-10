# Node.js · Go · Python

[Tiếng Việt](README.vi.md) · [English](README.en.md)

So sánh cú pháp bằng ví dụ, cơ chế hoạt động server và hệ sinh thái web/backend/validation/AI. Hai bản tài liệu có cùng cấu trúc chương.

| Chương | Nội dung |
| --- | --- |
| 01 | [Nền tảng và cách đọc](docs/01-foundations.vi.md) |
| 02 | [So sánh cú pháp](docs/02-syntax.vi.md) |
| 03 | [Dữ liệu, I/O và xử lý lỗi](docs/03-data-and-errors.vi.md) |
| 04 | [Server hoạt động như thế nào](docs/04-server-runtime.vi.md) |
| 05 | [Ba server cùng một API](docs/05-server-examples.vi.md) |
| 06 | [Thư viện và hệ sinh thái](docs/06-ecosystem.vi.md) |
| 07 | [AI, ML và nền tảng phục vụ mô hình](docs/07-ai-platforms.vi.md) |
| 08 | [Chọn stack, đo hiệu năng và chuyển đổi](docs/08-choosing-a-stack.vi.md) |

## Hướng dẫn chuyên sâu

| Hướng dẫn | Nội dung |
| --- | --- |
| [Node stacks](docs/guides/node-stacks.vi.md) | Web/UI, validation, SQL/ORM, cache/job, tests, observability, AI và 3 recipe |
| [Go stacks](docs/guides/go-stacks.vi.md) | HTTP/router, DTO, pgx/sqlc/GORM, migration, RPC/job, tests và 3 recipe |
| [Python backend](docs/guides/python-backend.vi.md) | FastAPI/Django/Flask, ASGI/WSGI, Pydantic, DB, HTTP pooling, Celery và 4 recipe |
| [Python data](docs/guides/python-data.vi.md) | 12 công cụ numerical/tabular/analytics/distributed/viz và lab offline |
| [Python AI/ML](docs/guides/python-ai-ml.vi.md) | 31 công cụ classical ML, deep learning, NLP/CV/audio/time series, RAG/serving và MLOps |

Mỗi profile nêu công dụng, tình huống, ví dụ/kết quả, đánh đổi và docs official. [Chương 4](docs/04-server-runtime.vi.md) có luồng request cho từng runtime/framework và phân tích I/O, CPU, pool, cancellation, backpressure.

## Có gì trong repo?

- 44 tác vụ cú pháp đối chiếu Node/Go/Python và các khác biệt semantics.
- 10 chương trình chạy được: syntax, concurrency, HTTP server và lab Python data/ML.
- Catalogue đối chiếu cùng profile thư viện chi tiết và recipe stack hoàn chỉnh.
- 8 chương + 5 hướng dẫn chuyên sâu × 2 ngôn ngữ, nguồn chính thức và GitHub Actions.

## Chạy nhanh

Cần Node 24, Go ≥1.22 và Python ≥3.12. Clone repo và chạy trên Linux/macOS hoặc WSL:

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

[Chương 5](docs/05-server-examples.vi.md) có lệnh chạy ba server, endpoint contract và mô hình Python nhiều worker. Demo dùng loopback, không cần database/API key và không đưa ra kết luận benchmark.

## Nguồn, phiên bản và đóng góp

Tham khảo cách trình bày của [Miguel Mota](https://github.com/miguelmota/golang-for-nodejs-developers); code và nội dung ở đây được viết mới. Nguồn/đánh giá kiểm tra ngày 10/10/2026. Danh sách “thường gặp” không phải bảng xếp hạng đo lường. Xem [phạm vi](docs/01-foundations.vi.md), [đóng góp](CONTRIBUTING.vi.md) và [MIT License](LICENSE).

[Lab data offline](docs/guides/python-data.vi.md) tùy chọn có environment và requirements riêng. Snippet framework/model trong guide là minh họa; CI kiểm tra chương trình đầy đủ thay vì mọi integration tùy chọn.
