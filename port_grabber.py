from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import keyboard

options = Options()
# options.add_argument("--headless")
# options.add_argument("--width=1920")
# options.add_argument("--height=1080")
# options.set_preference("browser.tabs.remote.autostart", False)
# options.set_preference("browser.tabs.remote.autostart.2", False)

driver = webdriver.Firefox(options=options)
driver.get("http://localhost:8000")

# Warten, bis __GLOBAL_SCENE_DATA__ existiert
WebDriverWait(driver, timeout=10).until(
    lambda d: d.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
)

print("Press 'p' to print global scene data, 'k' to simulate 'w' key press, 'q' to quit.")

while True:
    if keyboard.is_pressed('p'):
        data = driver.execute_script("return window.__GLOBAL_SCENE_DATA__();")
        print(data)
    if keyboard.is_pressed('q'):
        break

driver.quit()
