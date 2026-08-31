.PHONY: install run debug clean lint lint-strict

CONFIG ?= config.json

install:
	uv sync

run:
	uv run python3 pac-man.py $(CONFIG)

debug:
	uv run python3 -m pdb pac-man.py $(CONFIG)

clean:
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache .coverage htmlcov

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs
