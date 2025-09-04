# Operations Runbooks

## Local Development
- **Start stack:** `make bootstrap && make up && make logs`
- **DB migrate:** `make migrate`
- **Seed data:** `make seed`
- **Health check:** `make health`

## Production Operations
- **Build & push image:** `make build push`
- **Deploy to k8s:** `make release` (build+push+apply)
- **Rollback:** `make kube-rollback`
- **Health check:** `make health`
- **View logs:** `make logs`

## Troubleshooting
- **Service not starting:** Check Docker logs with `make logs`
- **Database issues:** Verify DATABASE_URL in .env
- **Kubernetes issues:** Check pod status and events
- **Health check failing:** Verify application endpoints
