import cv2
import numpy as np
import pyautogui  # Using this as it's in your old script
import time

# --- 1. Import Your Extractor Class ---
# This assumes your class is in a file named "visual_extractor.py"
try:
    from visual_extractor_toolv3_1_DebugaddedClassbased import PokerogueExtractor
except ImportError:
    print("Error: Could not find 'visual_extractor.py'.")
    print("Make sure your PokerogueExtractor class is in that file.")
    exit()

# --- 2. Configuration ---

# This is the resolution your labels were created for.
# We found this in your 'result.json' file (e.g., "width": 2559, "height": 1439)
BASE_RESOLUTION = (2559, 1439)  # (Width, Height)

# Set this to the fight type you are testing
FIGHT_TYPE = 'single'  # or 'single'

# --- 3. Initialize ---
print("Initializing extractor... (This may take a moment)")
extractor = PokerogueExtractor('resultsLIVE.json')
print(f"Extractor ready. Will resize screen captures to {BASE_RESOLUTION} for processing.")

# --- 4. Live Capture Loop ---
print("Starting live capture... Press 'q' in the debug window to quit.")
while True:
    try:
        start_time = time.time()
        
        # 1. Grab the *entire* screen (just like your old script)
        img_pil = pyautogui.screenshot()
        
        # 2. Convert to OpenCV format (PIL -> Numpy -> BGR)
        frame_full_res = np.array(img_pil)
        frame_full_res = cv2.cvtColor(frame_full_res, cv2.COLOR_RGB2BGR)

        # 3. --- THE KEY STEP ---
        # Resize the *entire* screenshot to the *base resolution* of your labels.
        # This scales the game (wherever it is) to match the label coordinates.
        frame_resized = cv2.resize(
            frame_full_res, 
            BASE_RESOLUTION, 
            interpolation=cv2.INTER_AREA  # Good for shrinking
        )

        # 4. Call your extractor (with debug=True)
        # The extractor now receives an image of the *exact size it expects*.
        results, debug_frame = extractor.extract_gamestate(
            frame_resized, 
            FIGHT_TYPE, 
            debug=True
        )
        
        # 5. Calculate and display FPS
        fps = 1 / (time.time() - start_time)
        cv2.putText(
            debug_frame, 
            f"FPS: {fps:.2f}", 
            (10, 30),  # Top-left corner
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, (0, 0, 255), 2  # Red color
        )
        
        # 6. Show the debug window
        # The debug_frame is large (2559x1439), so we scale it down by 50% for display
        h, w = debug_frame.shape[:2]
        cv2.imshow("Pokerogue Live Debug (Resized 50%)", cv2.resize(debug_frame, (w // 2, h // 2)))

        # 7. Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        # Allow quitting with Ctrl+C in the console
        print("\nStopping live test.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        break

cv2.destroyAllWindows()
print("Live test complete.")