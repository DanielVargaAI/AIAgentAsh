"""
do template matching of Screenshots/snipped_confirm_button.png on image Screenshots/InGame/InGame_1.png
"""
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


def check_mask():
    tpl = cv2.imread("poke_dollar_template.png")
    hsv = cv2.cvtColor(tpl, cv2.COLOR_BGR2HSV)

    lower = np.array([25, 40, 120], dtype=np.uint8)
    upper = np.array([40, 140, 255], dtype=np.uint8)

    # lower = np.array([25, 40, 190], dtype=np.uint8)
    # upper = np.array([40, 130, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower, upper)
    masked = cv2.bitwise_and(tpl, tpl, mask=mask)

    # BGR → RGB für matplotlib
    tpl_rgb = cv2.cvtColor(tpl, cv2.COLOR_BGR2RGB)
    masked_rgb = cv2.cvtColor(masked, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 5))

    plt.subplot(1, 3, 1)
    plt.title("Template")
    plt.imshow(tpl_rgb)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Mask")
    plt.imshow(mask, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Masked Template")
    plt.imshow(masked_rgb)
    plt.axis("off")

    plt.show()


def get_pokedollar_pos(image_path, template=None, threshold=0.9):
    # Load the main image and template
    image = cv2.imread(image_path) if isinstance(image_path, str) else image_path
    template = cv2.imread("poke_dollar_template.png") if not template.any() else template
    template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)

    lower = np.array([25, 40, 120], dtype=np.uint8)
    upper = np.array([40, 140, 255], dtype=np.uint8)
    template_mask = cv2.inRange(template_hsv, lower, upper)

    # Perform template matching
    result = cv2.matchTemplate(
        image,
        template,
        cv2.TM_CCOEFF_NORMED,
        mask=template_mask
    )

    # Find locations where the matching result exceeds the threshold
    locations = np.where(result >= threshold)
    # print(len(locations[0]), locations)

    return [int(locations[0][0]), int(locations[1][0])] if len(locations[0]) > 0 else None


def found_template_skip(image_path, threshold=0.8):
    # Load the main image and template
    image = cv2.imread(image_path) if isinstance(image_path, str) else image_path
    template = cv2.imread("skip_template.png")

    # Perform template matching
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    # Find locations where the matching result exceeds the threshold
    locations = np.where(result >= threshold)
    # print(locations)

    return len(locations[0]) > 0  # Return True if any match found


if __name__ == "__main__":
    # check_mask()
    # for x in os.listdir("Screenshots\\InGame"):
    #     image_path = f"Screenshots\\InGame\\{x}"
    #     match_found = get_pokedollar_pos(image_path)
    #     print(f"Template match found in {x}: {match_found}")
    image_path = f"Screenshots\\InGame\\InGame_122.png"
    match_found = get_pokedollar_pos(image_path)
    print(f"Template match found: {match_found}")
