IMAGE_NAME=chimera-dev

.PHONY: setup test spec-check build

setup: build
	@echo "Setup complete (image built)."

build:
	docker build -t $(IMAGE_NAME) .

test: build
	docker run --rm -v "$(PWD):/app" -w /app $(IMAGE_NAME) pytest -q

spec-check:
	python scripts/spec_check.py
