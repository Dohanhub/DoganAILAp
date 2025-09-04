# Security Policy

## Supported Versions
We aim to maintain the `main` branch as secure and up to date. For tagged releases, apply latest patches or rebuild containers with updated dependencies.

## Reporting a Vulnerability
If you discover a security issue:
- Do not open a public issue with sensitive details.
- Email: security@dogan.ai
- Include: description, affected versions/paths, reproduction steps, impact.
- We acknowledge within 72 hours and coordinate a fix timeline.

## Best Practices in This Repo
- `.env.example` provided; do not commit actual `.env`.
- Dependencies pinned in `requirements*.txt`.
- CORS configured in `engine/api.py` via `engine/settings.py`.
- Docker Compose uses healthchecks and `restart: unless-stopped`.

## Hardening Recommendations
- Run containers as non-root in production images (future Dockerfiles).
- Use a reverse proxy (Nginx/Traefik) with TLS termination.
- Use network firewalls/security groups to limit Postgres exposure.
- Enable Dependabot/GitHub security updates.
