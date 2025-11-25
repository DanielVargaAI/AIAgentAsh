import cv2
import json
import numpy as np
import easyocr
import pprint
import os

class PokerogueExtractor:
    """
    A class to extract game state information from a Pokerogue screenshot.
    
    V5.2: Fixes HP bar logic using HSV masking to ignore borders.
    """
    
    # --- Configuration for Template Matching ---
    TEMPLATE_DIR = "type_templates"
    TEMPLATE_MAP = {
        "Normal": "normal.png",
        "Fire": "fire.png",
        "Water": "water.png",
        "Ground": "help1.png"  # <-- You can rename "Ground"
    }
    MATCH_THRESHOLD = 0.8  
    
    def __init__(self, json_file):
        """
        Initializes the extractor.
        """
        # 1. Load EasyOCR
        print("Loading EasyOCR models... (This may take a moment)")
        try:
            self.reader = easyocr.Reader(['de', 'en'], gpu=False) 
            print("EasyOCR loaded successfully.")
        except Exception as e:
            print(f"Could not initialize EasyOCR. Error: {e}")
            self.reader = None

        # 2. Load and parse the layouts
        print(f"Loading layouts from {json_file}...")
        self.single_layout = {}
        self.double_layout = {}
        self._load_layouts(json_file)
        print("Layouts loaded successfully.")
        
        # 3. Load Type Templates
        print(f"Loading type templates from '{self.TEMPLATE_DIR}'...")
        self.type_templates = {}
        self._load_templates()
        print(f"Loaded {len(self.type_templates)} templates.")

    def _load_layouts(self, json_file):
        """Private method to load and parse the annotation JSON file."""
        if not os.path.exists(json_file):
            print(f"Error: JSON file not found at {json_file}")
            return
            
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        category_map = {cat['id']: cat['name'] for cat in data['categories']}
        
        TEXT_CATEGORIES = [
            'AttackAcc', 'AttackBL', 'AttackBR', 'AttackPP', 'AttackPower',
            'AttackTL', 'AttackTR', 'MyLevel', 'MyName', 'VsLevel', 'VsName'
        ]
        HP_BAR_CATEGORIES = ['MyHealth', 'VsHealth']
        IMAGE_CATEGORIES = ['AttackType', 'AttackType2', 'MyType', 'VsType']

        for ann in data['annotations']:
            img_id = ann['image_id']
            cat_id = ann['category_id']
            bbox = ann['bbox'] # [x, y, w, h]
            cat_name = category_map.get(cat_id)
            if not cat_name: continue
                
            processor_type = None
            if cat_name in TEXT_CATEGORIES: processor_type = 'text'
            elif cat_name in HP_BAR_CATEGORIES: processor_type = 'hp'
            elif cat_name in IMAGE_CATEGORIES: processor_type = 'image'
            else: continue

            layout = self.single_layout if img_id == 0 else self.double_layout
            if cat_name not in layout:
                layout[cat_name] = []
            layout[cat_name].append((bbox, processor_type))

    def _load_templates(self):
        """Private method to load template images from the TEMPLATE_DIR."""
        if not os.path.isdir(self.TEMPLATE_DIR):
            print(f"Warning: Template directory '{self.TEMPLATE_DIR}' not found.")
            return

        for type_name, filename in self.TEMPLATE_MAP.items():
            path = os.path.join(self.TEMPLATE_DIR, filename)
            if os.path.exists(path):
                # Load as grayscale for simpler matching
                template_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if template_img is not None:
                    self.type_templates[type_name] = template_img
                else:
                    print(f"Warning: Could not load template '{path}'")
            else:
                print(f"Warning: Template file not found '{path}'")

    def _process_hp_bar(self, roi):
            """
            --- UPDATED: HP Bar Logic (v5.3) ---
            Calculates HP 0.0-1.0 using HSV color masking.
            This version correctly handles dark/shadowed parts of the health bar.
            """
            if roi.size == 0:
                return 0.0

            # 1. Convert the ROI to HSV color space
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # 2. Define masks
            
            # Mask for "health" pixels (Green, Yellow, Red)
            # We define "health" as any pixel with Saturation > 50.
            # This correctly includes all shades (light and dark) of the health color.
            # (H, S, V)
            health_mask = cv2.inRange(hsv_roi, (0, 50, 20), (180, 255, 255))

            # Mask for "empty" pixels (Black/Dark Gray)
            # We define "empty" as any pixel with low Saturation (< 50) AND low Value (< 50).
            # This targets the black "empty" part of the bar.
            empty_mask = cv2.inRange(hsv_roi, (0, 0, 0), (180, 49, 49))

            # 3. Count the pixels
            # The tight bounding box means we don't need to worry about the border.
            health_pixels = cv2.countNonZero(health_mask)
            empty_pixels = cv2.countNonZero(empty_mask)
            
            # 4. Calculate the total bar pixels
            total_bar_pixels = health_pixels + empty_pixels

            if total_bar_pixels == 0:
                # Avoid division by zero, means we didn't find the bar
                return 0.0 

            # 5. Calculate the ratio
            hp_ratio = health_pixels / total_bar_pixels
            
            # Handle the full-health bar (might be 0.998...)
            # If the ratio is very close to 1, just call it 1.
            if hp_ratio > 0.95:
                hp_ratio = 1.0
                
            return round(hp_ratio, 4)

    def _extract_text_easyocr(self, roi):
        if roi.size == 0 or self.reader is None: return ""
        results = self.reader.readtext(roi, detail=0, paragraph=True)
        return ' '.join(results).strip()

    def _match_template(self, roi):
        """
        Compares the ROI against all loaded templates and returns the best match.
        """
        if roi.size == 0 or not self.type_templates:
            return "Unknown"
        
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        best_score = -1.0
        best_match = "Unknown"

        for type_name, template_img in self.type_templates.items():
            if roi_gray.shape[0] < template_img.shape[0] or roi_gray.shape[1] < template_img.shape[1]:
                continue 
                
            result = cv2.matchTemplate(roi_gray, template_img, cv2.TM_CCOEFF_NORMED)
            _min_val, max_val, _min_loc, _max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                best_match = type_name

        if best_score >= self.MATCH_THRESHOLD:
            return best_match
        else:
            return "Unknown"

    def extract_gamestate(self, frame, fight_type, debug=False):
        """
        Main public method. Extracts info from a game frame.
        """
        if self.reader is None:
            return ({"error": "EasyOCR is not initialized."}, None)
            
        if fight_type == 'single':
            layout = self.single_layout
            is_double = False
        elif fight_type == 'double':
            layout = self.double_layout
            is_double = True
        else:
            return ({"error": "Invalid fight_type. Use 'single' or 'double'."}, None)
        
        debug_frame = frame.copy() if debug else None
        results = {}

        for cat_name, annotations in layout.items():
            sorted_annotations = sorted(annotations, key=lambda ann: ann[0][1])
            
            for i, (bbox, processor_type) in enumerate(sorted_annotations):
                x, y, w, h = [int(v) for v in bbox]
                roi = frame[y:y+h, x:x+w]
                
                value = None
                display_text = ""
                
                if roi.size == 0:
                    value = None
                    display_text = "ROI_ERROR"
                elif processor_type == 'text':
                    value = self._extract_text_easyocr(roi)
                    display_text = value
                elif processor_type == 'hp':
                    value = self._process_hp_bar(roi)
                    display_text = f"HP: {value}"
                elif processor_type == 'image':
                    value = self._match_template(roi)
                    display_text = f"Type: {value}"
                
                base_key = cat_name.replace('Vs', 'vs_').replace('My', 'my_').lower()
                key = f"{base_key}_{i+1}" if is_double else base_key
                results[key] = value

                if debug:
                    cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(debug_frame, display_text, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return results, debug_frame

# --- Example Usage (No changes) ---
if __name__ == "__main__":
    
    JSON_PATH = 'resultsLIVE.json'

    SINGLE_IMAGE_PATH = '15_11_testscreen.png' # Your single battle image
    DOUBLE_IMAGE_PATH = 'img_Double_Screenshot 2025-11-04 161234.png' # Your double battle image
    
    extractor = PokerogueExtractor(JSON_PATH)
    
    print("\n--- Extracting Single Fight State (Debug Mode) ---")
    img_single = cv2.imread(SINGLE_IMAGE_PATH)
    if img_single is not None:
        state_single, debug_frame_single = extractor.extract_gamestate(
            img_single, 'single', debug=True
        )
        print("Results:")
        pprint.pprint(state_single)
        
        if debug_frame_single is not None:
            print("\nShowing debug window... Press any key to close.")
            h, w = debug_frame_single.shape[:2]
            cv2.imshow("Debug - Single Fight", cv2.resize(debug_frame_single, (w // 2, h // 2)))
            cv2.waitKey(0)
    else:
        print(f"Error: Could not load single fight image at {SINGLE_IMAGE_PATH}")

    print("\n--- Extracting Double Fight State (Debug Mode) ---")
    img_double = cv2.imread(DOUBLE_IMAGE_PATH)
    if img_double is not None:
        state_double, debug_frame_double = extractor.extract_gamestate(
            img_double, 'double', debug=True
        )
        print("Results:")
        pprint.pprint(state_double)
        
        if debug_frame_double is not None:
            print("\nShowing debug window... Press any key to close.")
            h, w = debug_frame_double.shape[:2]
            cv2.imshow("Debug - Double Fight", cv2.resize(debug_frame_double, (w // 2, h // 2)))
            cv2.waitKey(0)
    else:
        print(f"Error: Could not load double fight image at {DOUBLE_IMAGE_PATH}")

    cv2.destroyAllWindows()