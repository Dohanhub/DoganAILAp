# DoganAI Compliance Kit - Build Automation
# ===========================================

# Variables
PYTHON := python
PIP := python -m pip
PYTEST := python -m pytest
UVICORN := uvicorn
STREAMLIT := streamlit
RUFF := ruff
PORT_API := 8000
PORT_UI := 8501

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)DoganAI Compliance Kit - Build Automation$(RESET)"
	@echo "$(BLUE)===========================================$(RESET)"
	@echo ""
	@echo "$(YELLOW)Development Commands:$(RESET)"
	@echo "  $(GREEN)make dev$(RESET)          - Start development environment (API + UI)"
	@echo "  $(GREEN)make api$(RESET)          - Launch FastAPI server"
	@echo "  $(GREEN)make test$(RESET)         - Run test suite"
	@echo "  $(GREEN)make lint$(RESET)         - Run code linting"
	@echo "  $(GREEN)make install$(RESET)      - Install project in development mode"
	@echo ""
	@echo "$(YELLOW)Database Commands:$(RESET)"
	@echo "  $(GREEN)make up$(RESET)           - Start all infrastructure services"
	@echo "  $(GREEN)make down$(RESET)         - Stop all infrastructure services"
	@echo "  $(GREEN)make db-migrate$(RESET)   - Run database migrations"
	@echo "  $(GREEN)make psql$(RESET)         - Connect to PostgreSQL database"
	@echo "  $(GREEN)make seed$(RESET)         - Populate database with test data"
	@echo ""
	@echo "$(YELLOW)Quality & Testing:$(RESET)"
	@echo "  $(GREEN)make ci$(RESET)           - Run CI pipeline locally"
	@echo "  $(GREEN)make test-coverage$(RESET) - Run tests with coverage"
	@echo "  $(GREEN)make security-scan$(RESET) - Run security scan"
	@echo "  $(GREEN)make health$(RESET)       - Run comprehensive health check"
	@echo ""
	@echo "$(YELLOW)Build & Deploy:$(RESET)"
	@echo "  $(GREEN)make build$(RESET)        - Build project (clean, lint, test)"
	@echo "  $(GREEN)make docker-build$(RESET) - Build Docker image"
	@echo "  $(GREEN)make clean$(RESET)        - Clean build artifacts and containers"
	@echo ""
	@echo "$(YELLOW)For more commands, see the Makefile$(RESET)"

# ===========================================
# Development Environment
# ===========================================

.PHONY: install
install: ## Install project in development mode
	@echo "$(BLUE)Installing project in development mode...$(RESET)"
	$(PIP) install -e .
	@echo "$(GREEN)✅ Installation completed$(RESET)"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -e .
	$(PIP) install ruff pytest httpx pytest-asyncio
	@echo "$(GREEN)✅ Development dependencies installed$(RESET)"

# ===========================================
# Code Quality
# ===========================================

.PHONY: lint
lint: ## Run code linting with ruff
	@echo "$(BLUE)Running code linting...$(RESET)"
	$(RUFF) check src
	@echo "$(GREEN)✅ Linting completed$(RESET)"

.PHONY: lint-fix
lint-fix: ## Run code linting with automatic fixes
	@echo "$(BLUE)Running code linting with fixes...$(RESET)"
	$(RUFF) check src --fix
	@echo "$(GREEN)✅ Linting with fixes completed$(RESET)"

.PHONY: format
format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(RUFF) format src
	@echo "$(GREEN)✅ Code formatting completed$(RESET)"

# ===========================================
# Testing
# ===========================================

.PHONY: test
test: ## Run test suite
	@echo "$(BLUE)Running test suite...$(RESET)"
	$(PYTEST) -v
	@echo "$(GREEN)✅ Tests completed$(RESET)"

.PHONY: test-quick
test-quick: ## Run quick tests (excluding slow tests)
	@echo "$(BLUE)Running quick tests...$(RESET)"
	$(PYTEST) -v -m "not slow"
	@echo "$(GREEN)✅ Quick tests completed$(RESET)"

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTEST) --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated$(RESET)"

# ===========================================
# Application Services
# ===========================================

.PHONY: api
api: ## Launch FastAPI server
	@echo "$(BLUE)Starting FastAPI server on port $(PORT_API)...$(RESET)"
	@echo "$(YELLOW)API will be available at: http://localhost:$(PORT_API)$(RESET)"
	@echo "$(YELLOW)API docs will be available at: http://localhost:$(PORT_API)/docs$(RESET)"
	$(UVICORN) run:app --port $(PORT_API) --reload

.PHONY: ui
ui: ## Launch Streamlit UI
	@echo "$(BLUE)Starting Streamlit UI on port $(PORT_UI)...$(RESET)"
	@echo "$(YELLOW)UI will be available at: http://localhost:$(PORT_UI)$(RESET)"
	$(STREAMLIT) run ui/app.py --server.port $(PORT_UI)

.PHONY: dev
dev: ## Start development environment (API + UI)
	@echo "$(BLUE)Starting development environment...$(RESET)"
	@echo "$(YELLOW)API: http://localhost:$(PORT_API)$(RESET)"
	@echo "$(YELLOW)UI: http://localhost:$(PORT_UI)$(RESET)"
	@$(MAKE) api

# ===========================================
# Health and Monitoring
# ===========================================

.PHONY: health
health: ## Run comprehensive health check
	@echo "$(BLUE)Running comprehensive health check...$(RESET)"
	$(PYTHON) -c "from src.api.health import get_health_checker; import json; hc = get_health_checker(); print(json.dumps(hc.run_all_checks(), indent=2))"

.PHONY: security-scan
security-scan: ## Run security scan
	@echo "$(BLUE)Running security scan...$(RESET)"
	$(PIP) install bandit
	bandit -r src/
	@echo "$(GREEN)✅ Security scan completed$(RESET)"

# ===========================================
# Build and Deploy
# ===========================================

.PHONY: build
build: clean-python lint test ## Build project (clean, lint, test)
	@echo "$(BLUE)Building project...$(RESET)"
	$(PIP) install build
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Build completed$(RESET)"

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t doganai-compliance-kit:latest .
	@echo "$(GREEN)✅ Docker image built$(RESET)"

.PHONY: ci
ci: install-dev lint test ## Run CI pipeline locally
	@echo "$(GREEN)✅ CI pipeline completed successfully$(RESET)"

.PHONY: clean-python
clean-python: ## Clean Python build artifacts and cache
	@echo "$(BLUE)Cleaning Python artifacts...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)✅ Python cleanup completed$(RESET)"

# ===========================================
# Database Operations (Legacy)
# ===========================================

# Start infrastructure
.PHONY: up
up: ## Start all infrastructure services
	@echo "$(BLUE)Starting infrastructure services...$(RESET)"
	docker compose -f infra/docker-compose.yml up -d --build
	@echo "$(GREEN)✅ Infrastructure services started$(RESET)"

# Stop infrastructure
.PHONY: down
down: ## Stop all infrastructure services
	@echo "$(BLUE)Stopping infrastructure services...$(RESET)"
	docker compose -f infra/docker-compose.yml down
	@echo "$(GREEN)✅ Infrastructure services stopped$(RESET)"

# Run database migrations
.PHONY: migrate db-migrate
migrate db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(RESET)"
	docker compose -f infra/docker-compose.yml run --rm migrate -locations=filesystem:/flyway/sql migrate
	@echo "$(GREEN)✅ Database migrations completed$(RESET)"

# Connect to PostgreSQL
.PHONY: psql
psql: ## Connect to PostgreSQL database
	@echo "$(BLUE)Connecting to PostgreSQL database...$(RESET)"
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai

# Seed database with test data
.PHONY: seed
seed: ## Populate database with test data
	@echo "$(BLUE)Seeding database with test data...$(RESET)"
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai -f scripts/seed.sql
	@echo "$(GREEN)✅ Database seeded successfully$(RESET)"

# Run smoke tests
.PHONY: smoke
smoke: ## Run smoke tests to validate setup
	@echo "$(BLUE)Running smoke tests...$(RESET)"
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai -f scripts/smoke.sql
	@echo "$(GREEN)✅ Smoke tests completed$(RESET)"

# Clean up everything
.PHONY: clean
clean: clean-python ## Remove all containers, volumes, and build artifacts
	@echo "$(BLUE)Cleaning up Docker resources...$(RESET)"
	docker compose -f infra/docker-compose.yml down -v
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

# View service logs
.PHONY: logs
logs: ## View service logs
	@echo "$(BLUE)Viewing service logs...$(RESET)"
	docker compose -f infra/docker-compose.yml logs -f

# Check service status
.PHONY: status
status: ## Check service status
	@echo "$(BLUE)Checking service status...$(RESET)"
	docker compose -f infra/docker-compose.yml ps

# Create database backup
.PHONY: backup
backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(RESET)"
	@mkdir -p backups
	PGPASSWORD=postgres pg_dump -h 127.0.0.1 -U postgres -d doganai > backups/doganai_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup created in backups/ directory$(RESET)"

# Restore database from backup
.PHONY: restore
restore: ## Restore database from backup
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(YELLOW)Usage: make restore BACKUP_FILE=backups/filename.sql$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(BACKUP_FILE)...$(RESET)"
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai < $(BACKUP_FILE)
	@echo "$(GREEN)✅ Database restored successfully$(RESET)"

# Development shortcuts
.PHONY: dev-legacy
dev-legacy: up migrate seed ## Legacy dev command (use 'make dev' for new development environment)
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

# Production-like setup
.PHONY: prod
prod: up migrate ## Setup production-like environment
	@echo "$(GREEN)✅ Production environment ready!$(RESET)"

# Reset everything and start fresh
.PHONY: reset
reset: clean up migrate seed ## Reset everything and start fresh
	@echo "$(GREEN)✅ Fresh start completed!$(RESET)"

# Show database info
.PHONY: info
info: ## Show database information
	@echo "$(BLUE)Database Information:$(RESET)"
	@echo "$(BLUE)=====================$(RESET)"
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai -c "SELECT version();" -t
	@echo ""
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai -c "SELECT extname FROM pg_extension;" -t
	@echo ""
	PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d doganai -c "SELECT schemaname, tablename, n_tup_ins FROM pg_stat_user_tables ORDER BY tablename;" -t

# ===========================================
# Utility Script Aliases
# ===========================================

.PHONY: demo
demo: ## Run quick performance demo
	@echo "$(BLUE)Running quick performance demo...$(RESET)"
	$(PYTHON) quick_demo.py
	@echo "$(GREEN)✅ Demo completed$(RESET)"

.PHONY: warm-cache
warm-cache: ## Warm up application cache
	@echo "$(BLUE)Warming up cache...$(RESET)"
	$(PYTHON) cache_warmer.py
	@echo "$(GREEN)✅ Cache warmed$(RESET)"

.PHONY: shard-info
shard-info: ## Show shard routing information
	@echo "$(BLUE)Shard routing information:$(RESET)"
	$(PYTHON) -c "from shard_router import shard_router; print(f'Shard count: {shard_router.shard_count}'); print('Shard router ready')"

# Ensure all targets are marked as PHONY
.PHONY: help install install-dev lint lint-fix format test test-quick test-coverage
.PHONY: api ui dev health security-scan build docker-build ci clean-python
.PHONY: up down migrate db-migrate psql seed smoke clean logs status backup restore
.PHONY: dev-legacy prod reset info demo warm-cache shard-info
