run: build
	@docker run --rm --tty --interactive xypath

build:
	@docker build --tag xypath .

lint:
	@uv run ruff format --check .
	@uv run ruff check .

fix:
	@uv run ruff format .
	@uv run ruff check --fix .

check:
	@uv run pytest
	@$(MAKE) lint

.PHONY: run build lint fix check
