import cv2
import json
import numpy as np
import easyocr
import pprint
import os
import re

class PokerogueExtractor:
    """
    V2 Extractor for PokeRogue.
    Features: BGR Type detection, HSV HP calculation, OCR Name cleaning, and Status detection.
    """
    
    # --- CONFIGURATION: COLORS (BGR Format) ---
    # Use MS Paint to pick these colors if detection fails. OpenCV uses (Blue, Green, Red).
    TYPE_BGR_MAP = {
        "Normal": (168, 168, 168), "Fire": (80, 48, 240), "Water": (216, 120, 48),
        "Grass": (64, 176, 88), "Electric": (40, 208, 248), "Ice": (208, 208, 96),
        "Fighting": (48, 64, 192), "Poison": (176, 80, 160), "Ground": (80, 152, 216),
        "Flying": (168, 144, 104), "Psychic": (120, 88, 248), "Bug": (80, 176, 152),
        "Rock": (112, 168, 184), "Ghost": (128, 96, 80), "Dragon": (152, 80, 72),
        "Dark": (112, 112, 112), "Steel": (168, 168, 184), "Fairy": (208, 152, 232)
    }

    # Approximate colors for Status ailments (BGR)
    STATUS_BGR_MAP = {
        "PAR": (0, 255, 255),    # Yellow
        "BRN": (0, 0, 255),      # Red
        "FRZ": (255, 200, 100),  # Light Blue
        "PSN": (255, 0, 255),    # Purple
        "SLP": (192, 192, 192)   # Grey
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
        
        # 3. Pre-calculate numpy arrays for fast color matching
        self.type_names = list(self.TYPE_BGR_MAP.keys())
        self.type_colors_np = np.array(list(self.TYPE_BGR_MAP.values()), dtype=np.uint8)

        self.status_names = list(self.STATUS_BGR_MAP.keys())
        self.status_colors_np = np.array(list(self.STATUS_BGR_MAP.values()), dtype=np.uint8)


    def _load_layouts(self, json_file):
        """Private method to load and parse the annotation JSON file."""
        if not os.path.exists(json_file):
            print(f"Error: JSON file not found at {json_file}")
            return
            
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        category_map = {cat['id']: cat['name'] for cat in data['categories']}
        
        # Define how to process each label found in your JSON
        TEXT_CATEGORIES = [
            'AttackAcc', 'AttackBL', 'AttackBR', 'AttackPP', 'AttackPower',
            'AttackTL', 'AttackTR', 'MyLevel', 'MyName', 'VsLevel', 'VsName'
        ]
        HP_BAR_CATEGORIES = ['MyHealth', 'VsHealth']
        TYPE_IMAGE_CATEGORIES = ['AttackType', 'AttackType2', 'MyType', 'VsType']
        STATUS_CATEGORIES = ['MyStatus', 'VsStatus'] # NEW for V2

        for ann in data['annotations']:
            img_id = ann['image_id']
            cat_id = ann['category_id']
            bbox = ann['bbox'] # [x, y, w, h]
            cat_name = category_map.get(cat_id)
            if not cat_name: continue
                
            processor_type = None
            if cat_name in TEXT_CATEGORIES: processor_type = 'text'
            elif cat_name in HP_BAR_CATEGORIES: processor_type = 'hp'
            elif cat_name in TYPE_IMAGE_CATEGORIES: processor_type = 'type_image'
            elif cat_name in STATUS_CATEGORIES: processor_type = 'status_image'
            else: continue

            layout = self.single_layout if img_id == 0 else self.double_layout
            if cat_name not in layout:
                layout[cat_name] = []
            layout[cat_name].append((bbox, processor_type))


    def _process_hp_bar(self, roi):
        """Calculates HP 0.0-1.0 using HSV masking."""
        if roi.size == 0: return 0.0
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        # Green/Yellow/Red ranges for HP
        health_mask = cv2.inRange(hsv_roi, (0, 40, 20), (180, 255, 255))
        # Dark grey background of empty bar
        empty_mask = cv2.inRange(hsv_roi, (0, 0, 0), (180, 60, 80))
        
        health_pixels = cv2.countNonZero(health_mask)
        empty_pixels = cv2.countNonZero(empty_mask)
        total_bar_pixels = health_pixels + empty_pixels
        
        if total_bar_pixels == 0: return 0.0 
        hp_ratio = health_pixels / total_bar_pixels
        if hp_ratio > 0.96: hp_ratio = 1.0
        return round(hp_ratio, 4)

    def _clean_name(self, text):
        """
        V2 Update: Removes gender symbols and garbage characters.
        e.g., 'Pikachu♂' -> 'Pikachu'
        """
        # Allow letters, numbers, hyphens, apostrophes. Remove everything else.
        cleaned = re.sub(r'[^\w\s\-\']', '', text)
        return cleaned.strip()

    def _extract_text_easyocr(self, roi):
        if roi.size == 0 or self.reader is None: return ""
        results = self.reader.readtext(roi, detail=0, paragraph=True)
        raw_text = ' '.join(results)
        return self._clean_name(raw_text)

    def _get_closest_color(self, bgr_color, color_map_np, names_list):
        """Generic helper to find nearest color in a map."""
        pixel_color = np.array(bgr_color, dtype=np.uint8)
        distances = np.sum((color_map_np - pixel_color)**2, axis=1)
        min_dist = np.min(distances)
        closest_index = np.argmin(distances)
        return names_list[closest_index], min_dist

    def _identify_types(self, roi):
        """Identifies Single or Dual types based on BGR color."""
        if roi.size == 0: return "Unknown"
        h, w = roi.shape[:2]
        
        # Sample two points to catch dual types
        p1 = roi[int(h * 0.5), int(w * 0.25)] # Left side
        p2 = roi[int(h * 0.5), int(w * 0.75)] # Right side

        type1, _ = self._get_closest_color(p1, self.type_colors_np, self.type_names)
        type2, _ = self._get_closest_color(p2, self.type_colors_np, self.type_names)
        
        if type1 != type2:
            return f"{type1}/{type2}"
        return type1

    def _identify_status(self, roi):
        """
        V2 NEW: Checks if a status condition exists based on color.
        Returns 'OK' if no status is detected (background color).
        """
        if roi.size == 0: return "OK"
        
        # Take the center pixel of the status icon
        h, w = roi.shape[:2]
        center_pixel = roi[int(h/2), int(w/2)]
        
        status, dist = self._get_closest_color(center_pixel, self.status_colors_np, self.status_names)
        
        # Threshold: If the color is too far from any known status color, assume it's empty/background
        # 2000 is an arbitrary threshold for Squared Euclidean distance
        if dist > 3000: 
            return "OK"
        return status

    def extract_gamestate(self, frame, fight_type, debug=False):
        """
        Main method to extract V2 Game State.
        """
        if self.reader is None:
            return ({"error": "EasyOCR is not initialized."}, None)
            
        layout = self.single_layout if fight_type == 'single' else self.double_layout
        is_double = (fight_type == 'double')
        
        debug_frame = frame.copy() if debug else None
        results = {}

        for cat_name, annotations in layout.items():
            # Sort by Y position so top items come first (helpful for move lists)
            sorted_annotations = sorted(annotations, key=lambda ann: ann[0][1])
            
            for i, (bbox, processor_type) in enumerate(sorted_annotations):
                x, y, w, h = [int(v) for v in bbox]
                roi = frame[y:y+h, x:x+w]
                
                value = None
                display_text = ""
                
                if roi.size == 0:
                    value = None
                elif processor_type == 'text':
                    value = self._extract_text_easyocr(roi)
                    display_text = value
                elif processor_type == 'hp':
                    value = self._process_hp_bar(roi)
                    display_text = f"{value*100:.0f}%"
                elif processor_type == 'type_image':
                    value = self._identify_types(roi)
                    display_text = value
                elif processor_type == 'status_image':
                    value = self._identify_status(roi)
                    display_text = value
                
                # Key generation (e.g., vs_name, vs_name_2)
                base_key = cat_name.replace('Vs', 'vs_').replace('My', 'my_').lower()
                key = f"{base_key}_{i+1}" if is_double else base_key
                
                results[key] = value

                if debug:
                    color = (0, 255, 0) # Green
                    if processor_type == 'status_image' and value != 'OK': color = (0, 0, 255) # Red for status
                    cv2.rectangle(debug_frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(debug_frame, str(display_text), (x, y - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return results, debug_frame

# --- Example Usage ---
if __name__ == "__main__":
    
    JSON_PATH = 'resultsLIVE.json'
    # Ensure your JSON has 'MyStatus' and 'VsStatus' categories now!

    SINGLE_IMAGE_PATH = '15_11_testscreen.png' 
    DOUBLE_IMAGE_PATH = 'img_Double_Screenshot 2025-11-04 161234.png'
    
    extractor = PokerogueExtractor(JSON_PATH)
    
    print("\n--- 👾 Extracting V2 Single Fight State ---")
    img_single = cv2.imread(SINGLE_IMAGE_PATH)
    if img_single is not None:
        state, debug_img = extractor.extract_gamestate(img_single, 'single', debug=True)
        pprint.pprint(state)
        cv2.imshow("V2 Debug", debug_img)
        cv2.waitKey(0)
    else:
        print(f"Error loading {SINGLE_IMAGE_PATH}")

    cv2.destroyAllWindows()