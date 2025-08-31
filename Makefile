.DEFAULT_GOAL := help
.PHONY: help test migration build up down clean-db

# Colors for output  
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RESET := \033[0m

# Project configuration
DOCKER_COMPOSE := docker-compose
APP_SERVICE := fireflow-app

help: ## Display this help message
	@echo "$(BLUE)FireFlow Makefile Commands$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

test: ## Run tests
	@echo "$(BLUE)Running tests...$(RESET)"
	uv run pytest -v
	@echo "$(GREEN)✓ Tests completed$(RESET)"

migration: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(RESET)"
	$(DOCKER_COMPOSE) exec -T $(APP_SERVICE) sh -c "cd /app && uv run alembic upgrade head"
	@echo "$(GREEN)✓ Migrations applied$(RESET)"

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(RESET)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Images built successfully$(RESET)"

up: ## Start all services
	@echo "$(BLUE)Starting FireFlow application...$(RESET)"
	$(DOCKER_COMPOSE) up --build -d
	@echo "$(GREEN)✓ Application started$(RESET)"
	@echo "$(GREEN)🌐 App: http://localhost:5000$(RESET)"
	@echo "$(GREEN)📚 API Docs: http://localhost:5000/apidocs/$(RESET)"
	@echo "$(GREEN)🌸 Flower: http://localhost:5555$(RESET)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping application...$(RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Application stopped$(RESET)"

clean-db: ## Remove database file and recreate it
	@echo "$(YELLOW)Cleaning up database...$(RESET)"
	$(DOCKER_COMPOSE) down
	@if [ -d "data/fireflow.db" ]; then \
		echo "$(BLUE)Removing incorrectly created database directory...$(RESET)"; \
		sudo rm -rf data/fireflow.db 2>/dev/null || true; \
	fi
	@if [ -f "data/fireflow.db" ]; then \
		echo "$(BLUE)Removing existing database file...$(RESET)"; \
		rm -f data/fireflow.db; \
	fi
	@echo "$(BLUE)Creating empty database file...$(RESET)"
	@mkdir -p data
	@touch data/fireflow.db
	@echo "$(GREEN)✓ Database cleaned$(RESET)"