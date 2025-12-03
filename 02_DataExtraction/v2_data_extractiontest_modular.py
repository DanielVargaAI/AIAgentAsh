from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import json
import time
import os

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

# --- 4. Interactive Extraction Loop ---
print("\n" + "="*40)
print("  INTERACTIVE MODE ACTIVE")
print("  Press ENTER to capture the current state.")
print("  Type 'q' and ENTER to quit.")
print("="*40 + "\n")

try:
    while True:
        user_input = input("Press Enter to extract (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break

        # CALL THE EXTRACTION
        try:
            state = driver.execute_script("return window.__GLOBAL_SCENE_DATA__();")
            
            # Clear console for cleaner output (optional, remove if you want history)
            # os.system('cls' if os.name == 'nt' else 'clear') 

            print(f"\n========== CAPTURED STATE ==========")
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
                    
                    # Safe stat printing
                    stats = lead.get('stats', {})
                    print(f"Stats:  Atk:{stats.get('atk', 0)} Def:{stats.get('def', 0)} Spd:{stats.get('spd', 0)}")
                    
                    print("Moves:")
                    if lead.get('moves'):
                        for m in lead['moves']:
                            print(f" [ ] {m['name']} (PP: {m['pp']}) Type: {m['type']}")
                    else:
                        print(" [!] No moves found (Check extraction logic)")

            # --- PRINT ENEMY POKEMON (Detailed) ---
            if state.get('enemyActive'):
                enemy = state['enemyActive']
                print("\n--- ENEMY ---")
                print(f"Name:   {enemy['name']} (Lvl {enemy['level']})")
                print(f"HP:     {enemy['hp']} / {enemy['maxHp']}")
                print(f"Types:  {enemy['type1']} / {enemy['type2']}")
                
                stats = enemy.get('stats', {})
                print(f"Stats:  Atk:{stats.get('atk', 0)} Def:{stats.get('def', 0)} Spd:{stats.get('spd', 0)}")
            
            print("====================================\n")
            
        except Exception as e:
            print(f"Extraction Error: {e}")

except KeyboardInterrupt:
    print("\nStopping...")

driver.quit()