from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import keyboard
import json
import example_save
import time

# Headless (optional)
options = Options()
# options.add_argument("--headless")

driver = webdriver.Firefox(options=options)
driver.get("http://localhost:8000")

print("timer start")
# wait 5 seconds for the page to load
# time.sleep(30)

settings = {"PLAYER_GENDER": 0, "GAME_SPEED": 7, "MASTER_VOLUME": 0, "TUTORIALS": 0, "ENABLE_RETRIES": 1, "SHOW_LEVEL_UP_STATS": 0, "EXP_GAINS_SPEED": 3, "EXP_PARTY_DISPLAY": 1, "HP_BAR_SPEED": 2, "gameVersion": "1.11.3"}
tutorials = {"INTRO":True,"ACCESS_MENU":True,"MENU":True,"STARTER_SELECT":True,"POKERUS":False,"STAT_CHANGE":True,"SELECT_ITEM":True,"EGG_GACHA":False}
# save_data = example_save.save_data  # TODO hier den Save-Daten-String einfügen (localStorage.data_Guest)

# driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
# driver.execute_script(f"localStorage.setItem('data_Guest', '{save_data}');")
# print("Save data and settings injected.")
# driver.refresh()
is_copied = False
is_entered = False

while True:
    if keyboard.is_pressed("p"):
        print(driver.execute_script("return window.__GLOBAL_SCENE_DATA__();"))
    if keyboard.is_pressed("q"):
        break
    if keyboard.is_pressed("l"):
        driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
    if keyboard.is_pressed("o"):
        # import example_save
        # save_data = example_save.save_data
        # driver.execute_script(f"localStorage.setItem('data_Guest', '{save_data}');")
        if not is_entered:
            with open("copied_save_data.txt", "r") as f:
                file_content = f.read()
            driver.execute_script(f"localStorage.setItem('data_Guest', '{file_content}');")
            is_entered = True
    if keyboard.is_pressed("c"):
        if not is_copied:
            copied_save_data = driver.execute_script("return localStorage.getItem('data_Guest');")
            with open("copied_save_data.txt", "w") as f:
                f.write(copied_save_data)
            print("Save data copied to copied_save_data.txt")
            is_copied = True

driver.quit()
