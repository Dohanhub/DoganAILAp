from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from src.api.v1 import api_router
from src.core.config import settings
from src.core.middleware import add_cors_middleware
from src.core.exception_handlers import http_exception_handler, validation_exception_handler

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Set up CORS and other middleware
    app = add_cors_middleware(app)
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    @app.get("/")
    async def root():
        return {"message": f"Welcome to {settings.PROJECT_NAME}"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app
