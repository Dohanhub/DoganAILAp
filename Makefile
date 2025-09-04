SHELL := /usr/bin/env bash
.ONESHELL:

# Load env if present
ifneq (,$(wildcard .env))
  include .env
  export $(shell sed -n 's/=.*//p' .env)
endif

# Project configuration
APP?=doganai-compliance-kit
REGISTRY?=ghcr.io/doganai
REGISTRY?=$(DOCKER_REGISTRY)
TAG?=$(shell git rev-parse --short HEAD)
IMAGE?=$(REGISTRY)/$(APP):$(TAG)

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

.PHONY: help bootstrap build push up logs down test migrate seed lint fmt login release kube-apply kube-rollback health install install-dev security clean

help: ## Show this help message
	@echo "$(BLUE)DoganAI Compliance Kit - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

bootstrap: ## Initialize development environment
	@echo "$(BLUE)Bootstrapping development environment...$(NC)"
	@./scripts/bootstrap.sh
	@echo "$(GREEN)Bootstrap complete!$(NC)"

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)Production dependencies installed!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -r requirements-dev.txt
	pip install -e .
	@if [ -f "package.json" ]; then \
		echo "$(BLUE)Installing Node.js dependencies...$(NC)"; \
		pnpm install; \
	fi
	@echo "$(GREEN)Development environment ready!$(NC)"

build: ## Build Docker image
	@echo "$(BLUE)Building Docker image: $(IMAGE)$(NC)"
	docker build -t $(IMAGE) .
	@echo "$(GREEN)Docker image built!$(NC)"

push: login ## Push Docker image to registry
	@echo "$(BLUE)Pushing Docker image: $(IMAGE)$(NC)"
	docker push $(IMAGE)
	@echo "$(GREEN)Docker image pushed!$(NC)"

login: ## Login to Docker registry
	@echo "$(BLUE)Logging into Docker registry...$(NC)"
	echo $$DOCKER_PASSWORD | docker login $${DOCKER_REGISTRY%%/*} -u $$DOCKER_USERNAME --password-stdin

up: ## Start development environment with Docker Compose
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker compose up -d --build
	@echo "$(GREEN)Development environment started!$(NC)"

logs: ## View Docker Compose logs
	@echo "$(BLUE)Viewing logs...$(NC)"
	docker compose logs -f --tail=200

down: ## Stop development environment
	@echo "$(BLUE)Stopping development environment...$(NC)"
	docker compose down -v
	@echo "$(GREEN)Development environment stopped!$(NC)"

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker compose exec api python -m alembic upgrade head || true
	@echo "$(GREEN)Database migrations complete!$(NC)"

seed: ## Seed database with initial data
	@echo "$(BLUE)Seeding database...$(NC)"
	docker compose exec api python -c "from app.init_db import init_db; init_db()" || true
	@echo "$(GREEN)Database seeded!$(NC)"

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	./scripts/healthcheck.sh http://localhost:$(PORT)

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	python -m pytest tests/ -v --cov=app --cov=backend --cov=src --cov-report=term-missing
	@echo "$(GREEN)Tests complete!$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	python -m pytest tests/ -v -m "unit" --cov=app --cov=backend --cov=src

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	python -m pytest tests/ -v -m "integration"

test-security: ## Run security tests
	@echo "$(BLUE)Running security tests...$(NC)"
	python -m pytest tests/ -v -m "security"

lint: ## Run linters and code quality checks
	@echo "$(BLUE)Running linters...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	black . --check
	isort . --check-only
	ruff check .
	mypy .
	@echo "$(GREEN)Linting complete!$(NC)"

fmt: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	black .
	isort .
	ruff format .
	@echo "$(GREEN)Code formatting complete!$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r . -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	pip-audit --format=json --output=pip-audit-report.json || true
	@echo "$(GREEN)Security checks complete! Check *-report.json files for details.$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -f *-report.json
	@echo "$(GREEN)Cleanup complete!$(NC)"

kube-apply: ## Apply Kubernetes configurations
	@echo "$(BLUE)Applying Kubernetes configurations...$(NC)"
	kubectl apply -f k8s/namespace.yaml
	sed "s#{{IMAGE}}#$(IMAGE)#g" k8s/deployment.yaml | kubectl apply -f -
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/ingress.yaml
	kubectl apply -f k8s/hpa.yaml
	@echo "$(GREEN)Kubernetes deployment complete!$(NC)"

kube-rollback: ## Rollback Kubernetes deployment
	@echo "$(BLUE)Rolling back Kubernetes deployment...$(NC)"
	kubectl rollout undo deploy/$(APP) -n $(K8S_NAMESPACE)
	@echo "$(GREEN)Rollback complete!$(NC)"

kube-status: ## Check Kubernetes deployment status
	@echo "$(BLUE)Checking Kubernetes status...$(NC)"
	kubectl get pods -n $(K8S_NAMESPACE)
	kubectl get services -n $(K8S_NAMESPACE)

kube-logs: ## View Kubernetes logs
	@echo "$(BLUE)Viewing Kubernetes logs...$(NC)"
	kubectl logs -f deployment/$(APP) -n $(K8S_NAMESPACE)

release: build push kube-apply ## Full release pipeline

ci: lint test security ## Run all CI checks
	@echo "$(GREEN)All CI checks passed!$(NC)"

dev: ## Start development server locally
	@echo "$(BLUE)Starting development server...$(NC)"
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@if [ -f "package.json" ]; then \
		echo "$(BLUE)Starting frontend development server...$(NC)"; \
		pnpm run dev; \
	else \
		echo "$(YELLOW)No package.json found, skipping frontend dev server$(NC)"; \
	fi

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt
	pip install --upgrade -r requirements-dev.txt
	@if [ -f "package.json" ]; then \
		echo "$(BLUE)Updating Node.js dependencies...$(NC)"; \
		pnpm update; \
	fi
	@echo "$(GREEN)Dependencies updated!$(NC)"

# Docker targets
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image: $(IMAGE)$(NC)"
	docker build -t $(IMAGE) .
	@echo "$(GREEN)Docker image built!$(NC)"

docker-build-no-cache: ## Build Docker image without cache
	@echo "$(BLUE)Building Docker image without cache: $(IMAGE)$(NC)"
	docker build --no-cache -t $(IMAGE) .
	@echo "$(GREEN)Docker image built!$(NC)"

docker-run: ## Run Docker container locally
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run --env-file .env.template -p 8000:8000 $(IMAGE)

docker-run-detached: ## Run Docker container in background
	@echo "$(BLUE)Running Docker container in background...$(NC)"
	docker run -d --name doganai-compliance-kit --env-file .env.template -p 8000:8000 $(IMAGE)
	@echo "$(GREEN)Container started! Access at http://localhost:8000$(NC)"

docker-stop: ## Stop running Docker container
	@echo "$(BLUE)Stopping Docker container...$(NC)"
	docker stop doganai-compliance-kit || true
	docker rm doganai-compliance-kit || true
	@echo "$(GREEN)Container stopped!$(NC)"

docker-logs: ## View Docker container logs
	@echo "$(BLUE)Viewing Docker container logs...$(NC)"
	docker logs -f doganai-compliance-kit

docker-shell: ## Open shell in running container
	@echo "$(BLUE)Opening shell in container...$(NC)"
	docker exec -it doganai-compliance-kit /bin/bash

# Docker Compose targets
compose-up: ## Start services with docker-compose
	@echo "$(BLUE)Starting services with docker-compose...$(NC)"
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)Creating .env from template...$(NC)"; \
		cp .env.template .env; \
	fi
	docker-compose -f docker-compose.production.yml up -d
	@echo "$(GREEN)Services started! App: http://localhost:8000$(NC)"

compose-up-monitoring: ## Start services with monitoring stack
	@echo "$(BLUE)Starting services with monitoring...$(NC)"
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)Creating .env from template...$(NC)"; \
		cp .env.template .env; \
	fi
	docker-compose -f docker-compose.production.yml --profile monitoring up -d
	@echo "$(GREEN)Services with monitoring started!$(NC)"
	@echo "$(BLUE)App: http://localhost:8000$(NC)"
	@echo "$(BLUE)Grafana: http://localhost:3000 (admin/admin)$(NC)"
	@echo "$(BLUE)Prometheus: http://localhost:9090$(NC)"

compose-down: ## Stop docker-compose services
	@echo "$(BLUE)Stopping docker-compose services...$(NC)"
	docker-compose -f docker-compose.production.yml down
	@echo "$(GREEN)Services stopped!$(NC)"

compose-logs: ## View docker-compose logs
	@echo "$(BLUE)Viewing docker-compose logs...$(NC)"
	docker-compose -f docker-compose.production.yml logs -f

compose-ps: ## Show docker-compose service status
	@echo "$(BLUE)Docker-compose service status:$(NC)"
	docker-compose -f docker-compose.production.yml ps

compose-restart: ## Restart docker-compose services
	@echo "$(BLUE)Restarting docker-compose services...$(NC)"
	$(MAKE) compose-down
	$(MAKE) compose-up
	@echo "$(GREEN)Services restarted!$(NC)"

# Database targets in Docker
docker-migrate: ## Run database migrations in Docker
	@echo "$(BLUE)Running database migrations in Docker...$(NC)"
	docker-compose -f docker-compose.production.yml exec app alembic upgrade head
	@echo "$(GREEN)Database migrations complete!$(NC)"

docker-db-backup: ## Backup database from Docker
	@echo "$(BLUE)Creating database backup...$(NC)"
	@BACKUP_FILE="backup_$$(date +%Y%m%d_%H%M%S).sql"; \
	docker-compose -f docker-compose.production.yml exec -T db pg_dump -U postgres compliance_kit > "$$BACKUP_FILE"; \
	echo "$(GREEN)Database backup created: $$BACKUP_FILE$(NC)"

# Docker cleanup targets
docker-clean: ## Clean Docker containers and images
	@echo "$(BLUE)Cleaning Docker containers and images...$(NC)"
	docker-compose -f docker-compose.production.yml down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Docker cleanup complete!$(NC)"

docker-clean-all: ## Clean all Docker resources including volumes
	@echo "$(RED)WARNING: This will remove all Docker volumes and data!$(NC)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose -f docker-compose.production.yml down -v --rmi all; \
		docker system prune -a -f --volumes; \
		echo "$(GREEN)All Docker resources cleaned!$(NC)"; \
	else \
		echo "$(YELLOW)Docker cleanup cancelled.$(NC)"; \
	fi

# Combined targets for easy use
docker-dev: docker-build compose-up ## Build and start development environment
	@echo "$(GREEN)Development environment ready!$(NC)"

docker-prod: docker-build compose-up-monitoring ## Build and start production environment with monitoring
	@echo "$(GREEN)Production environment ready!$(NC)"

# Docker health check
docker-health: ## Check health of Docker services
	@echo "$(BLUE)Checking Docker service health...$(NC)"
	@if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then \
		echo "$(GREEN)Services are running$(NC)"; \
		docker-compose -f docker-compose.production.yml exec app curl -s http://localhost:8000/health || echo "$(YELLOW)Health check failed$(NC)"; \
	else \
		echo "$(RED)Services are not running$(NC)"; \
	fi
