"""
do template matching of Screenshots/snipped_confirm_button.png on image Screenshots/InGame/InGame_1.png
"""
import cv2
import numpy as np


def template_matching(image_path, template_path, threshold=0.9):
    # Load the main image and template
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # Perform template matching
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    # Find locations where the matching result exceeds the threshold
    locations = np.where(result >= threshold)

    return len(locations[0]) > 0  # Return True if any match found


if __name__ == "__main__":
    for x in range(50):
        image_path = f"Screenshots\\InGame\\InGame_{x}.png"
        template_path = "skip_template.png"
        match_found = template_matching(image_path, template_path)
        print(f"Template match found in {x}: {match_found}")
