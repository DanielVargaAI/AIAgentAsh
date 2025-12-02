from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import keyboard
import json
import time

# Headless (optional)
options = Options()
# options.add_argument("--headless")

driver = webdriver.Firefox(options=options)
driver.get("http://localhost:8000")

settings = {"PLAYER_GENDER": 0, "GAME_SPEED": 7, "MASTER_VOLUME": 0, "TUTORIALS": 0, "ENABLE_RETRIES": 1, "SHOW_LEVEL_UP_STATS": 0, "EXP_GAINS_SPEED": 3, "EXP_PARTY_DISPLAY": 1, "HP_BAR_SPEED": 2, "gameVersion": "1.11.3"}

driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
driver.refresh()

with open("copied_save_data.txt", "r") as f:
    file_content = f.read()
driver.execute_script(f"localStorage.setItem('data_Guest', '{file_content}');")
time.sleep(1)
driver.refresh()
time.sleep(8) 

from selenium.webdriver.support.ui import WebDriverWait
WebDriverWait(driver, timeout=10).until(
    lambda d: d.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
)
# print(driver.execute_script("return window.__GLOBAL_SCENE_DATA__();"))
# time.sleep(3)
# print(driver.execute_script("return window.__GLOBAL_SCENE_DATA__();"))

while True:
    if keyboard.is_pressed('p'):
        print(driver.execute_script("return window.__GLOBAL_SCENE_DATA__();"))
        break
