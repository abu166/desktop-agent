import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import router
from core.logger import logger

def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="Ghost Pilot — Local Voice AI Desktop Agent",
        description="Local voice assistant using Gemini 2.5 Flash for desktop OS automation.",
        version="1.0.0"
    )

    # Mount web directory for static CSS and JS assets
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
    if os.path.exists(web_dir):
        app.mount("/static", StaticFiles(directory=web_dir), name="static")

    app.include_router(router)
    logger.info("FastAPI app initialized successfully.")
    return app

app = create_app()
