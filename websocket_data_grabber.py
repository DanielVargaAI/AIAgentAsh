from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import keyboard
import json
import example_save
import time

# Headless (optional)
options = Options()
# options.headless = True

driver = webdriver.Firefox(options=options)
driver.get("http://localhost:8000")

print("timer start")
# wait 5 seconds for the page to load
time.sleep(30)

settings = {"PLAYER_GENDER": 0, "GAME_SPEED": 7, "MASTER_VOLUME": 0, "TUTORIALS": 0, "ENABLE_RETRIES": 1, "SHOW_LEVEL_UP_STATS": 0, "EXP_GAINS_SPEED": 3, "EXP_PARTY_DISPLAY": 1, "HP_BAR_SPEED": 2, "gameVersion": "1.11.3"}
save_data = example_save.save_data  # TODO hier den Save-Daten-String einfügen (localStorage.data_Guest)

driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
driver.execute_script(f"localStorage.setItem('data_Guest', '{save_data}');")
print("Save data and settings injected.")
# driver.refresh()

while True:
    if keyboard.is_pressed("p"):
        print(driver.execute_script("return window.__GLOBAL_SCENE_DATA__();"))
    if keyboard.is_pressed("q"):
        break
    if keyboard.is_pressed("l"):
        driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
        driver.execute_script(f"localStorage.setItem('data_Guest', '{save_data}');")

driver.quit()
