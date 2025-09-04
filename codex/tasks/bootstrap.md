# Bootstrap Task

Task: Stand up the full local stack.

Steps:
1) Run `make bootstrap`.
2) Run `make up`.
3) Wait for health: `make health`.
4) If health fails, tail logs and surface the first failing container with exact errors.

Expected outcome: All services running and healthy.
