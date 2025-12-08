from settings import BUTTON_KEYCODES
import time


def press_button(driver, button_name: str, hold_ms: int = 80):
    if button_name not in BUTTON_KEYCODES:
        raise ValueError(f"Unbekannter Button: {button_name}")

    keycode = BUTTON_KEYCODES[button_name]

    # JS für keyDown
    js_down = f"""
            if (window.globalScene && globalScene.inputController) {{
                globalScene.inputController.keyboardKeyDown({{ keyCode: {keycode} }});
            }}
        """

    # JS für keyUp
    js_up = f"""
            if (window.globalScene && globalScene.inputController) {{
                globalScene.inputController.keyboardKeyUp({{ keyCode: {keycode} }});
            }}
        """

    # Down senden
    driver.execute_script(js_down)

    # Kurze Haltezeit simulieren wie ein echter Tastendruck
    time.sleep(hold_ms / 1000.0)

    # Up senden
    driver.execute_script(js_up)

    time.sleep(0.1)
