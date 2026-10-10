# Đóng góp

[VI](CONTRIBUTING.vi.md) · [EN](CONTRIBUTING.en.md)

- Cập nhật cả `.vi.md` và `.en.md`, giữ cùng phạm vi và ví dụ.
- Viết ví dụ mới theo cùng contract. Phân biệt snippet minh họa với file chạy được.
- Ghi nguồn chính thức cạnh claim; ghi phiên bản khi behavior phụ thuộc version.
- Không đưa claim hiệu năng/phổ biến thiếu phương pháp đo; đánh giá lựa chọn cần nêu workload.
- Khi sửa code: chạy `python scripts/check.py` trong môi trường có Uvicorn, `go vet ./...` và `go run -race ./examples/concurrency/go`.
- Không commit API key, file môi trường riêng, model weight hoặc dữ liệu người dùng.

Ví dụ Go dùng gofmt. Giữ dependency demo nhỏ; thư viện trong catalog không cần cài vào repo chỉ để minh họa.
