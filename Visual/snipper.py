import os
import keyboard
import pyautogui
import time


def screenshot_ingame():
    """Take a screenshot of the ingame screen when F10 is pressed."""

    screenshot_folder = "Screenshots\\InGame"
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    print("Press F10 to take a screenshot of the ingame screen. Press ESC to exit.")
    screenshot_counter = 0

    while True:
        if keyboard.is_pressed('f10'):
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(screenshot_folder, f"InGame_{screenshot_counter}.png")
            screenshot.save(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            screenshot_counter += 1
            time.sleep(1)  # Prevent multiple screenshots on a single press
        elif keyboard.is_pressed('esc'):
            print("Exiting screenshot mode.")
            break


if __name__ == "__main__":
    screenshot_ingame()
