# Codex Agent Policy and Guardrails

## Security
- Never echo secret values in logs
- Always use environment variables for sensitive data
- Validate all inputs before processing

## Deployment Safety
- Diff infra changes before applying when possible
- If migrations fail, abort deploy and suggest rollback
- Enforce health gates: rollout must reach Ready or fail fast with logs
- Only tag images with immutable SHAs in CI

## Monitoring
- Always check health endpoints after deployment
- Monitor logs for errors and warnings
- Verify all services are running before considering deployment successful

## Rollback Procedures
- Keep previous deployment available for quick rollback
- Test rollback procedures regularly
- Document rollback steps for each deployment
