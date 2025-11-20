"""
do template matching of Screenshots/snipped_confirm_button.png on image Screenshots/InGame/InGame_1.png
"""
import cv2
import numpy as np
from PIL import Image
import os


def template_matching(image_path, template_path, threshold=0.8):
    # Load the main image and template
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # Convert images to grayscale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Get dimensions of the template
    template_height, template_width = template_gray.shape

    # Perform template matching
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Find locations where the matching result exceeds the threshold
    locations = np.where(result >= threshold)

    # Draw rectangles around matched regions
    for pt in zip(*locations[::-1]):  # Switch x and y coordinates
        cv2.rectangle(image, pt, (pt[0] + template_width, pt[1] + template_height), (0, 255, 0), 2)

    return len(locations[0]) > 0  # Return True if any match found


if __name__ == "__main__":
    image_path = "Screenshots\\InGame\\InGame_1.png"
    template_path = "Screenshots\\snipped_confirm_button.png"
    match_found = template_matching(image_path, template_path)
    print(f"Template match found: {match_found}")
