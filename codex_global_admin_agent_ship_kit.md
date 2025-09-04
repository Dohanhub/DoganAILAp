# Codex Global Admin Agent — Ship Kit

**Goal:** Give Codex (the admin agent) end‑to‑end authority to build, test, package, deploy, and operate the app locally and in CI/CD with minimal human taps.

---

## 0) Repo Layout (drop-in)
```
/ (repo root)
├─ .github/workflows/deploy.yml
├─ Makefile
├─ docker-compose.yml
├─ .env.example
├─ codex/
│  ├─ agent.yml
│  ├─ tasks/
│  │  ├─ bootstrap.md
│  │  ├─ build_push.md
│  │  ├─ migrate_seed.md
│  │  ├─ deploy_k8s.md
│  │  └─ ops_runbooks.md
│  └─ prompts/
│     └─ policy.md
├─ k8s/
│  ├─ namespace.yaml
│  ├─ deployment.yaml
│  ├─ service.yaml
│  ├─ ingress.yaml
│  └─ hpa.yaml
└─ scripts/
   ├─ bootstrap.sh
   ├─ wait_for.sh
   └─ healthcheck.sh
```

---

## 1) Makefile — single entrypoint UX
> One command per lifecycle. Keeps humans out of yak‑shaving.
```makefile
SHELL := /usr/bin/env bash
.ONESHELL:

# Load env if present
ifneq (,$(wildcard .env))
  include .env
  export $(shell sed -n 's/=.*//p' .env)
endif

APP?=your-app
REGISTRY?=$(DOCKER_REGISTRY)
TAG?=$(shell git rev-parse --short HEAD)
IMAGE?=$(REGISTRY)/$(APP):$(TAG)

.PHONY: bootstrap build push up logs down test migrate seed lint fmt login release kube-apply kube-rollback health

bootstrap:
	@./scripts/bootstrap.sh

build:
	docker build -t $(IMAGE) .

push: login
	docker push $(IMAGE)

login:
	echo $$DOCKER_PASSWORD | docker login $${DOCKER_REGISTRY%%/*} -u $$DOCKER_USERNAME --password-stdin

up:
	docker compose up -d --build

logs:
	docker compose logs -f --tail=200

down:
	docker compose down -v

migrate:
	docker compose exec api npm run migrate || true

seed:
	docker compose exec api npm run seed || true

health:
	./scripts/healthcheck.sh http://localhost:$(PORT)

kube-apply:
	kubectl apply -f k8s/namespace.yaml
	sed "s#{{IMAGE}}#$(IMAGE)#g" k8s/deployment.yaml | kubectl apply -f -
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/ingress.yaml
	kubectl apply -f k8s/hpa.yaml

kube-rollback:
	kubectl rollout undo deploy/$(APP) -n $(K8S_NAMESPACE)

release: build push kube-apply
```

---

## 2) docker-compose.yml — full local stack
```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: ${DB_USER:-app}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-app}
      POSTGRES_DB: ${DB_NAME:-app}
    ports: ["${DB_PORT:-5432}:5432"]
    volumes:
      - dbdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER"]
      interval: 5s
      timeout: 5s
      retries: 20

  redis:
    image: redis:7
    ports: ["${REDIS_PORT:-6379}:6379"]

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    env_file: .env
    environment:
      DATABASE_URL: ${DATABASE_URL:-postgresql://${DB_USER:-app}:${DB_PASSWORD:-app}@db:5432/${DB_NAME:-app}}
      REDIS_URL: ${REDIS_URL:-redis://redis:6379}
      NODE_ENV: ${NODE_ENV:-development}
    ports: ["${PORT:-3000}:3000"]
    command: ["npm","run","start"]

volumes:
  dbdata:
```

---

## 3) .env.example — enforce config contract
```dotenv
# Registry (for CI/CD)
DOCKER_REGISTRY=ghcr.io/your-org
DOCKER_USERNAME=__set_in_ci_only__
DOCKER_PASSWORD=__set_in_ci_only__

# App
PORT=3000
JWT_SECRET=replace_me

# DB
DB_USER=app
DB_PASSWORD=app
DB_NAME=app
DB_PORT=5432
DATABASE_URL=postgresql://app:app@db:5432/app

# Redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379

# Kubernetes
K8S_NAMESPACE=prod
```

---

## 4) GitHub Actions — deploy.yml (secrets‑aware)
```yaml
name: CI/CD
on:
  push:
    branches: [ main ]
  workflow_dispatch: {}

env:
  APP: your-app

jobs:
  build-push-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.DOCKER_REGISTRY }}
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_REGISTRY }}/your-app:${{ github.sha }}

      - name: Configure kubectl (optional)
        if: ${{ secrets.KUBECONFIG != '' }}
        run: |
          echo "$KUBECONFIG_B64" | base64 -d > $HOME/.kube/config
          kubectl config set-context --current --namespace=${{ vars.K8S_NAMESPACE || 'prod' }}
        env:
          KUBECONFIG_B64: ${{ secrets.KUBECONFIG }}

      - name: Deploy (kubectl)
        if: ${{ secrets.KUBECONFIG != '' }}
        run: |
          IMAGE=${{ secrets.DOCKER_REGISTRY }}/your-app:${{ github.sha }}
          sed "s#{{IMAGE}}#$$IMAGE#g" k8s/deployment.yaml | kubectl apply -f -
          kubectl apply -f k8s/service.yaml
          kubectl apply -f k8s/ingress.yaml
          kubectl rollout status deploy/your-app -n ${{ vars.K8S_NAMESPACE || 'prod' }}
```

---

## 5) Kubernetes Manifests (minimal but production‑leaning)
**k8s/namespace.yaml**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ${K8S_NAMESPACE}
```

**k8s/deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-app
  namespace: ${K8S_NAMESPACE}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: your-app
  template:
    metadata:
      labels:
        app: your-app
    spec:
      containers:
        - name: api
          image: {{IMAGE}}
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: app-secrets, key: DATABASE_URL }
            - name: REDIS_URL
              valueFrom:
                secretKeyRef: { name: app-secrets, key: REDIS_URL }
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef: { name: app-secrets, key: JWT_SECRET }
          readinessProbe:
            httpGet: { path: /health, port: 3000 }
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /health, port: 3000 }
            initialDelaySeconds: 10
            periodSeconds: 10
```

**k8s/service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: your-app
  namespace: ${K8S_NAMESPACE}
spec:
  type: ClusterIP
  selector:
    app: your-app
  ports:
    - port: 80
      targetPort: 3000
```

**k8s/ingress.yaml**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: your-app
  namespace: ${K8S_NAMESPACE}
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: your-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: your-app
                port: { number: 80 }
```

**k8s/hpa.yaml**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: your-app
  namespace: ${K8S_NAMESPACE}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: your-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 6) scripts/
**scripts/bootstrap.sh**
```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo ".env created. Edit secrets before running prod flows." >&2
fi

# Node example — swap for your stack
if command -v npm >/dev/null 2>&1; then
  npm ci || npm install
fi

docker version >/dev/null 2>&1 || { echo "Docker not running"; exit 1; }

echo "Bootstrap complete. Run: make up && make migrate && make seed && make health"
```

**scripts/wait_for.sh**
```bash
#!/usr/bin/env bash
set -euo pipefail
URL="$1"
for i in {1..60}; do
  if curl -fsS "$URL" >/dev/null; then exit 0; fi
  sleep 2
done
exit 1
```

**scripts/healthcheck.sh**
```bash
#!/usr/bin/env bash
set -euo pipefail
URL="$1"; curl -fsS "$URL/health" && echo OK || (echo FAIL; exit 1)
```

---

## 7) Codex Agent Definition (admin persona)
**codex/agent.yml**
```yaml
name: Codex Global Admin
role: platform-admin
objectives:
  - Build, test, and run the app locally via Makefile targets.
  - Package and publish container images to the configured registry.
  - Deploy to Kubernetes using k8s manifests and report rollout.
  - Run migrations and seeds safely (idempotent).
  - Perform basic SRE checks (health, logs, rollout status) and propose fixes.

capabilities:
  - shell
  - docker
  - kubectl
  - github-actions: trigger, read logs

inputs:
  env:
    - DOCKER_REGISTRY (secret)
    - DOCKER_USERNAME (secret)
    - DOCKER_PASSWORD (secret)
    - KUBECONFIG (secret, base64)
    - K8S_NAMESPACE (var)

routines:
  bootstrap: ["make bootstrap", "make up", "make migrate", "make seed", "make health"]
  ci_cd: ["make build", "make push"]
  deploy: ["make kube-apply", "kubectl get pods -n $K8S_NAMESPACE", "kubectl rollout status deploy/your-app -n $K8S_NAMESPACE"]
  rollback: ["make kube-rollback"]
  logs: ["docker compose logs -f --tail=200"]
```

**codex/tasks/bootstrap.md** (example prompt for the agent)
```
Task: Stand up the full local stack.
Steps:
1) Run `make bootstrap`.
2) Run `make up`.
3) Wait for health: `make health`.
4) If health fails, tail logs and surface the first failing container with exact errors.
```

---

## 8) Ops Runbook — the 90% path
- **Local dev:** `make bootstrap && make up && make logs`
- **DB migrate:** `make migrate`
- **Seed data:** `make seed`
- **Build & push image:** `make build push`
- **Deploy to k8s:** `make release` (build+push+apply)
- **Rollback:** `make kube-rollback`
- **Health:** `make health`

**CI Secrets to create (GitHub → Settings → Secrets and variables → Actions):**
- `DOCKER_REGISTRY`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `KUBECONFIG`

**Optional Variables (Actions → Variables):**
- `K8S_NAMESPACE` (defaults to `prod`)

---

## 9) Guardrails & Policy (codex/prompts/policy.md)
- Never echo secret values in logs.
- Diff infra changes before applying when possible.
- If migrations fail, abort deploy and suggest rollback.
- Enforce health gates: rollout must reach Ready or fail fast with logs.
- Only tag images with immutable SHAs in CI.
```

