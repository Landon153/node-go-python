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

## Có gì trong repo?

- 44 tác vụ cú pháp đối chiếu Node/Go/Python và các khác biệt semantics.
- 9 chương trình chạy được: syntax, concurrency và HTTP server cho mỗi ngôn ngữ.
- 52 công cụ chính được đánh giá, thêm nhóm cache/queue/auth/migration/tooling và nền tảng AI.
- 8 chương × 2 ngôn ngữ, nguồn chính thức và GitHub Actions kiểm tra ví dụ.

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
