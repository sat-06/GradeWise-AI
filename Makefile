.PHONY: help dev-backend dev-frontend install seed train test lint format migrate clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

seed: ## Generate and load synthetic data
	cd backend && python -m app.ml.data.synthetic_generator

train: ## Train ML models on synthetic data
	cd backend && python -m app.ml.models.train

test: ## Run all tests
	cd backend && pytest -v --cov=app

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit -v

test-integration: ## Run integration tests
	cd backend && pytest tests/integration -v

lint: ## Lint all code
	cd backend && ruff check app/
	cd frontend && npm run lint

format: ## Format all code
	cd backend && black app/ && ruff check --fix app/

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create msg="description")
	cd backend && alembic revision --autogenerate -m "$(msg)"

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules
