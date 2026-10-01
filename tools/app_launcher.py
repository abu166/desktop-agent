import sys
import subprocess
import time
from core.logger import logger

MACOS_APP_ALIASES = {
    "заметки": "Notes",
    "калькулятор": "Calculator",
    "терминал": "Terminal",
    "сафари": "Safari",
    "хром": "Google Chrome",
    "chrome": "Google Chrome",
    "настройки": "System Settings",
    "календарь": "Calendar",
    "просмотр": "Preview",
    "консоль": "Terminal",
    "блокнот": "TextEdit",
    "ноутс": "Notes",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "finder": "Finder",
}

def open_application(app_name: str) -> str:
    """Open a desktop application by name on the user's operating system (optimized for macOS).

    Args:
        app_name: Name of the application to launch (e.g. 'Calculator', 'Notes', 'Safari', 'TextEdit', 'Terminal', 'Google Chrome').
    """
    logger.info(f"Tool 'open_application' executed with app_name='{app_name}'")
    try:
        platform = sys.platform
        target_app = app_name.strip()
        
        if platform == "darwin":
            resolved_app = MACOS_APP_ALIASES.get(target_app.lower(), target_app)
            subprocess.Popen(["open", "-a", resolved_app])
            target_app = resolved_app
        elif platform == "win32":
            subprocess.Popen(f'start "" "{target_app}"', shell=True)
        else:
            try:
                subprocess.Popen([target_app])
            except FileNotFoundError:
                subprocess.Popen(["xdg-open", target_app])

        # Mandatory UI delay to allow application window to load and gain focus
        time.sleep(0.5)
        msg = f"Successfully launched application '{app_name}'."
        logger.info(msg)
        return msg
    except Exception as e:
        err_msg = f"Failed to launch application '{app_name}': {str(e)}"
        logger.error(err_msg)
        return err_msg
