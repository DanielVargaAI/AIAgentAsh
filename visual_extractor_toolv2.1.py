import pyautogui
import numpy as np
import cv2
import easyocr

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])  # Specify the language(s)

# --- Label data exported from Label Studio ---
LABEL_DATA = {
  "images": [
    {
      "width": 1920,
      "height": 1080,
      "id": 0,
      "file_name": "..\\..\\label-studio\\label-studio\\media\\upload\\1\\21b50687-Screenshot_2025-11-07_152205.png"
    }
  ],
  "categories": [
    {"id": 0, "name": "Handwriting"},
    {"id": 1, "name": "Logo"},
    {"id": 2, "name": "Text"}
  ],
  "annotations": [
    {"id": 0, "image_id": 0, "category_id": 2, "segmentation": [], "bbox": [169.62226640159045, 201.8290258449304, 388.6282306163022, 81.5904572564612], "ignore": 0, "iscrowd": 0, "area": 31708.35503875355},
    {"id": 1, "image_id": 0, "category_id": 2, "segmentation": [], "bbox": [566.8389662027832, 195.3876739562625, 128.82703777335996, 94.47316103379723], "ignore": 0, "iscrowd": 0, "area": 12170.697485069713},
    {"id": 2, "image_id": 0, "category_id": 1, "segmentation": [], "bbox": [766.5208747514912, 182.5049701789264, 130.97415506958242, 173.91650099403586], "ignore": 0, "iscrowd": 0, "area": 22778.566770352038},
    {"id": 3, "image_id": 0, "category_id": 0, "segmentation": [], "bbox": [395.06958250496973, 270.53677932405583, 349.9801192842941, 60.11928429423495], "ignore": 0, "iscrowd": 0, "area": 21040.554288582738}
  ],
  "info": {"year": 2025, "version": "1.0", "description": "", "contributor": "Label Studio", "url": "", "date_created": "2025-11-07 15:51:44.706010"}
}

def _build_category_map(label_data):
    return {c['id']: c['name'] for c in label_data.get('categories', [])}

def _annotations_to_rois(label_data, include_categories=None):
    """
    Convert label-studio annotations (x,y,w,h) to list of ROIs (x1,y1,x2,y2).
    include_categories: list of category names to include (None => include all)
    """
    img_meta = label_data['images'][0]
    base_w, base_h = img_meta['width'], img_meta['height']
    cat_map = _build_category_map(label_data)
    rois = []
    for ann in label_data.get('annotations', []):
        cat_name = cat_map.get(ann['category_id'], None)
        if include_categories and cat_name not in include_categories:
            continue
        x, y, w, h = ann['bbox']
        x1, y1 = int(round(x)), int(round(y))
        x2, y2 = int(round(x + w)), int(round(y + h))
        rois.append({'id': ann['id'], 'category': cat_name, 'bbox': (x1, y1, x2, y2), 'base_size': (base_w, base_h)})
    return rois

def _scale_roi_to_screen(roi, screen_w, screen_h):
    """
    Scale ROI coordinates from labeled image resolution to current screen resolution.
    roi: dict returned from _annotations_to_rois
    """
    base_w, base_h = roi['base_size']
    x1, y1, x2, y2 = roi['bbox']
    x_scale = screen_w / base_w
    y_scale = screen_h / base_h
    sx1 = int(round(x1 * x_scale))
    sy1 = int(round(y1 * y_scale))
    sx2 = int(round(x2 * x_scale))
    sy2 = int(round(y2 * y_scale))
    return (sx1, sy1, sx2, sy2)

def read_current_progression_state():
    # take screenshot (PIL -> numpy)
    image = pyautogui.screenshot()
    image = np.array(image)
    screen_h, screen_w = image.shape[:2]

    # get ROIs that were labeled as "Text" (change as needed)
    rois = _annotations_to_rois(LABEL_DATA, include_categories=['Text'])
    if not rois:
        print("No labeled ROIs found for the requested categories.")
        return

    for roi in rois:
        scaled = _scale_roi_to_screen(roi, screen_w, screen_h)
        x1, y1, x2, y2 = scaled
        # guard bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(screen_w, x2), min(screen_h, y2)
        if x2 <= x1 or y2 <= y1:
            print(f"ROI {roi['id']} invalid after scaling: {scaled}")
            continue

        cropped_image = image[y1:y2, x1:x2]
        # optionally upscale to improve OCR
        cropped_image = cv2.resize(cropped_image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

        # perform OCR
        result = reader.readtext(cropped_image)
        print(f"ROI id={roi['id']} category={roi['category']} bbox={scaled} -> {x2-x1}x{y2-y1} px:")
        if not result:
            print("  No text detected.")
        for (res_bbox, res_text, res_conf) in result:
            print(f"  Detected text: {res_text} (conf={res_conf:.2f})")

if __name__ == "__main__":
    read_current_progression_state()