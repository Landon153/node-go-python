# Contributing

[VI](CONTRIBUTING.vi.md) · [EN](CONTRIBUTING.en.md)

- Update both `.vi.md` and `.en.md` with matching scope and examples.
- Use shared contracts for new runnable examples and distinguish illustrative snippets.
- Link primary sources beside claims; state versions for version-sensitive behavior.
- Performance/popularity claims need measurement methods; selection advice needs a workload.
- For code changes, run `python scripts/check.py` in an environment with Uvicorn, `go vet ./...`, and `go run -race ./examples/concurrency/go`.
- Do not commit API keys, private environments, model weights, or user data.

Format Go with gofmt. Keep demo dependencies small; catalog libraries do not need installation merely for illustration.
