import cv2
import easyocr
import template_matching


def get_stage_data(image, pos, reader):
    if pos is None:
        return None
    x1, y1, x2, y2 = [1100, pos[0]-55, 1820, pos[0]]
    cropped_image = image[y1:y2, x1:x2]
    result = reader.readtext(cropped_image)

    for (res_bbox, res_text, res_conf) in result:
        print(f"Detected text: {res_text} with confidence: {res_conf}")

    return result[-1][1] if result else None


if __name__ == "__main__":
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR Reader
    image = cv2.imread("Screenshots\\InGame\\InGame_122.png")
    pos = template_matching.get_pokedollar_pos(image)
    print(get_stage_data(image, pos, reader))
