import sys
import time
import pyautogui
import pyperclip
from core.logger import logger

# Enable PyAutoGUI failsafe mechanism
pyautogui.FAILSAFE = True

def paste_text(text: str) -> str:
    """Safely paste text into the currently active system window using the system clipboard.
    Supports non-ASCII text, Cyrillic, symbols, and multi-line strings without layout corruption.

    Args:
        text: The string content to paste into the focused input field.
    """
    logger.info(f"Tool 'paste_text' executed (character count: {len(text)})")
    try:
        pyperclip.copy(text)
        time.sleep(0.1)

        if sys.platform == "darwin":
            pyautogui.hotkey("command", "v")
        else:
            pyautogui.hotkey("ctrl", "v")

        time.sleep(0.2)
        msg = f"Successfully pasted text ({len(text)} chars) into active window."
        logger.info(msg)
        return msg
    except Exception as e:
        err_msg = f"Failed to paste text: {str(e)}"
        logger.error(err_msg)
        return err_msg

def press_hotkey(keys: str) -> str:
    """Press a key shortcut combination or single key on the keyboard.

    Args:
        keys: Key combination string (e.g. 'enter', 'escape', 'tab', 'command+v', 'ctrl+v', 'command+space', 'ctrl+t', 'ctrl+w', 'alt+tab').
    """
    logger.info(f"Tool 'press_hotkey' executed with keys='{keys}'")
    try:
        # Split on plus signs, commas, or spaces
        raw_parts = [k.strip().lower() for k in keys.replace("+", " ").replace(",", " ").split() if k.strip()]

        normalized_keys = []
        for key in raw_parts:
            if key in ("cmd", "command", "apple"):
                normalized_keys.append("command" if sys.platform == "darwin" else "ctrl")
            elif key in ("ctrl", "control"):
                normalized_keys.append("ctrl")
            elif key in ("win", "windows", "super", "meta"):
                normalized_keys.append("win")
            elif key in ("alt", "option"):
                normalized_keys.append("option" if sys.platform == "darwin" else "alt")
            elif key in ("return", "enter"):
                normalized_keys.append("enter")
            elif key in ("esc", "escape"):
                normalized_keys.append("escape")
            elif key in ("space", "spacebar"):
                normalized_keys.append("space")
            else:
                normalized_keys.append(key)

        if len(normalized_keys) == 1:
            pyautogui.press(normalized_keys[0])
        elif len(normalized_keys) > 1:
            pyautogui.hotkey(*normalized_keys)
        else:
            return "No valid keys specified for press_hotkey."

        time.sleep(0.2)
        msg = f"Successfully pressed hotkey combination: '{' + '.join(normalized_keys)}'."
        logger.info(msg)
        return msg
    except Exception as e:
        err_msg = f"Failed to press hotkey '{keys}': {str(e)}"
        logger.error(err_msg)
        return err_msg
