Secrets Rotation Guide

Scope
- Rotate JWT_SECRET/SECRET_KEY, API_KEY, DB_PASSWORD across GitHub, Kubernetes, and Helm values.

GitHub Secrets (per repo)
- Using GitHub CLI:
  - gh secret set DOCKER_PASSWORD --body "<value>"
  - gh secret set KUBE_CONFIG_STAGING --body "<base64-kubeconfig>"
  - gh secret set KUBE_CONFIG_PROD --body "<base64-kubeconfig>"
- Add environment-scoped secrets (staging, production) for:
  - SECRET_KEY, API_KEY, DATABASE_URL, DB_PASSWORD

Kubernetes Secrets (via Helm set values)
- Use Helm values or --set to supply required secrets:
  - env.api.SECRET_KEY, env.api.API_KEY, env.api.DATABASE_URL
- Example:
  - helm upgrade --install doganai deploy/helm/doganai -n doganai \
    --set env.api.SECRET_KEY=$(openssl rand -hex 32) \
    --set env.api.API_KEY=$(openssl rand -hex 24) \
    --set env.api.DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/db"

Database Credentials
- Prefer managed secret stores (AWS Secrets Manager/Azure Key Vault/GCP Secret Manager).
- Update application DATABASE_URL after rotation and perform rolling restart.

Revocation & Audit
- After rotation, invalidate old tokens/keys and check audit logs for anomalous access.

