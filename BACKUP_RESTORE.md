Backup and Restore Plan

Database (PostgreSQL)
- Managed service preferred (RDS/CloudSQL/Aurora) with automated backups, PITR enabled.
- Self-managed: use PGBackRest with retention: 14d full + WAL archiving; verify backups daily; test restore monthly.

Object Storage (Evidence/Uploads)
- Prefer S3 bucket with versioning, lifecycle policy (e.g., 365d retention), and SSE encryption.

Helm/Kubernetes
- Back up Helm release manifests (helm get values/manifests) and cluster state via GitOps.

Restore Procedures
- DB: provision new instance, restore snapshot/WAL to desired point, update DATABASE_URL secret, rolling restart API.
- Files: restore required object keys; validate checksums.

Runbooks
- Document RPO/RTO targets; practice DR in staging at least twice per year.

