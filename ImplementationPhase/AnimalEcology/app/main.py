import logging

from fastapi import FastAPI

from .api import router
from .db import init_db


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(
        title="ConfigAdminAPI Slice",
        version="0.1.0",
        description="Minimal ConfigAdminAPI implementation for AOIs, thresholds, and model configs.",
    )

    @app.on_event("startup")
    async def _startup() -> None:
        init_db()
        logging.getLogger(__name__).info("Database initialized")

    app.include_router(router)
    return app


app = create_app()
