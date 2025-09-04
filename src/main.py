"""
Application entrypoint adopting the app-factory pattern.

All application configuration and routes are defined in
`src/core/app.py:create_app`. This file only bootstraps the ASGI app
object for servers and provides a simple dev runner.
"""

from src.core.app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    # Local/dev run. Containers use gunicorn (see Dockerfile).
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

