.PHONY: help install install-dev test test-cov lint format type-check clean run docker-build docker-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=utils --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 utils/ app.py tests/ --max-line-length=100 --exclude=venv,__pycache__
	black --check utils/ app.py tests/

format: ## Format code with black and isort
	black utils/ app.py tests/
	isort utils/ app.py tests/

type-check: ## Run type checking with mypy
	mypy utils/ --ignore-missing-imports

clean: ## Clean cache and build artifacts
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov/ coverage.xml
	rm -rf dist/ build/

run: ## Run the Streamlit application
	streamlit run app.py

docker-build: ## Build Docker image
	docker build -t healthclaim-analytics-hub .

docker-run: ## Run Docker container
	docker run -p 8501:8501 --env-file .env healthclaim-analytics-hub

docker-compose-up: ## Start services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop docker-compose services
	docker-compose down

all-checks: lint type-check test ## Run all code quality checks
