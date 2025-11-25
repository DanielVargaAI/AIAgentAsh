import pyautogui
import numpy as np
import cv2
import easyocr
import os  # Added for template loading

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

# --- Helper Function: Load Type Templates ---

def load_templates(template_dir="type_templates"):
    """
    Loads all PNG images from a directory into a dictionary.
    e.g., "normal.png" -> {"name": "Normal", "image": <cv2_image>}
    """
    print(f"Loading templates from {template_dir}...")
    templates = {}
    # Make sure this directory exists and has your template PNGs
    if not os.path.isdir(template_dir):
        print(f"************************************************************")
        print(f"Warning: Template directory '{template_dir}' not found.")
        print(f"Please create this folder and add your type icon PNGs.")
        print(f"************************************************************")
        return {}
        
    for filename in os.listdir(template_dir):
        if filename.endswith(".png"):
            # e.g., "poison.png" -> "Poison"
            name = os.path.splitext(filename)[0].replace("_type", "").capitalize()
            filepath = os.path.join(template_dir, filename)
            # Use IMREAD_UNCHANGED to get the alpha (transparency) channel
            image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED) 
            
            if image is None:
                print(f"Warning: Could not load template {filepath}")
                continue

            # Handle images with alpha (transparency)
            if image.shape[2] == 4:
                # Create a mask from the alpha channel
                alpha = image[:, :, 3]
                # Use the BGR channels
                image = image[:, :, :3]
                templates[name] = {"image": image, "mask": alpha}
            else:
                # No alpha, use the full image and no mask
                templates[name] = {"image": image, "mask": None}
            print(f"  Loaded template: {name}")
    return templates

# --- Global Variables ---

# Load all templates from the "type_templates" folder on startup
TYPE_TEMPLATES = load_templates("type_templates")

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

# --- Core Helper Functions ---

def _build_category_map(label_data):
    """Builds a simple map of category ID to category name."""
    return {c['id']: c['name'] for c in label_data.get('categories', [])}

def _annotations_to_rois(label_data, include_categories=None):
    """
    Convert label-studio annotations (x,y,w,h) to list of ROIs (x1,y1,x2,y2).
    include_categories: list of category names to include (None => include all)
    """
    if not label_data.get('images'):
        print("Error: 'images' key missing from LABEL_DATA")
        return []
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

# --- NEW Processing Functions ---

def process_health_roi(roi_image):
    """
    Analyzes a cropped health bar image and returns the health percentage.
    """
    # Convert the cropped BGR image to HSV
    hsv_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)

    # --- Define color ranges in HSV ---
    # !!! NOTE: You will need to tune these values for your game !!!
    # Format: (Hue, Saturation, Value)
    
    # Green range (e.g., 35-75 Hue)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([75, 255, 255])
    
    # Yellow range (e.g., 20-30 Hue)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])

    # Red range (e.g., 0-10 Hue)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    
    # Empty bar background (e.g., dark grey/black)
    lower_empty = np.array([0, 0, 20])
    upper_empty = np.array([180, 50, 50])

    # --- Create masks ---
    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)
    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    red_mask = cv2.inRange(hsv_image, lower_red, upper_red)
    
    # Combine all "health" colors
    health_mask = green_mask + yellow_mask + red_mask
    
    # Create "empty" mask
    empty_mask = cv2.inRange(hsv_image, lower_empty, upper_empty)

    # --- Count pixels ---
    health_pixels = cv2.countNonZero(health_mask)
    empty_pixels = cv2.countNonZero(empty_mask)
    total_pixels = health_pixels + empty_pixels

    if total_pixels == 0:
        return 0.0  # Avoid division by zero

    return (health_pixels / total_pixels) * 100

def process_type_roi(roi_image, templates, threshold=0.8):
    """
    Finds ALL matching templates in a cropped ROI that meet the threshold.
    Returns them as a single string, sorted vertically.
    """
    found_types = [] 

    for name, template_data in templates.items():
        template_img = template_data["image"]
        mask = template_data["mask"]
        
        # Ensure template isn't larger than the ROI
        if template_img.shape[0] > roi_image.shape[0] or \
           template_img.shape[1] > roi_image.shape[1]:
            continue

        # Perform template matching
        result = cv2.matchTemplate(roi_image, template_img, cv2.TM_CCOEFF_NORMED, mask=mask)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Add ALL matches above the threshold
        if max_val > threshold:
            # store the name and its vertical (y) position
            found_types.append({"name": name, "y_pos": max_loc[1]})
    
    if not found_types:
        return "Unknown"

    # Sort the found types by their y-position (top-to-bottom)
    found_types.sort(key=lambda t: t['y_pos'])
    
    # Join all found type names
    return " / ".join([t['name'] for t in found_types])

# --- Main Application Function ---

def read_current_progression_state():
    """
    Takes a screenshot, identifies ROIs, performs appropriate processing
    (OCR, Health, Type), and shows debug windows.
    """
    # take screenshot (PIL -> numpy)
    image = pyautogui.screenshot()
    image = np.array(image) # This is RGB
    screen_h, screen_w = image.shape[:2]

    # Create a BGR copy for OpenCV drawing
    debug_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # --- Define Category Groups ---
    TEXT_CATEGORIES = ['MyName', 'VsName', 'MyLevel', 'VsLevel', 'Attacks']
    HEALTH_CATEGORIES = ['MyHealth', 'VsHealth']
    TYPE_CATEGORIES = ['MyType', 'VsType', 'AttackType']
    
    all_categories = TEXT_CATEGORIES + HEALTH_CATEGORIES + TYPE_CATEGORIES
    rois = _annotations_to_rois(LABEL_DATA, include_categories=all_categories)
    
    if not rois:
        print(f"No labeled ROIs found for the requested categories: {all_categories}")
        return

    print("--- Processing ROIs ---")
    for roi in rois:
        scaled = _scale_roi_to_screen(roi, screen_w, screen_h)
        x1, y1, x2, y2 = scaled
        
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(screen_w, x2), min(screen_h, y2)
        
        if x2 <= x1 or y2 <= y1:
            print(f"ROI {roi['id']} invalid after scaling: {scaled}")
            continue

        # --- Crop the image ---
        cropped_rgb = image[y1:y2, x1:x2]
        cropped_bgr = debug_image[y1:y2, x1:x2]

        # --- Debug text variables ---
        data_to_draw = ""
        box_color = (0, 255, 0) # Green
        data_color = (0, 0, 255) # Red (default)

        # --- Process based on Category ---
        if roi['category'] in TEXT_CATEGORIES:
            upscaled_rgb = cv2.resize(cropped_rgb, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            result = reader.readtext(upscaled_rgb)
            all_text = " ".join([res[1] for res in result])
            
            data_to_draw = all_text
            data_color = (0, 0, 255) # Red for text
            print(f"ROI id={roi['id']} ({roi['category']}) -> Text: {all_text}")
        
        elif roi['category'] in HEALTH_CATEGORIES:
            
            # <<< FIX: Slice the ROI to remove the "XP" text ---
            roi_height, roi_width = cropped_bgr.shape[:2]
            x_chop_percent = 0.18 # Tune this value (e.g., 0.18 = 18%)
            x_start = int(roi_width * x_chop_percent)
            chopped_bar_image = cropped_bgr[:, x_start:roi_width]
            # --- END FIX ---

            # <<< NEW DEBUG LINE: Display the chopped image in a new window
            cv2.imshow(f"Debug Health Chop (ID: {roi['id']})", chopped_bar_image)
            # <<< END NEW DEBUG LINE
            
            # Now, process the *chopped* image
            percent = process_health_roi(chopped_bar_image)
            
            data_to_draw = f"{percent:.1f}%"
            data_color = (0, 255, 255) # Yellow for health
            print(f"ROI id={roi['id']} ({roi['category']}) -> Health: {data_to_draw}")

        elif roi['category'] in TYPE_CATEGORIES:
            poke_type = process_type_roi(cropped_bgr, TYPE_TEMPLATES, threshold=0.7)
            
            data_to_draw = poke_type
            data_color = (255, 0, 0) # Blue for type
            print(f"ROI id={roi['id']} ({roi['category']}) -> Type: {data_to_draw}")

        # --- Draw Debug Info ---
        thickness = 2
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7

        cv2.rectangle(debug_image, (x1, y1), (x2, y2), box_color, thickness)
        
        label = f"ID: {roi['id']} ({roi['category']})"
        label_pos = (x1, y1 - 10)
        cv2.putText(debug_image, label, label_pos, font, font_scale, box_color, thickness)
        
        data_pos = (x1, y1 - 40)
        cv2.putText(debug_image, data_to_draw, data_pos, font, 
                    font_scale, data_color, thickness)

    print("-------------------------")

    cv2.imshow("Debug ROIs", debug_image)
    print("\nDisplaying debug window with ROIs and detected data.")
    print(">>> Press 'q' in the image window to close it and continue. <<<")
    
    # This waitKey loop will keep *all* imshow windows open
    while cv2.waitKey(1) & 0xFF != ord('q'):
        pass
    
    # This will destroy all windows (the main one and all chop windows)
    cv2.destroyAllWindows()

# --- Main execution ---
if __name__ == "__main__":
    read_current_progression_state()