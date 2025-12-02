import cv2
import json
import numpy as np
import easyocr
import pprint
import os

class PokerogueExtractor:
    """
    A class to extract game state information from a Pokerogue screenshot.
    
    V4: Includes a debug mode to visualize ROIs and detected text.
    """
    
    def __init__(self, json_file):
        """
        Initializes the extractor.
        
        Args:
            json_file (str): Path to the Label Studio JSON file.
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
        """Calculates the HP percentage (0.0 to 1.0) from an HP bar ROI."""
        if roi.size == 0: return 0.0
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _ , thresholded = cv2.threshold(gray_roi, 25, 255, cv2.THRESH_BINARY)
        colored_pixels = cv2.countNonZero(thresholded)
        total_pixels = roi.shape[0] * roi.shape[1]
        if total_pixels == 0: return 0.0
        return round(colored_pixels / total_pixels, 4)

    def _extract_text_easyocr(self, roi):
        """Extracts text from an ROI using the initialized EasyOCR reader."""
        if roi.size == 0 or self.reader is None: return ""
        results = self.reader.readtext(roi, detail=0, paragraph=True)
        return ' '.join(results).strip()

    def extract_gamestate(self, frame, fight_type, debug=False):
        """
        This is the main public method. Extracts info from a game frame.

        Args:
            frame (np.array): The current game screenshot (from cv2.imread).
            fight_type (str): 'single' or 'double'.
            debug (bool): If True, returns a frame with debug info drawn on it.

        Returns:
            tuple: (results_dict, debug_frame)
                   If debug=False, debug_frame will be None.
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
        
        # --- DEBUG: Create a copy of the frame to draw on ---
        debug_frame = None
        if debug:
            debug_frame = frame.copy()

        results = {}

        for cat_name, annotations in layout.items():
            
            # Sort by Y-coordinate to distinguish top/bottom pokemon
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
                    value = roi 
                    display_text = "IMAGE_TEMPLATE"
                
                # Generate structured keys
                base_key = cat_name.replace('Vs', 'vs_').replace('My', 'my_').lower()
                key = f"{base_key}_{i+1}" if is_double else base_key
                results[key] = value

                # --- DEBUG: Draw info on the debug_frame ---
                if debug:
                    # Draw the bounding box
                    cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # Draw the detected text just above the box
                    cv2.putText(
                        debug_frame, 
                        display_text, 
                        (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6,          # Font scale
                        (0, 255, 0),  # Color (green)
                        2             # Thickness
                    )
        
        return results, debug_frame

# --- Example Usage ---
# This block runs only when you execute this script directly
if __name__ == "__main__":
    
    JSON_PATH = 'result.json'
    SINGLE_IMAGE_PATH = 'image_f9c18c.png'
    DOUBLE_IMAGE_PATH = 'image_f9c202.png'
    
    # 1. Instantiate the class
    extractor = PokerogueExtractor(JSON_PATH)
    
    # --- 2. Test single fight ---
    print("\n--- 👾 Extracting Single Fight State (Debug Mode) ---")
    img_single = cv2.imread(SINGLE_IMAGE_PATH)
    if img_single is not None:
        # Call with debug=True
        state_single, debug_frame_single = extractor.extract_gamestate(
            img_single, 'single', debug=True
        )
        
        print("Results:")
        pprint.pprint(state_single)
        
        # Show the debug frame
        if debug_frame_single is not None:
            print("\nShowing debug window for Single Fight. Press any key to close.")
            # Resize for better viewing if it's a large monitor
            h, w = debug_frame_single.shape[:2]
            cv2.imshow("Debug - Single Fight", cv2.resize(debug_frame_single, (w // 2, h // 2)))
            cv2.waitKey(0)
    else:
        print(f"Error: Could not load single fight image at {SINGLE_IMAGE_PATH}")

    # --- 3. Test double fight ---
    print("\n--- 👾👾 Extracting Double Fight State (Debug Mode) ---")
    img_double = cv2.imread(DOUBLE_IMAGE_PATH)
    if img_double is not None:
        # Call with debug=True
        state_double, debug_frame_double = extractor.extract_gamestate(
            img_double, 'double', debug=True
        )
        
        print("Results:")
        pprint.pprint(state_double)

        # Show the debug frame
        if debug_frame_double is not None:
            print("\nShowing debug window for Double Fight. Press any key to close.")
            h, w = debug_frame_double.shape[:2]
            cv2.imshow("Debug - Double Fight", cv2.resize(debug_frame_double, (w // 2, h // 2)))
            cv2.waitKey(0)
    else:
        print(f"Error: Could not load double fight image at {DOUBLE_IMAGE_PATH}")

    cv2.destroyAllWindows()