import uvicorn
from core.config import settings
from core.logger import logger

def main():
    logger.info(f"Starting Ghost Pilot server at http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "api.app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
