# Backup & Disaster Recovery Plan (Draft)

Scope
- PostgreSQL backups (full + WAL)
- Object store backups (S3-compatible)
- Configuration/state for services

Backups
- Daily full logical backup: `pg_dump -Fc` of `doganai`
- Hourly WAL archiving for point-in-time recovery
- Retention: 7 days (hourly), 30 days (daily), 6 months (weekly)
- Storage: S3 bucket with lifecycle policies and encryption (SSE-S3 or KMS)

Restores
- PITR via `pg_restore` with WAL replay
- Verified quarterly restore drills into staging environment

Automation
- GitHub Actions nightly workflow or cronjob in ops host
- Alerts on backup failures (email/Slack)

Validation
- Checksums + restore tests to validate backup integrity

