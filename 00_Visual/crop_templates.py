import pyautogui
import numpy as np
import cv2
import easyocr
import keyboard
import baseline_model.bm_environment as bm_env
import settings

"""Cut out template of the skip-button-visualiser (arrow down)"""
image = cv2.imread("Screenshots/InGame/InGame_2.png")

y1 = 116
y2 = 159
x1 = 1677
x2 = 1704
cropped_image = image[y1:y2, x1:x2]

cv2.imwrite("poke_dollar_template.png", cropped_image)
