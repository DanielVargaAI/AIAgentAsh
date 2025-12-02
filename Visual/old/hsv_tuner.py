import cv2
import numpy as np

def nothing(x):
    pass

# Load the test image you saved
image = cv2.imread("health_bar_test.png")
if image is None:
    print("************************************************************")
    print("Error: 'health_bar_test.png' not found.")
    print("Please save a screenshot of a 'Debug Health Chop' window")
    print("as 'health_bar_test.png' in the same folder as this script.")
    print("************************************************************")
else:
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cv2.namedWindow("Trackbars")

    # Create trackbars for color change
    cvs = 'Trackbars' 
    cv2.createTrackbar("H_min", cvs, 0, 179, nothing)
    cv2.createTrackbar("S_min", cvs, 0, 255, nothing)
    cv2.createTrackbar("V_min", cvs, 0, 255, nothing)
    cv2.createTrackbar("H_max", cvs, 179, 179, nothing)
    cv2.createTrackbar("S_max", cvs, 255, 255, nothing)
    cv2.createTrackbar("V_max", cvs, 255, 255, nothing)

    print("\n--- HSV Color Tuner ---")
    print("Adjust sliders until 'Mask' shows *only* the color you want.")
    print("Find 'Green', 'Yellow' (optional), and 'Red' (optional).")
    print("\nPress 'q' to quit and print the final values.")

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
        cv2.imshow("Original Health Bar", image)
        cv2.imshow("Mask (Your Target)", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nFinal Values (Copy-paste these into game_reader.py):")
            print(f"lower = np.array([{h_min}, {s_min}, {v_min}])")
            print(f"upper = np.array([{h_max}, {s_max}, {v_max}])")
            break

    cv2.destroyAllWindows()