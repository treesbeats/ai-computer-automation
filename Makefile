.PHONY: help install install-dev test lint format clean docs

help:
	@echo "Available commands:"
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make test         Run tests with coverage"
	@echo "  make lint         Run linting checks"
	@echo "  make format       Format code with black and isort"
	@echo "  make clean        Remove build artifacts and cache files"
	@echo "  make docs         Build documentation"
	@echo "  make pre-commit   Install pre-commit hooks"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest --cov=ai_automation --cov-report=term-missing --cov-report=html

test-verbose:
	pytest -v --cov=ai_automation --cov-report=term-missing

lint:
	flake8 src/ tests/
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/ examples/
	isort src/ tests/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && make html

pre-commit:
	pre-commit install
	pre-commit run --all-files

build:
	python -m build

publish-test:
	python -m build
	twine upload --repository testpypi dist/*

publish:
	python -m build
	twine upload dist/*
