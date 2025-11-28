import cv2
import json
import numpy as np
import easyocr
import pprint
import os

class PokerogueExtractor:
    """
    A class to extract game state information from a Pokerogue screenshot.

    Initializes by loading EasyOCR models and parsing the label layout JSON.
    """
    
    def __init__(self, json_file):
        """
        Initializes the extractor.
        
        Args:
            json_file (str): Path to the Label Studio JSON file.
        """
        # 1. Load EasyOCR (this is the heavy part, done once)
        print("Loading EasyOCR models... (This may take a moment)")
        try:
            # Set gpu=True if you have a CUDA-compatible GPU
            self.reader = easyocr.Reader(['de', 'en'], gpu=False) 
            print("EasyOCR loaded successfully.")
        except Exception as e:
            print(f"Could not initialize EasyOCR. Error: {e}")
            self.reader = None

        # 2. Load and parse the layouts from the JSON
        print(f"Loading layouts from {json_file}...")
        self.single_layout = {}
        self.double_layout = {}
        self._load_layouts(json_file)
        print("Layouts loaded successfully.")

    def _load_layouts(self, json_file):
        """
        Private method to load and parse the annotation JSON file.
        Populates self.single_layout and self.double_layout.
        """
        if not os.path.exists(json_file):
            print(f"Error: JSON file not found at {json_file}")
            return
            
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        category_map = {cat['id']: cat['name'] for cat in data['categories']}
        
        # Define processor types
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
            if not cat_name:
                continue
                
            # Determine the processor type
            processor_type = None
            if cat_name in TEXT_CATEGORIES:
                processor_type = 'text'
            elif cat_name in HP_BAR_CATEGORIES:
                processor_type = 'hp'
            elif cat_name in IMAGE_CATEGORIES:
                processor_type = 'image'
            else:
                continue

            # Check if this annotation is for single (0) or double (1)
            # This relies on your JSON's image_id
            layout = self.single_layout if img_id == 0 else self.double_layout
            
            if cat_name not in layout:
                layout[cat_name] = []
                
            # Store the (bbox, processor_type) tuple
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
        if roi.size == 0 or self.reader is None:
            return ""
        results = self.reader.readtext(roi, detail=0, paragraph=True)
        return ' '.join(results).strip()

    def extract_gamestate(self, frame, fight_type):
        """
        This is the main public method.
        
        It extracts all information from a game frame based on the fight type.

        Args:
            frame (np.array): The current game screenshot (from cv2.imread).
            fight_type (str): 'single' or 'double'.

        Returns:
            dict: A structured dictionary of the game state.
        """
        if self.reader is None:
            return {"error": "EasyOCR is not initialized."}
            
        if fight_type == 'single':
            layout = self.single_layout
            is_double = False
        elif fight_type == 'double':
            layout = self.double_layout
            is_double = True
        else:
            return {"error": "Invalid fight_type. Use 'single' or 'double'."}
        
        results = {}

        # Process each category in the layout (e.g., 'VsName', 'MyHealth')
        for cat_name, annotations in layout.items():
            
            # --- THIS IS THE KEY LOGIC YOU REQUESTED ---
            # Sort annotations by Y-coordinate (bbox[1])
            # The "top" pokemon (y=smaller) will be first (index 0).
            sorted_annotations = sorted(annotations, key=lambda ann: ann[0][1])
            
            # Process each annotation in its sorted order
            for i, (bbox, processor_type) in enumerate(sorted_annotations):
                x, y, w, h = [int(v) for v in bbox]
                roi = frame[y:y+h, x:x+w]
                
                value = None
                if roi.size == 0:
                    value = None
                elif processor_type == 'text':
                    value = self._extract_text_easyocr(roi)
                elif processor_type == 'hp':
                    value = self._process_hp_bar(roi)
                elif processor_type == 'image':
                    value = roi # Return the image region for template matching
                
                # --- NEW: Generate structured keys ---
                # 'VsName' -> 'vs_name'
                # 'MyHealth' -> 'my_health'
                base_key = cat_name.replace('Vs', 'vs_').replace('My', 'my_').lower()
                
                if is_double:
                    # For doubles, append _1 or _2
                    # i=0 is the top one (pokemon_1)
                    # i=1 is the bottom one (pokemon_2)
                    key = f"{base_key}_{i+1}"
                else:
                    # For singles, just use the base key
                    key = base_key

                results[key] = value

        return results

# --- Example Usage ---
# This block runs only when you execute this script directly
if __name__ == "__main__":
    
    JSON_PATH = 'resultsLIVE.json'
    SINGLE_IMAGE_PATH = 'img_Single_Screenshot 2025-11-09 154025.png' # Your single battle image
    DOUBLE_IMAGE_PATH = 'img_Double_Screenshot 2025-11-04 161234.png' # Your double battle image
    
    # 1. Instantiate the class (loads models and layouts ONCE)
    extractor = PokerogueExtractor(JSON_PATH)
    
    # 2. Test single fight
    print("\n--- 👾 Extracting Single Fight State ---")
    img_single = cv2.imread(SINGLE_IMAGE_PATH)
    if img_single is not None:
        state_single = extractor.extract_gamestate(img_single, 'single')
        pprint.pprint(state_single)
    else:
        print(f"Error: Could not load single fight image at {SINGLE_IMAGE_PATH}")

    # 3. Test double fight
    print("\n--- 👾👾 Extracting Double Fight State ---")
    img_double = cv2.imread(DOUBLE_IMAGE_PATH)
    if img_double is not None:
        state_double = extractor.extract_gamestate(img_double, 'double')
        pprint.pprint(state_double)
        
        # Check for missing labels
        if 'my_name_1' not in state_double:
            print("\n*** ⚠️ NOTE ***")
            print("Your 'result.json' is missing 'MyName' labels for the double battle (image_id: 1).")
            print("The script is working, but it can't extract what isn't labeled.")
            print("To fix this, add labels for 'MyName' on your double battle image in Label Studio and re-export the JSON.")
    else:
        print(f"Error: Could not load double fight image at {DOUBLE_IMAGE_PATH}")