import cv2
import json
import numpy as np
import easyocr
import pprint
import os

class PokerogueExtractor:
    """
    A class to extract game state information from a Pokerogue screenshot.

    """
    
    TYPE_BGR_MAP = {
        "Normal": (168, 168, 168),
        "Fire": (80, 48, 240),
        "Water": (216, 120, 48),
        "Grass": (64, 176, 88),
        "Electric": (40, 208, 248),
        "Ice": (208, 208, 96),
        "Fighting": (48, 64, 192),
        "Poison": (176, 80, 160),
        "Ground": (80, 152, 216),
        "Flying": (168, 144, 104),
        "Psychic": (120, 88, 248),
        "Bug": (80, 176, 152),
        "Rock": (112, 168, 184),
        "Ghost": (128, 96, 80),
        "Dragon": (152, 80, 72),
        "Dark": (112, 112, 112),
        "Steel": (168, 168, 184),
        "Fairy": (208, 152, 232)
    }
    
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
        
        # 3. --- NEW: Create a pre-calculated numpy array for BGR map ---
        # This makes the color comparison math much faster.
        self.type_names = list(self.TYPE_BGR_MAP.keys())
        self.type_colors_np = np.array(list(self.TYPE_BGR_MAP.values()), dtype=np.uint8)


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


    def _process_hp_bar(self, roi):
        """Calculates HP 0.0-1.0 using HSV masking (v5.3 logic)."""
        if roi.size == 0: return 0.0
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        health_mask = cv2.inRange(hsv_roi, (0, 50, 20), (180, 255, 255))
        empty_mask = cv2.inRange(hsv_roi, (0, 0, 0), (180, 49, 49))
        
        health_pixels = cv2.countNonZero(health_mask)
        empty_pixels = cv2.countNonZero(empty_mask)
        total_bar_pixels = health_pixels + empty_pixels
        
        if total_bar_pixels == 0: return 0.0 
        hp_ratio = health_pixels / total_bar_pixels
        if hp_ratio > 0.96: hp_ratio = 1.0
        return round(hp_ratio, 4)

    def _extract_text_easyocr(self, roi):
        if roi.size == 0 or self.reader is None: return ""
        results = self.reader.readtext(roi, detail=0, paragraph=True)
        return ' '.join(results).strip()

    def _get_type_from_bgr(self, bgr_color):
        """
        --- NEW: Nearest Color Finder ---
        Finds the closest type from our TYPE_BGR_MAP using fast numpy math.
        """
        # Convert the single pixel to a numpy array
        pixel_color = np.array(bgr_color, dtype=np.uint8)
        
        # Calculate the Sum of Squared Differences (SSD)
        # This finds the "distance" between our pixel's color
        # and all 18 "key" colors at once.
        distances = np.sum((self.type_colors_np - pixel_color)**2, axis=1)
        
        # Find the index of the smallest distance
        closest_index = np.argmin(distances)
        
        # Return the type name at that index
        return self.type_names[closest_index]

    def _identify_types(self, roi):
        """
        --- UPDATED: Type Identification Logic ---
        Checks for dual types by sampling two points.
        Now uses the new BGR-based finder.
        """
        if roi.size == 0:
            return "Unknown"
        
        # We don't need HSV anymore, just use the BGR ROI
        h, w = roi.shape[:2]

        # 1. Define sample points
        # Point 1: Top-left quadrant (for type 1)
        p1_coords = (int(h * 0.25), int(w * 0.5))
        # Point 2: Bottom-right quadrant (for type 2)
        p2_coords = (int(h * 0.75), int(w * 0.5))
        
        # 2. Get BGR values for both points
        # Note: OpenCV is [y, x] for indexing
        bgr1 = roi[p1_coords[0], p1_coords[1]]
        bgr2 = roi[p2_coords[0], p2_coords[1]]

        # 3. Identify the type for each point
        type1 = self._get_type_from_bgr(bgr1)
        type2 = self._get_type_from_bgr(bgr2)
        
        # 4. Check if they are different
        if type1 != type2:
            return f"{type1}/{type2}"
        else:
            return type1 # They are the same, just return one.

    def extract_gamestate(self, frame, fight_type, debug=False):
        """
        Main public method. Extracts info from a game frame.
        """
        if self.reader is None:
            return ({"error": "EasyOCR is not initialized."}, None)
            
        layout = self.single_layout if fight_type == 'single' else self.double_layout
        is_double = (fight_type == 'double')
        if fight_type not in ['single', 'double']:
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
                    value = None; display_text = "ROI_ERROR"
                elif processor_type == 'text':
                    value = self._extract_text_easyocr(roi); display_text = value
                elif processor_type == 'hp':
                    value = self._process_hp_bar(roi); display_text = f"HP: {value}"
                elif processor_type == 'image':
                    # --- UPDATED: Call new color ID function ---
                    value = self._identify_types(roi)
                    display_text = f"Type: {value}"
                
                base_key = cat_name.replace('Vs', 'vs_').replace('My', 'my_').lower()
                key = f"{base_key}_{i+1}" if is_double else base_key
                results[key] = value

                if debug:
                    cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(debug_frame, display_text, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return results, debug_frame

# --- Example Usage (No changes needed) ---
if __name__ == "__main__":
    
    JSON_PATH = 'resultsLIVE.json'

    SINGLE_IMAGE_PATH = '15_11_testscreen.png' # Your single battle image
    DOUBLE_IMAGE_PATH = 'img_Double_Screenshot 2025-11-04 161234.png' # Your double battle image
    
    extractor = PokerogueExtractor(JSON_PATH)
    
    print("\n--- 👾 Extracting Single Fight State (Debug Mode) ---")
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

    print("\n--- 👾👾 Extracting Double Fight State (Debug Mode) ---")
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