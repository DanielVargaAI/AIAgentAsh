import pyautogui
import numpy as np
import cv2

def nothing(x):
    pass

print("--- Interactive Health Bar Calibrator ---")
print("\nInstructions:")
print("1. Run your game and get a health bar on screen.")
print("2. Run this script.")
print("3. A window with a screenshot of your screen will appear.")
print("4. Draw a box *tightly* around the 'perfect' health bar.")
print("   (Click and drag from top-left to bottom-right)")
print("5. Press ENTER or SPACE to confirm your selection.")
print("6. Look at the console. It will print the W/H for your main script.")
print("7. A new 'Trackbars' window will appear. Tune the HSV values.")
print("8. Press 'q' to get the final values for that color.")
print("\n...Taking screenshot in 3 seconds...")
cv2.waitKey(3000) # 3-second delay to let you switch to your game

# 1. Take screenshot and let user select ROI
image = pyautogui.screenshot()
image = np.array(image)
image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# Make window resizable
cv2.namedWindow("Select Health Bar", cv2.WINDOW_NORMAL)
roi = cv2.selectROI("Select Health Bar", image_bgr, fromCenter=False, showCrosshair=True)
cv2.destroyWindow("Select Health Bar")

# 2. Crop to the selected ROI
x, y, w, h = roi
cropped_image = image_bgr[y:y+h, x:x+w]

# --- 3. Print Dimensions ---
print("\n--- STEP 1: Dimensions Calibration ---")
print("Copy these values into your main game_reader.py script:")
print(f"TARGET_HEALTH_BAR_WIDTH = {w}")
print(f"TARGET_HEALTH_BAR_HEIGHT = {h}")
print("--------------------------------------")

if w == 0 or h == 0:
    print("Error: You did not select a region. Exiting.")
else:
    # --- 4. Open HSV Tuner ---
    hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    
    cv2.namedWindow("Trackbars")
    cvs = 'Trackbars' 
    cv2.createTrackbar("H_min", cvs, 0, 179, nothing)
    cv2.createTrackbar("S_min", cvs, 0, 255, nothing)
    cv2.createTrackbar("V_min", cvs, 0, 255, nothing)
    cv2.createTrackbar("H_max", cvs, 179, 179, nothing)
    cv2.createTrackbar("S_max", cvs, 255, 255, nothing)
    cv2.createTrackbar("V_max", cvs, 255, 255, nothing)

    print("\n--- STEP 2: HSV Color Tuning ---")
    print("Adjust sliders to find your first color (e.g., Green).")
    print("Press 'q' when the 'Mask' window looks perfect.")

    while True:
        h_min = cv2.getTrackbarPos("H_min", cvs)
        s_min = cv2.getTrackbarPos("S_min", cvs)
        v_min = cv2.getTrackbarPos("V_min", cvs)
        h_max = cv2.getTrackbarPos("H_max", cvs)
        s_max = cv2.getTrackbarPos("S_max", cvs)
        v_max = cv2.getTrackbarPos("V_max", cvs)

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(hsv, lower, upper)
        cv2.imshow("Original Cropped Bar", cropped_image)
        cv2.imshow("Mask (Your Target)", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nFinal Values (Copy-paste into process_health_roi):")
            print(f"lower = np.array([{h_min}, {s_min}, {v_min}])")
            print(f"upper = np.array([{h_max}, {s_max}, {v_max}])")
            break

    cv2.destroyAllWindows()