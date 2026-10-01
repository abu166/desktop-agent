import webbrowser
import time
from core.logger import logger

def open_url_in_browser(url: str) -> str:
    """Open a website URL in the user's default web browser.

    Args:
        url: Web address to open (e.g. 'https://google.com', 'youtube.com', 'github.com').
    """
    logger.info(f"Tool 'open_url_in_browser' executed with url='{url}'")
    try:
        target_url = url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        webbrowser.open(target_url)
        time.sleep(0.5)
        msg = f"Successfully opened URL '{target_url}' in default browser."
        logger.info(msg)
        return msg
    except Exception as e:
        err_msg = f"Failed to open URL '{url}': {str(e)}"
        logger.error(err_msg)
        return err_msg
