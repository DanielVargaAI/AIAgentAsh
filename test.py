import pyautogui
import numpy as np
import cv2
import easyocr
import keyboard
import baseline_model.bm_environment as bm_env

# # Initialize EasyOCR Reader
# reader = easyocr.Reader(['en'])  # Specify the language(s)

def read_current_progression_state():
    # image should be the image from self.current_screen
    image = pyautogui.screenshot()
    image = np.array(image)

    # Define the ROI (x1, y1, x2, y2)
    roi = (1595, 300, 1695, 342)

    # # scale ROI to current observation size
    # x_scale = self.obs_width / self.screen_width
    # y_scale = self.obs_height / self.screen_height
    # roi = (int(roi[0] * x_scale), int(roi[1] * y_scale), int(roi[2] * x_scale), int(roi[3] * y_scale))

    # Crop the image to the ROI
    x1, y1, x2, y2 = roi
    cropped_image = image[y1:y2, x1:x2]
    # Scale up the cropped image
    cropped_image = cv2.resize(cropped_image, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

    # Perform OCR on the cropped image
    result = reader.readtext(cropped_image)
    for (res_bbox, res_text, res_conf) in result:
        print(f"Detected text: {res_text} with confidence: {res_conf}")


def test_env_reset():
    # TODO reset the environment to an initial state
    # start new endless run
    # keyboard presses: S, Space, S, S, S, Space, A, Space, Space, Space, Space, Space, Space, Enter, Space, W, Space
    sequence = [2, 4, 2, 2, 2, 4, 1, 4, 4, 4, 4, 4, 4, 6, 4, 0, 4]
    for action in sequence:
        bm_env.apply_action(action)
        # wait a bit between actions
        pyautogui.sleep(0.5)
    pyautogui.sleep(2.0)
    bm_env.apply_action(4)  # Final Space to start
    print("Environment reset sequence completed.")


if __name__ == "__main__":
    while True:
        if keyboard.is_pressed("o"):
            break
        if keyboard.is_pressed('p'):
            read_current_progression_state()
        if keyboard.is_pressed('r'):
            test_env_reset()
