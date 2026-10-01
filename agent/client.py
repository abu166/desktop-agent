from google import genai
from core.config import settings
from core.logger import logger

def get_genai_client() -> genai.Client:
    """Initialize and return the official google-genai Client."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("GEMINI_API_KEY is not set or using placeholder in config/environment.")
    
    return genai.Client(api_key=api_key)
