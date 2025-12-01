from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import json
import time

# Headless mode is faster for training, but keep it visible for debugging
options = Options()
# options.add_argument("--headless")

print("Starting Browser...")
driver = webdriver.Firefox(options=options)
driver.get("http://localhost:8000")

# --- 1. Inject Settings ---
print("Injecting Settings...")
settings = {
    "PLAYER_GENDER": 0, 
    "GAME_SPEED": 5, 
    "MASTER_VOLUME": 0, 
    "TUTORIALS": 0, 
    "ENABLE_RETRIES": 1, 
    "HP_BAR_SPEED": 2
}
driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
driver.refresh()

# --- 2. Inject Save Data ---
try:
    with open("copied_save_data.txt", "r") as f:
        file_content = f.read()
    print("Injecting Save Data...")
    driver.execute_script(f"localStorage.setItem('data_Guest', '{file_content}');")
except FileNotFoundError:
    print("Warning: 'copied_save_data.txt' not found. Starting fresh save.")

time.sleep(1)
driver.refresh()

# --- 3. Wait for Game Load ---
print("Waiting for game to load...")
WebDriverWait(driver, timeout=30).until(
    lambda d: d.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
)
print("Game Loaded & Hooks Detected!")

input("Press Enter to start the extraction loop...")

# --- 4. Game Loop with FULL DATA Print ---
try:
    for i in range(5):
        # CALL THE EXTRACTION
        state = driver.execute_script("return window.__GLOBAL_SCENE_DATA__();")
        
        print(f"\n========== STEP {i} ==========")
        print(f"Phase:   {state.get('phase')}")
        print(f"Turn:    {state.get('turn')}")
        print(f"Weather: {state.get('weather')}")
        
        # --- PRINT MY POKEMON (Detailed) ---
        if state.get('myParty'):
            # Get the first valid pokemon
            valid_party = [p for p in state['myParty'] if p is not None]
            if valid_party:
                lead = valid_party[0]
                print("\n--- MY LEAD ---")
                print(f"Name:   {lead['name']} (Lvl {lead['level']})")
                print(f"HP:     {lead['hp']} / {lead['maxHp']}")
                print(f"Types:  {lead['type1']} / {lead['type2']}")
                print(f"Stats:  Atk:{lead['stats']['atk']} Def:{lead['stats']['def']} Spd:{lead['stats']['spd']}")
                print("Moves:")
                for m in lead['moves']:
                    print(f" [ ] {m['name']} (PP: {m['pp']}) Type: {m['type']}")
        
        # --- PRINT ENEMY POKEMON (Detailed) ---
        if state.get('enemyActive'):
            enemy = state['enemyActive']
            print("\n--- ENEMY ---")
            print(f"Name:   {enemy['name']} (Lvl {enemy['level']})")
            print(f"HP:     {enemy['hp']} / {enemy['maxHp']}")
            print(f"Types:  {enemy['type1']} / {enemy['type2']}")
            print(f"Stats:  Atk:{enemy['stats']['atk']} Def:{enemy['stats']['def']} Spd:{enemy['stats']['spd']}")
            
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping...")

driver.quit()