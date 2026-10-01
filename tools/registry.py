from tools.app_launcher import open_application
from tools.keyboard import paste_text, press_hotkey
from tools.browser import open_url_in_browser

# List of executable python tools passed to the Gemini LLM SDK
ALL_TOOLS = [
    open_application,
    paste_text,
    press_hotkey,
    open_url_in_browser,
]

# Mapping from tool function names to callables
TOOL_MAP = {func.__name__: func for func in ALL_TOOLS}
