import pyautogui
import numpy as np
import cv2
import easyocr

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])  # Specify the language(s)

# --- Label data exported from Label Studio (NEW) ---
LABEL_DATA = {
  "images": [
    {
      "width": 2559,
      "height": 1439,
      "id": 0,
      "file_name": "..\\..\\label-studio\\label-studio\\media\\upload\\1\\41c7afa3-Screenshot_2025-11-09_154025.png"
    }
  ],
  "categories": [
    { "id": 0, "name": "AttackType" },
    { "id": 1, "name": "Attacks" },
    { "id": 2, "name": "MyHealth" },
    { "id": 3, "name": "MyLevel" },
    { "id": 4, "name": "MyName" },
    { "id": 5, "name": "MyType" },
    { "id": 6, "name": "VsHealth" },
    { "id": 7, "name": "VsLevel" },
    { "id": 8, "name": "VsName" },
    { "id": 9, "name": "VsType" }
  ],
  "annotations": [
    {
      "id": 0, "image_id": 0, "category_id": 8, "segmentation": [],
      "bbox": [194.71177015755308, 240.02093482135058, 523.2954668470327, 109.41810352616805],
      "ignore": 0, "iscrowd": 0, "area": 57257.997566243066
    },
    {
      "id": 1, "image_id": 0, "category_id": 7, "segmentation": [],
      "bbox": [728.1847725162489, 247.18198700092844, 263.21541318477256, 89.51996285979575],
      "ignore": 0, "iscrowd": 0, "area": 23563.034012426633
    },
    {
      "id": 2, "image_id": 0, "category_id": 6, "segmentation": [],
      "bbox": [475.6583101207057, 330.02135561745587, 531.7753017641597, 81.50324976787375],
      "ignore": 0, "iscrowd": 0, "area": 43341.415240070746
    },
    {
      "id": 3, "image_id": 0, "category_id": 9, "segmentation": [],
      "bbox": [1016.7864438254412, 213.77901578458682, 154.98978644382527, 220.45961002785515],
      "ignore": 0, "iscrowd": 0, "area": 34168.98787770627
    },
    {
      "id": 4, "image_id": 0, "category_id": 4, "segmentation": [],
      "bbox": [1531.1922005571032, 738.873723305478, 541.1281337047352, 84.17548746518118],
      "ignore": 0, "iscrowd": 0, "area": 45549.72443571982
    },
    {
      "id": 5, "image_id": 0, "category_id": 5, "segmentation": [],
      "bbox": [1350.816155988858, 732.1931290622099, 175.0315691736305, 231.1485608170844],
      "ignore": 0, "iscrowd": 0, "area": 40458.29531204064
    },
    {
      "id": 6, "image_id": 0, "category_id": 2, "segmentation": [],
      "bbox": [1826.474466109564, 815.0324976787373, 522.4224698235843, 70.81429897864446],
      "ignore": 0, "iscrowd": 0, "area": 36994.98097124916
    },
    {
      "id": 7, "image_id": 0, "category_id": 3, "segmentation": [],
      "bbox": [2070.984215413185, 733.5292479108634, 271.23212627669454, 77.4948932219127],
      "ignore": 0, "iscrowd": 0, "area": 21019.104664164788
    },
    {
      "id": 8, "image_id": 0, "category_id": 1, "segmentation": [],
      "bbox": [207.09842154131854, 1106.3064066852369, 664.0510677808728, 110.89786443825439],
      "ignore": 0, "iscrowd": 0, "area": 73641.8452948413
    },
    {
      "id": 9, "image_id": 0, "category_id": 1, "segmentation": [],
      "bbox": [205.7623026926648, 1230.5654596100278, 669.3955431754877, 108.22562674094733],
      "ignore": 0, "iscrowd": 0, "area": 72445.75219776403
    },
    {
      "id": 10, "image_id": 0, "category_id": 1, "segmentation": [],
      "bbox": [1051.5255338904365, 1106.3064066852369, 640.0009285051067, 117.57845868152253],
      "ignore": 0, "iscrowd": 0, "area": 75250.32272837375
    },
    {
      "id": 11, "image_id": 0, "category_id": 1, "segmentation": [],
      "bbox": [1047.5171773444754, 1230.5654596100278, 672.0677808727946, 105.55338904363965],
      "ignore": 0, "iscrowd": 0, "area": 70939.03193816166
    },
    {
      "id": 12, "image_id": 0, "category_id": 0, "segmentation": [],
      "bbox": [1956.0779944289707, 1074.239554317549, 211.10677808727928, 92.19220055710203],
      "ignore": 0, "iscrowd": 0, "area": 19462.398424386083
    }
  ],
  "info": {
    "year": 2025, "version": "1.0", "description": "", "contributor": "Label Studio",
    "url": "", "date_created": "2025-11-09 18:32:36.011723"
  }
}

def _build_category_map(label_data):
    """Builds a simple map of category ID to category name."""
    return {c['id']: c['name'] for c in label_data.get('categories', [])}

def _annotations_to_rois(label_data, include_categories=None):
    """
    Convert label-studio annotations (x,y,w,h) to list of ROIs (x1,y1,x2,y2).
    include_categories: list of category names to include (None => include all)
    """
    # Get base resolution from the *first image* in the label data
    if not label_data.get('images'):
        print("Error: 'images' key missing from LABEL_DATA")
        return []
    img_meta = label_data['images'][0]
    base_w, base_h = img_meta['width'], img_meta['height']
    
    cat_map = _build_category_map(label_data)
    rois = []
    
    for ann in label_data.get('annotations', []):
        cat_name = cat_map.get(ann['category_id'], None)
        
        # Filter by category name
        if include_categories and cat_name not in include_categories:
            continue
            
        x, y, w, h = ann['bbox']
        x1, y1 = int(round(x)), int(round(y))
        x2, y2 = int(round(x + w)), int(round(y + h))
        
        rois.append({
            'id': ann['id'], 
            'category': cat_name, 
            'bbox': (x1, y1, x2, y2), 
            'base_size': (base_w, base_h)
        })
    return rois

def _scale_roi_to_screen(roi, screen_w, screen_h):
    """
    Scale ROI coordinates from labeled image resolution to current screen resolution.
    roi: dict returned from _annotations_to_rois
    """
    base_w, base_h = roi['base_size']
    x1, y1, x2, y2 = roi['bbox']
    
    # Calculate scaling factors
    x_scale = screen_w / base_w
    y_scale = screen_h / base_h
    
    # Apply scaling and round to nearest integer
    sx1 = int(round(x1 * x_scale))
    sy1 = int(round(y1 * y_scale))
    sx2 = int(round(x2 * x_scale))
    sy2 = int(round(y2 * y_scale))
    
    return (sx1, sy1, sx2, sy2)

def read_current_progression_state():
    """
    Takes a screenshot, identifies ROIs, performs OCR, and shows a debug window
    with both the ROI labels and the detected text.
    """
    # take screenshot (PIL -> numpy)
    image = pyautogui.screenshot()
    image = np.array(image)
    screen_h, screen_w = image.shape[:2]

    # <<< DEBUG: Create a BGR copy of the image for OpenCV drawing/display
    debug_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # <<< END DEBUG

    # --- UPDATED CATEGORIES ---
    categories_to_read = [
        'MyHealth', 'MyLevel', 'MyName', 
        'VsHealth', 'VsLevel', 'VsName',
        'Attacks', 'AttackType', 'MyType', 'VsType'
    ]
    # --- END UPDATE ---

    rois = _annotations_to_rois(LABEL_DATA, include_categories=categories_to_read)
    
    if not rois:
        print(f"No labeled ROIs found for the requested categories: {categories_to_read}")
        return

    print("--- Processing ROIs ---")
    for roi in rois:
        # Scale ROI from the *label data's* base resolution to the *current* screen resolution
        scaled = _scale_roi_to_screen(roi, screen_w, screen_h)
        x1, y1, x2, y2 = scaled
        
        # guard bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(screen_w, x2), min(screen_h, y2)
        
        if x2 <= x1 or y2 <= y1:
            print(f"ROI {roi['id']} invalid after scaling: {scaled}")
            continue

        # <<< DEBUG: Draw rectangle and label on the debug image
        color = (0, 255, 0) # Green
        thickness = 2
        cv2.rectangle(debug_image, (x1, y1), (x2, y2), color, thickness)
        
        label = f"ID: {roi['id']} ({roi['category']})"
        # Put the label just above the rectangle
        cv2.putText(debug_image, label, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, thickness)
        # <<< END DEBUG

        # Crop the *original* image (RGB) for EasyOCR
        cropped_image = image[y1:y2, x1:x2]
        
        # optionally upscale to improve OCR
        cropped_image = cv2.resize(cropped_image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

        # perform OCR
        result = reader.readtext(cropped_image)
        
        print(f"ROI id={roi['id']} category={roi['category']} bbox={scaled} -> {x2-x1}x{y2-y1} px:")
        
        # --- Process and Draw Detected Text ---
        
        # <<< NEW DEBUG: Consolidate all text fragments into one string
        all_text = " ".join([res[1] for res in result])
        # <<< END NEW DEBUG
        
        if not result:
            print("  No text detected.")
        else:
            print(f"  Detected text: {all_text}")
            
        # <<< NEW DEBUG: Draw the detected OCR text below the box
        # Set text color to Yellow (BGR)
        text_color = (0, 255, 255) 
        # Set position: at the bottom-left of the box (x1, y2) + 20px padding
        text_position = (x1, y2 + 20) 
        
        cv2.putText(debug_image, 
                    all_text, 
                    text_position, 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7,  # Font scale
                    text_color, 
                    thickness)
        # <<< END NEW DEBUG
        # --- End Process and Draw ---

    print("-------------------------")

    # <<< DEBUG: Display the final image with all ROIs
    cv2.imshow("Debug ROIs", debug_image)
    print("\nDisplaying debug window with ROIs and detected text.")
    print(">>> Press 'q' in the image window to close it and continue. <<<")
    
    # Wait until 'q' is pressed to close the window
    while cv2.waitKey(1) & 0xFF != ord('q'):
        pass
    cv2.destroyAllWindows()
    # <<< END DEBUG

if __name__ == "__main__":
    read_current_progression_state()