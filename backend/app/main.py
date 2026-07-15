"""GradeWise AI - FastAPI Application Factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    alerts,
    analytics,
    auth,
    knowledge,
    monitoring,
    predictions,
    recommendations,
    whatif,
)
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        description="AI-Powered Decision Support System for Predictive Basis Weight Control",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.API_V1_PREFIX
    app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    app.include_router(monitoring.router, prefix=f"{api_prefix}/monitoring", tags=["Live Monitoring"])
    app.include_router(predictions.router, prefix=f"{api_prefix}/predictions", tags=["AI Predictions"])
    app.include_router(recommendations.router, prefix=f"{api_prefix}/recommendations", tags=["Recommendations"])
    app.include_router(whatif.router, prefix=f"{api_prefix}/whatif", tags=["What-If Simulator"])
    app.include_router(analytics.router, prefix=f"{api_prefix}/analytics", tags=["Analytics"])
    app.include_router(knowledge.router, prefix=f"{api_prefix}/knowledge", tags=["Knowledge Base"])
    app.include_router(alerts.router, prefix=f"{api_prefix}/alerts", tags=["Alerts"])

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    return app


app = create_app()
