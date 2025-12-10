from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import keyboard
import json
import time
 #from Environment.send_key_inputs import press_button


def setup_driver():
    """Launches browser and injects save/settings."""
    print("--- Launching PokeRogue Environment ---")
    # Headless (optional)
    options = Options()
    # options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    driver.get("http://localhost:8000")

    settings = {"PLAYER_GENDER":0,"gameVersion":"1.11.3","MASTER_VOLUME":0,"LANGUAGE":0,"GAME_SPEED":7,"HP_BAR_SPEED":3,"EXP_GAINS_SPEED":3,"EXP_PARTY_DISPLAY":2,"SKIP_SEEN_DIALOGUES":1,"EGG_SKIP":2,"HIDE_IVS":1,"TUTORIALS":0,"VIBRATION":1,"MOVE_ANIMATIONS":0,"SHOW_LEVEL_UP_STATS":0,"SHOW_ARENA_FLYOUT":0,"SHOW_MOVESET_FLYOUT":0,"TIME_OF_DAY_ANIMATION":1,"TYPE_HINTS":1,"SHOW_BGM_BAR":0,"SHOP_OVERLAY_OPACITY":8,"ENABLE_RETRIES":0}

    driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
    driver.refresh()

    # Load save data (file should be in DataExtraction folder or current working directory)
    try:
        with open("DataExtraction/copied_save_data.txt", "r") as f:
            file_content = f.read()
        driver.execute_script(f"localStorage.setItem('data_Guest', '{file_content}');")
        print("Save data injected.")
    except FileNotFoundError:
        print("Warning: copied_save_data.txt not found. Starting with clean save.")
    
    time.sleep(1)
    driver.refresh()
    time.sleep(8)

    from selenium.webdriver.support.ui import WebDriverWait
    WebDriverWait(driver, timeout=10).until(
        lambda d: d.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
    )
    return driver


if __name__ == "__main__":
    driver = setup_driver()
    while True:
        if keyboard.is_pressed('p'):
            print(driver.execute_script("return window.__GLOBAL_SCENE_DATA__();"))
            break
        if keyboard.is_pressed('q'):
            #press_button(driver, "SPACE")
            break

    print(driver.execute_script("return globalScene.phaseManager"))
