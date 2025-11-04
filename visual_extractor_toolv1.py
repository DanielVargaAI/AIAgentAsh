# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#                 POKEROGUE VISUAL EXTRACTOR TOOL
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# This script is a 4-in-1 tool to help you build and debug the
# "eyes" of your AI bot. Its only job is to find the game
# window and perfectly read all the data from the screen.
#
# You must run this script and follow the steps in order (1-4)
# to configure all the coordinates at the top of this file.
#
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

# --- 1. IMPORTS ---
# Import all necessary libraries

import cv2          # OpenCV: For all image processing (cropping, color detection)
import numpy as np  # NumPy: For handling image data as arrays
import pytesseract  # Python-Tesseract: For reading text (OCR)
import pyautogui    # PyAutoGUI: For controlling the mouse (hovering, finding position)
import time         # Time: For adding small pauses (e.g., `time.sleep(0.1)`)
import sys          # System: For basic system functions
import os           # Operating System: For checking if files exist (e.g., `image_82eca9.png`)
import mss          # MSS: For ultra-fast screen capturing (much faster than pyautogui)
import pygetwindow as gw # PyGetWindow: For finding and controlling the game window
import re           # Regular Expressions: For cleaning up the text we read with OCR

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# --- (!!! 2. CONFIGURATION - TUNE THIS SECTION !!!) ---
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# This is the *only* section you need to edit.
# Use the tool's modes to find the correct values.
#
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

# --- Desired Fixed Size ---
# This is our *goal*. Try to manually resize your window
# as close to this as possible in Mode 2.
TARGET_WIDTH = 800
TARGET_HEIGHT = 450

# --- Monitor Region ---
# This is the (top, left, width, height) of your game's *content area*.
# You will get this value by running Mode 2.
MONITOR_REGION = {"top": 100, "left": 100, "width": TARGET_WIDTH, "height": TARGET_HEIGHT} # (!!! CUSTOMIZE AFTER RUNNING MODE 2 !!!)

# --- Test Image ---
# The static screenshot to test logic on (must match your TARGET_WIDTH/HEIGHT)
IMAGE_PATH = 'image_82eca9.png' 

# --- Bounding Boxes (BBoxes) ---
# All BBoxes are (y1, y2, x1, x2) and ARE RELATIVE to the MONITOR_REGION.
# (y1, y2) is the top-to-bottom pixel range.
# (x1, x2) is the left-to-right pixel range.
#
# You will find these values by running Mode 3 and manually tuning them
# until the red boxes in the debug window are perfect.
# These guesses are based on your 800x450 screenshot.

# --- HP BBoxes ---
PLAYER_HP_TEXT_BBOX = (357, 377, 375, 455) # For the "14 / 20" text
ENEMY_HP_BBOX = (138, 148, 260, 400)      # For the enemy's green HP bar

# --- Type Icon BBoxes (for CV Color) ---
PLAYER_TYPE1_BBOX = (330, 350, 203, 223)  # Player's 1st type icon
PLAYER_TYPE2_BBOX = (355, 375, 203, 223)  # Player's 2nd type icon
ENEMY_TYPE1_BBOX = (110, 130, 410, 430)   # Enemy's 1st type icon
ENEMY_TYPE2_BBOX = (135, 155, 410, 430)   # Enemy's 2nd type icon

# --- Move Info BBoxes (for OCR) ---
# These all point to the info box in the bottom-right
MOVE_TYPE_BBOX = (395, 415, 385, 480)     # "NORMAL" text
MOVE_POWER_BBOX = (418, 438, 425, 455)    # "40" (from "Stärke 40")
MOVE_ACCURACY_BBOX = (440, 460, 425, 465) # "100" (from "Genauigkeit 100")

# --- Move Hover Coordinates (x, y) ---
# The (x, y) pixel *inside* the MONITOR_REGION to hover over
# to select each move.
MOVE_HOVER_COORDS = [
    (200, 405), # Move 1 (Tackle)
    (325, 405), # Move 2 (Heuler)
    (210, 435), # Move 3 (Rankenhieb)
    # (Add Move 4 here if it appears)
]

# --- Color Definitions (HSV) ---
# We use HSV (Hue, Saturation, Value) because it's better for
# color detection than RGB. You can find these values with any
# online "HSV Color Picker" tool. 
COLOR_RANGES = {
    # The (min_color, max_color) for the HP bar
    "GREEN_HP": (np.array([35, 100, 100]), np.array([75, 255, 255])),
    
    # The (min_color, max_color) for each type icon
    # You must find these values yourself by looking at the icons.
    "TYPE_GRASS": (np.array([40, 40, 40]), np.array([70, 255, 255])), # (Guess)
    "TYPE_POISON": (np.array([130, 40, 40]), np.array([160, 255, 255])), # (Guess)
    # ... add all other 16 types here as you find them ...
}

# --- Tesseract Path ---
# If you did NOT check "Add to PATH" during installation,
# you must uncomment this line and point it to your `tesseract.exe`
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- (!!! END OF CONFIGURATION SECTION !!!) ---


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# ---     3. CV/OCR HELPER FUNCTIONS     ---
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# These are the core "eyes" of our bot. Each function reads
# one specific piece of data from a cropped part of the screen.
#
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def _get_hp_from_color(image, bbox):
    """(CV Method) Gets HP percentage from a color bar."""
    try:
        # 1. Crop the image to just the HP bar
        y1, y2, x1, x2 = bbox
        hp_bar_img = image[y1:y2, x1:x2]
        
        # 2. Convert from BGR (OpenCV's default) to HSV color space
        hsv = cv2.cvtColor(hp_bar_img, cv2.COLOR_BGR2HSV)
        
        # 3. Create a "mask" that is 1 for green pixels, 0 for everything else
        mask = cv2.inRange(hsv, COLOR_RANGES["GREEN_HP"][0], COLOR_RANGES["GREEN_HP"][1])
        
        # 4. Calculate the percentage of green pixels
        total_pixels = hp_bar_img.size / 3 # (h * w * 3) / 3
        green_pixels = cv2.countNonZero(mask)
        
        if total_pixels == 0: return 0.0 # Avoid division by zero
        return green_pixels / total_pixels
    except Exception as e:
        print(f"[CV HP Error] {e}")
        return 0.0 # Return 0% on any error

def _get_hp_from_ocr(image, bbox):
    """(OCR Method) Gets player HP from "X / Y" text."""
    try:
        # 1. Crop the image to just the text
        y1, y2, x1, x2 = bbox
        hp_text_img = image[y1:y2, x1:x2]
        
        # 2. Pre-process: Convert to grayscale
        gray = cv2.cvtColor(hp_text_img, cv2.COLOR_BGR2GRAY)
        
        # 3. Pre-process: Threshold to get a clean black-and-white image
        # (This is a *critical* step for OCR accuracy)
        (thresh, bw_img) = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # 4. Configure Tesseract
        # --oem 3: Default OCR engine
        # --psm 6: Assume a single uniform block of text
        # -c ...: Whitelist *only* these characters.
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789/'
        
        # 5. Run OCR
        text = pytesseract.image_to_string(bw_img, config=custom_config)
        
        # 6. Parse the text "14 / 20"
        parts = text.strip().split('/')
        if len(parts) == 2:
            return float(parts[0]) / float(parts[1])
        return 0.0 # Return 0% if OCR failed
    except Exception as e:
        print(f"[OCR HP Error] {e}")
        return 0.0

def _get_type_from_color(image, bbox):
    """(CV Method) Gets a Pokémon type by checking the avg color of an icon."""
    try:
        # 1. Crop to the tiny icon
        y1, y2, x1, x2 = bbox
        icon_img = image[y1:y2, x1:x2]
        
        # 2. Convert to HSV
        hsv = cv2.cvtColor(icon_img, cv2.COLOR_BGR2HSV)
        
        # 3. Check for GRASS
        # Create a mask for the "Grass" HSV range
        mask_grass = cv2.inRange(hsv, COLOR_RANGES["TYPE_GRASS"][0], COLOR_RANGES["TYPE_GRASS"][1])
        # If > 25% of the icon's pixels are Grass-green, we'll call it
        if cv2.countNonZero(mask_grass) > (icon_img.size / 4): 
            return "GRASS"
            
        # 4. Check for POISON
        mask_poison = cv2.inRange(hsv, COLOR_RANGES["TYPE_POISON"][0], COLOR_RANGES["TYPE_POISON"][1])
        if cv2.countNonZero(mask_poison) > (icon_img.size / 4):
            return "POISON"

        # ... you would add all other 16 types here ...
            
        return "UNKNOWN" # If no color matched
    except Exception as e:
        print(f"[CV Type Error] {e}")
        return "ERROR"

def _get_text_from_ocr(image, bbox, whitelist=None):
    """(Generic OCR Method) Reads any text from a BBox."""
    try:
        # 1. Crop to the text
        y1, y2, x1, x2 = bbox
        text_img = image[y1:y2, x1:x2]
        
        # 2. Pre-process: Grayscale and Threshold
        gray = cv2.cvtColor(text_img, cv2.COLOR_BGR2GRAY)
        (thresh, bw_img) = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # 3. Configure Tesseract
        # --psm 7: Treat as a single line of text.
        config = r'--oem 3 --psm 7' 
        if whitelist:
            config += f' -c tessedit_char_whitelist={whitelist}'
            
        # 4. Run OCR (set language to German, 'deu', for "Stärke")
        text = pytesseract.image_to_string(bw_img, config=config, lang='deu') 
        
        # 5. Clean the text: remove all non-alphanumeric chars and make uppercase
        # (e.g., "Stärke 40" -> "STRKE40" -- we only care about the "40")
        # (e.g., "NORMAL" -> "NORMAL")
        cleaned_text = re.sub(r'[^A-Z0-9]', '', text.upper())
        return cleaned_text
    except Exception as e:
        print(f"[OCR Text Error] {e}")
        return "OCR_ERROR"

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# ---     4. TOOL MODES (1-4)     ---
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# These are the 4 user-facing functions you will run from the
# command line to set up and debug the extractor.
#
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def mode_1_find_window_title():
    """
    MODE 1:
    Scans and prints all open window titles.
    Your game's desktop app will have a unique title.
    You need this title for Mode 2.
    """
    print("--- Mode 1: Find Window Title ---")
    print("Scanning all open windows...")
    
    all_titles = gw.getAllTitles()
    if not all_titles:
        print("No windows found.")
        return

    print("\nAll currently open window titles:")
    for title in all_titles:
        if title: # Filter out empty titles
            print(title)
            
    print("\nFind your game's title in this list (e.g., 'PokeRogue').")
    print("You'll need this *exact* title for Mode 2.")

def mode_2_find_game_coords():
    """
    MODE 2: (Automatic Resize)
    This is the most important setup step.
    1. Asks for the game's window title.
    2. Tries to AUTOMATICALLY resize the window to TARGET_WIDTH/HEIGHT.
    3. Asks you to find the top-left corner of the *content area*.
    4. Calculates and prints the final `MONITOR_REGION` dictionary.
    
    You MUST copy/paste this output into the CONFIGURATION section.
    """
    print("--- Mode 2: Find Game Coordinates (Automatic) ---")
    
    default_title = "PokéRogue"
    title_prompt = f"Enter the *exact* title of your game window (default: {default_title}): "
    title_input = input(title_prompt)
    title = title_input if title_input else default_title
    
    try:
        # 1. Find the window
        window_list = gw.getWindowsWithTitle(title)
        if not window_list:
            print(f"Error: No window with title '{title}' found.")
            return
        
        window = window_list[0]
        print(f"\nFound window: '{window.title}'")

        # --- NEW ROBUST STEPS ---
        
        # 2. Check if minimized and restore
        if window.isMinimized:
            print("Window is minimized. Restoring...")
            window.restore()
            time.sleep(0.5) # Give window time to restore

        # 3. Try to resize
        print(f"Attempting to resize window to {TARGET_WIDTH}x{TARGET_HEIGHT}...")
        try:
            window.resizeTo(TARGET_WIDTH, TARGET_HEIGHT)
            time.sleep(0.5) # Give window time to resize
        except Exception as e:
            print(f"\n--- RESIZE FAILED ---")
            print(f"Error: {e}")
            print("The game window is locked and cannot be resized automatically.")
            print("Please run Mode 2 (Manual Resize) from the previous script version,")
            print("or manually resize the window to 800x450 and find the BBoxes yourself.")
            return

        # 4. Try to activate (bring to front)
        print("Activating window (bringing to front)...")
        try:
            window.activate()
            time.sleep(0.5) # Give window time to activate
        except Exception as e:
            print(f"Warning: Could not auto-activate window ({e}).")
            print("PLEASE CLICK ON THE GAME WINDOW MANUALLY NOW.")
        
        # 5. Find the content area
        print("\nINSTRUCTIONS: We now need to find the *content area*.")
        print("The window is resized and (should be) active.")
        
        print("\n1. Move your mouse to the **TOP-LEFT** corner of the game's *content area* (e.g., just below the title bar, at the top-left of the battle scene).")
        print("2. Press ENTER.")
        input("   (Waiting...)")
        top_left = pyautogui.position() # Get mouse position
        print(f"   > Top-Left set to: {top_left}")

        # 6. Calculate the final region
        # We assume the resize worked, so width/height are our targets
        left = top_left.x
        top = top_left.y
        width = TARGET_WIDTH 
        height = TARGET_HEIGHT
        
        print("\n--- RESULT ---")
        print("SUCCESS! Your coordinates are locked in.")
        print("Copy this dictionary into the `MONITOR_REGION` variable at the top of this script:")
        print(f'MONITOR_REGION = {{"top": {top}, "left": {left}, "width": {width}, "height": {height}}}')
        print("\nYou won't need to run Mode 2 again unless you change TARGET_WIDTH/HEIGHT.")

    except IndexError:
        print(f"Error: No window with title '{title}' found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Hint: Is the window title *exactly* correct? Is the game running?")

def mode_3_test_logic_on_image():
    """
    MODE 3:
    This is your main debugging mode for the BBoxes.
    It loads your static screenshot (`IMAGE_PATH`) and runs all
    the CV/OCR functions on it.
    
    It prints the results to the console AND shows a popup
    debug window with red boxes drawn on it.
    
    Your job: If the console output is wrong, look at the
    red boxes. If a box is in the wrong place, go to the
    CONFIGURATION section and "tune" (edit) the ..._BBOX
    variable until it's perfect.
    """
    print(f"--- Mode 3: Test Logic on Static Image ({IMAGE_PATH}) ---")
    
    # Check if the test image exists
    if not os.path.exists(IMAGE_PATH):
        print(f"[Error] Test image '{IMAGE_PATH}' not found in this folder.")
        print("Please save your 800x450 battle screenshot as 'image_82eca9.png' here.")
        return
        
    # Read the image from disk
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"[Error] Could not read image.")
        return
        
    # Check if image matches target size
    h, w, _ = img.shape
    if w != TARGET_WIDTH or h != TARGET_HEIGHT:
        print(f"Warning: Your test image is {w}x{h} but your target is {TARGET_WIDTH}x{TARGET_HEIGHT}.")
        print("The BBoxes may not line up. Please use a screenshot that matches your TARGET_WIDTH/HEIGHT.")
        
    # Make a copy to draw on
    debug_img = img.copy()
    
    print("Running extractors on the image...")
    
    # --- Run ALL Extractions ---
    player_hp = _get_hp_from_ocr(img, PLAYER_HP_TEXT_BBOX)
    enemy_hp = _get_hp_from_color(img, ENEMY_HP_BBOX)
    
    p_type1 = _get_type_from_color(img, PLAYER_TYPE1_BBOX)
    p_type2 = _get_type_from_color(img, PLAYER_TYPE2_BBOX)
    e_type1 = _get_type_from_color(img, ENEMY_TYPE1_BBOX)
    e_type2 = _get_type_from_color(img, ENEMY_TYPE2_BBOX)
    
    # (Note: The screenshot only shows data for "Tackle")
    move_type = _get_text_from_ocr(img, MOVE_TYPE_BBOX, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    move_power_text = _get_text_from_ocr(img, MOVE_POWER_BBOX, "0123456789")
    move_acc_text = _get_text_from_ocr(img, MOVE_ACCURACY_BBOX, "0123456789")
    # Clean OCR noise
    move_power = re.sub(r'[^0-9]', '', move_power_text)
    move_acc = re.sub(r'[^0-9]', '', move_acc_text)


    print("\n--- EXTRACTION RESULTS ---")
    print(f"Player HP: {player_hp:.2f} (Expected: 0.70)")
    print(f"Enemy HP:  {enemy_hp:.2f} (Expected: ~1.0)")
    print(f"Player Types: {p_type1}, {p_type2} (Expected: GRASS, POISON)")
    print(f"Enemy Types:  {e_type1}, {e_type2} (Expected: GRASS, POISON)")
    print("\nMove Info (for 'Tackle'):")
    print(f"  Type: {move_type} (Expected: NORMAL)")
    print(f"  Power: {move_power} (Expected: 40)")
    print(f"  Accuracy: {move_acc} (Expected: 100)")
    print("--------------------------")

    # --- Draw BBoxes on the debug image ---
    print("Drawing BBoxes... check the debug window.")
    all_bboxes = {
        "P_HP": PLAYER_HP_TEXT_BBOX, "E_HP": ENEMY_HP_BBOX,
        "P_T1": PLAYER_TYPE1_BBOX, "P_T2": PLAYER_TYPE2_BBOX,
        "E_T1": ENEMY_TYPE1_BBOX, "E_T2": ENEMY_TYPE2_BBOX,
        "M_TYPE": MOVE_TYPE_BBOX, "M_POW": MOVE_POWER_BBOX, "M_ACC": MOVE_ACCURACY_BBOX,
    }
    # Loop over all our BBoxes and draw them
    for name, (y1, y2, x1, x2) in all_bboxes.items():
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 0, 255), 1) # Red box
        cv2.putText(debug_img, name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1) # Red text

    print("\nShowing debug window. Press any key to quit.")
    cv2.imshow(f"Extractor Debug (Static Image)", debug_img)
    cv2.waitKey(0) # Wait until a key is pressed
    cv2.destroyAllWindows() # Close the window

def mode_4_test_logic_on_live_game():
    """
    MODE 4:
    The final test. This runs the full "Hover-to-Scan" logic
    on the *live game* in a continuous loop.
    
    It will:
    1. Scan static data (HP, Types).
    2. Take control of your mouse.
    3. Hover over Move 1, scan the info box.
    4. Hover over Move 2, scan the info box.
    5. ...
    6. Print all results, wait 2 seconds, and repeat.
    
    Press Ctrl-C in your terminal to stop it.
    """
    print("--- Mode 4: Test Logic on Live Game ---")
    print("Ensure your MONITOR_REGION is set correctly from Mode 2.")
    print(f"Using region: {MONITOR_REGION}")
    print("This will take ~2 seconds to scan all moves.")
    print("Press Ctrl-C in this terminal to stop.")
    
    sct = mss.mss() # Initialize the screen grabber
    
    # Calculate *absolute* screen coordinates for hovering
    # (MONITOR_REGION's top-left corner + relative move coord)
    abs_hover_coords = [
        (MONITOR_REGION["left"] + x, MONITOR_REGION["top"] + y)
        for (x, y) in MOVE_HOVER_COORDS
    ]
    
    try:
        # Loop forever until user presses Ctrl-C
        while True:
            print("\n--- NEW SCAN ---")
            
            # --- 1. Grab constant data ---
            # Grab one screenshot of the whole game
            sct_img = sct.grab(MONITOR_REGION)
            img = np.array(sct_img)
            
            # Run extractors on this static image
            player_hp = _get_hp_from_ocr(img, PLAYER_HP_TEXT_BBOX)
            enemy_hp = _get_hp_from_color(img, ENEMY_HP_BBOX)
            e_type1 = _get_type_from_color(img, ENEMY_TYPE1_BBOX)
            
            # Use a try/except in case there is no second type
            try:
                e_type2 = _get_type_from_color(img, ENEMY_TYPE2_BBOX)
            except Exception:
                e_type2 = "NONE"
            
            print(f"Player HP: {player_hp:.2f} | Enemy HP: {enemy_hp:.2f}")
            print(f"Enemy Types: {e_type1}, {e_type2}")
            
            move_data = []
            
            # --- 2. Perform "Hover-to-Scan" ---
            for i, (abs_x, abs_y) in enumerate(abs_hover_coords):
                # Move the mouse to the move
                pyautogui.moveTo(abs_x, abs_y)
                time.sleep(0.1) # Wait for info box to update
                
                # Grab a *new* screenshot
                sct_img = sct.grab(MONITOR_REGION)
                img = np.array(sct_img)
                
                # Scan *only* the info box BBoxes
                move_type = _get_text_from_ocr(img, MOVE_TYPE_BBOX, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                move_power_text = _get_text_from_ocr(img, MOVE_POWER_BBOX, "0123456789")
                move_power = re.sub(r'[^0-9]', '', move_power_text) # Clean text
                
                print(f"  Move {i+1}: Type={move_type}, Power={move_power}")
                move_data.append((move_type, move_power))
            
            # Move mouse away to not obstruct the screen
            pyautogui.moveTo(MONITOR_REGION["left"], MONITOR_REGION["top"])
            time.sleep(2) # Wait before next scan

    except KeyboardInterrupt:
        print("\nLive test stopped by user.")
    except Exception as e:
        print(f"An error occurred during live test: {e}")

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# ---     5. MAIN SCRIPT ENTRYPOINT     ---
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# This is the code that runs when you type `python visual_extractor_tool.py`
# It's the main menu.
#
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

if __name__ == "__main__":
    print("===============================")
    print(" PokeRogue Visual Extractor Tool")
    print("===============================")
    print("What do you want to do?")
    print("\n--- Setup ---")
    print("  1: Find your game's *window title*")
    print("  2: Find game's coords & **Auto-Resize**")
    print("\n--- Debugging ---")
    print("  3: Test CV/OCR logic on a *static screenshot*")
    print("  4: Test CV/OCR logic on the *live game*")
    
    choice = input("\nEnter choice (1, 2, 3, or 4): ")
    
    if choice == '1':
        mode_1_find_window_title()
    elif choice == '2':
        mode_2_find_game_coords()
    elif choice == '3':
        mode_3_test_logic_on_image()
    elif choice == '4':
        mode_4_test_logic_on_live_game()
    else:
        print("Invalid choice. Exiting.")



