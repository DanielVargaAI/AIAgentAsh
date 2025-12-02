import cv2
import json
import numpy as np
import easyocr
import pprint
import os
import re
import time
import sys
from datetime import datetime

class PokerogueExtractor:
    """
    V3.1 Extractor for PokeRogue.
    - FIX: Name Cleaning is now specific. Only Pokemon Names have the last char removed (Gender fix).
      Attack names are left intact.
    - CONFIG: Base Resolution set to 1440p (2560x1440).
    - FEATURE: Auto-Scaling (Downscales for 1080p, Upscales for 4k).
    - FEATURE: Batch Processing.
    """
    
    # --- CONFIGURATION: RESOLUTION ---
    # Set to 1440p as per your annotation source.
    BASE_WIDTH = 2560
    BASE_HEIGHT = 1440

    # --- CONFIGURATION: COLORS (BGR Format) ---
    TYPE_BGR_MAP = {
        "Normal":   (120, 168, 168), "Fire":     (48, 128, 240),
        "Water":    (240, 144, 104), "Grass":    (80, 200, 120),
        "Electric": (48, 208, 248),  "Ice":      (216, 216, 152),
        "Fighting": (40, 48, 192),   "Poison":   (160, 64, 160),
        "Ground":   (104, 192, 224), "Flying":   (240, 144, 168),
        "Psychic":  (136, 88, 248),  "Bug":      (32, 184, 168),
        "Rock":     (56, 160, 184),  "Ghost":    (152, 88, 112),
        "Dragon":   (248, 56, 112),  "Dark":     (72, 88, 112),
        "Steel":    (208, 184, 184), "Fairy":    (172, 153, 238),
        "Stellar":  (255, 255, 255)
    }

    STATUS_BGR_MAP = {
        "PAR": (0, 255, 255),    "BRN": (0, 0, 255),
        "FRZ": (255, 200, 100),  "PSN": (255, 0, 255),
        "SLP": (192, 192, 192)
    }
    
    def __init__(self, json_file):
        print("Loading EasyOCR models... (One-time setup)")
        try:
            self.reader = easyocr.Reader(['en'], gpu=False)
            print("EasyOCR loaded.")
        except Exception as e:
            print(f"Error initializing EasyOCR: {e}")
            self.reader = None

        self.single_layout = {}
        self.double_layout = {}
        self._load_layouts(json_file)
        
        self.type_names = list(self.TYPE_BGR_MAP.keys())
        self.type_colors_np = np.array(list(self.TYPE_BGR_MAP.values()), dtype=np.uint8)
        self.status_names = list(self.STATUS_BGR_MAP.keys())
        self.status_colors_np = np.array(list(self.STATUS_BGR_MAP.values()), dtype=np.uint8)


    def _load_layouts(self, json_file):
        if not os.path.exists(json_file):
            print(f"Error: JSON file not found at {json_file}")
            return
            
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        category_map = {cat['id']: cat['name'] for cat in data['categories']}
        
        NAME_CATEGORIES = ['MyName', 'VsName', 'AttackTL', 'AttackTR', 'AttackBL', 'AttackBR']
        PP_CATEGORIES = ['AttackPP'] 
        HP_CATEGORIES = ['MyHealth', 'VsHealth']
        TYPE_CATEGORIES = ['MyType', 'VsType']
        STATUS_CATEGORIES = ['MyStatus', 'VsStatus']

        for ann in data['annotations']:
            cat_name = category_map.get(ann['category_id'])
            if not cat_name: continue
                
            processor_type = None
            if cat_name in NAME_CATEGORIES: processor_type = 'text_name'
            elif cat_name in PP_CATEGORIES: processor_type = 'text_pp'
            elif cat_name in HP_CATEGORIES: processor_type = 'hp'
            elif cat_name in TYPE_CATEGORIES: processor_type = 'type_image'
            elif cat_name in STATUS_CATEGORIES: processor_type = 'status_image'
            
            if processor_type is None: continue

            layout = self.single_layout if ann['image_id'] == 0 else self.double_layout
            if cat_name not in layout:
                layout[cat_name] = []
            layout[cat_name].append((ann['bbox'], processor_type))


    def _process_hp_bar(self, roi):
        if roi.size == 0: return 0.0
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        health_mask = cv2.inRange(hsv, (0, 40, 20), (180, 255, 255))
        empty_mask = cv2.inRange(hsv, (0, 0, 0), (180, 60, 80))
        total = cv2.countNonZero(health_mask) + cv2.countNonZero(empty_mask)
        if total == 0: return 0.0 
        return round(min(cv2.countNonZero(health_mask) / total, 1.0), 4)

    def _process_pp(self, roi):
        if roi.size == 0 or self.reader is None: return 0.0
        try:
            results = self.reader.readtext(roi, allowlist='0123456789/', detail=0)
            text = "".join(results).replace(" ", "")
            if "/" in text:
                parts = text.split("/")
                if len(parts) == 2 and parts[1] != "":
                    return round(float(parts[0]) / float(parts[1]), 4)
            return 0.0
        except:
            return 0.0

    def _clean_name(self, text, cut_last_char=False):
        """
        Cleans text.
        cut_last_char=True -> Removes the last character (Use for Pokemon Names to remove Gender symbol).
        cut_last_char=False -> Keeps text intact (Use for Attacks).
        """
        text = re.sub(r'[^\w\s\-\']', '', text).strip()
        if cut_last_char and len(text) > 3: 
            text = text[:-1] 
        return text.strip()

    def _extract_text(self, roi, cut_last_char=False):
        if roi.size == 0 or self.reader is None: return ""
        results = self.reader.readtext(roi, detail=0)
        return self._clean_name(' '.join(results), cut_last_char=cut_last_char)

    def _get_closest_color(self, bgr, map_np, names):
        dist = np.sum((map_np - np.array(bgr, dtype=np.uint8))**2, axis=1)
        return names[np.argmin(dist)], np.min(dist)

    def _identify_types(self, roi, debug_mode=False):
        if roi.size == 0: return "Unknown"
        h, w = roi.shape[:2]

        # 60% Center Crop
        margin_y = int(h * 0.20) 
        margin_x = int(w * 0.20)
        cropped = roi[margin_y : h - margin_y, margin_x : w - margin_x]
        
        if cropped.size == 0: return "Unknown"

        h_c, w_c = cropped.shape[:2]
        top_slice = cropped[0 : int(h_c * 0.35), :]
        bot_slice = cropped[int(h_c * 0.65) : h_c, :]

        if top_slice.size == 0 or bot_slice.size == 0: return "Unknown"

        color_top = np.median(top_slice, axis=(0,1))
        color_bot = np.median(bot_slice, axis=(0,1))

        t1, _ = self._get_closest_color(color_top, self.type_colors_np, self.type_names)
        t2, _ = self._get_closest_color(color_bot, self.type_colors_np, self.type_names)

        return t1 if t1 == t2 else f"{t1}/{t2}"

    def _identify_status(self, roi):
        if roi.size == 0: return "OK"
        h, w = roi.shape[:2]
        center = roi[int(h/2), int(w/2)]
        status, dist = self._get_closest_color(center, self.status_colors_np, self.status_names)
        return "OK" if dist > 3000 else status

    def extract_gamestate(self, frame, fight_type, debug=False):
        """
        Extracts game state with Auto-Resolution Scaling.
        """
        if self.reader is None: return ({"error": "EasyOCR missing"}, None)
        
        # --- RESOLUTION CHECK ---
        curr_h, curr_w = frame.shape[:2]
        scale_x = curr_w / self.BASE_WIDTH
        scale_y = curr_h / self.BASE_HEIGHT
        needs_scaling = abs(scale_x - 1.0) > 0.01 or abs(scale_y - 1.0) > 0.01

        layout = self.single_layout if fight_type == 'single' else self.double_layout
        is_double = (fight_type == 'double')
        results = {}
        debug_frame = frame.copy() if debug else None

        for cat, anns in layout.items():
            anns = sorted(anns, key=lambda a: (a[0][1], a[0][0])) 
            
            for i, (bbox, p_type) in enumerate(anns):
                # Original Coordinates (from 1440p JSON)
                x, y, w, h = bbox
                
                # --- APPLY SCALING ---
                if needs_scaling:
                    x = int(x * scale_x); y = int(y * scale_y)
                    w = int(w * scale_x); h = int(h * scale_y)
                else:
                    x, y, w, h = int(x), int(y), int(w), int(h)
                
                # Safety Clamp
                x = max(0, min(x, curr_w - 1)); y = max(0, min(y, curr_h - 1))
                w = min(w, curr_w - x); h = min(h, curr_h - y)

                roi = frame[y:y+h, x:x+w]
                val = None
                
                if roi.size == 0:
                    val = None
                elif p_type == 'text_name': 
                    # --- NEW: Check if it is a Pokemon name to decide on cleaning ---
                    is_pokemon_name = cat in ['MyName', 'VsName']
                    val = self._extract_text(roi, cut_last_char=is_pokemon_name)
                    
                elif p_type == 'text_pp': val = self._process_pp(roi)
                elif p_type == 'hp': val = self._process_hp_bar(roi)
                elif p_type == 'type_image': val = self._identify_types(roi, debug_mode=debug) 
                elif p_type == 'status_image': val = self._identify_status(roi)
                
                key_base = cat.replace('Vs', 'vs_').replace('My', 'my_').lower()
                
                if cat == 'AttackTL': key = "attack_name_1"
                elif cat == 'AttackTR': key = "attack_name_2"
                elif cat == 'AttackBL': key = "attack_name_3"
                elif cat == 'AttackBR': key = "attack_name_4"
                elif 'AttackPP' in cat: key = f"attack_pp_{i+1}"
                else: key = f"{key_base}_{i+1}" if is_double else key_base
                
                results[key] = val

                if debug:
                    label = f"{val:.2f}" if isinstance(val, float) else str(val)
                    cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0,255,0), 1)
                    cv2.putText(debug_frame, label, (x, y-5), 0, 0.4, (0,255,0), 1)
                    if p_type == 'type_image':
                         m_y = int(h * 0.2); m_x = int(w * 0.2)
                         cv2.rectangle(debug_frame, (x+m_x, y+m_y), (x+w-m_x, y+h-m_y), (255,0,0), 1)

        return results, debug_frame

    def save_snapshot(self, state, debug_image, output_folder, original_filename):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        base_name = os.path.splitext(original_filename)[0]
        img_path = os.path.join(output_folder, f"{base_name}_debug.png")
        if debug_image is not None:
            cv2.imwrite(img_path, debug_image)
        json_path = os.path.join(output_folder, f"{base_name}_data.json")
        with open(json_path, 'w') as f:
            json.dump(state, f, indent=4)

# --- BATCH PROCESSOR FUNCTION ---
def batch_process_folder(source_folder, output_folder, json_config_path):
    print(f"\n--- Starting Batch Process (V3.1 Name Fix) ---")
    print(f"Source: {source_folder}")
    print(f"Output: {output_folder}")

    extractor = PokerogueExtractor(json_config_path)
    if extractor.reader is None:
        print("CRITICAL ERROR: EasyOCR failed to load. Aborting.")
        return

    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
    files = [f for f in os.listdir(source_folder) if f.lower().endswith(valid_extensions)]
    total_files = len(files)
    
    if total_files == 0:
        print("No image files found in source folder.")
        return

    print(f"Found {total_files} images. Processing...")

    for i, filename in enumerate(files):
        file_path = os.path.join(source_folder, filename)
        try:
            img = cv2.imread(file_path)
            if img is None:
                print(f"Skipping corrupt file: {filename}")
                continue

            state, dbg_img = extractor.extract_gamestate(img, 'single', debug=True)
            extractor.save_snapshot(state, dbg_img, output_folder, filename)
            
            percent = ((i + 1) / total_files) * 100
            sys.stdout.write(f"\rProgress: [{i+1}/{total_files}] - {percent:.1f}%")
            sys.stdout.flush()

        except Exception as e:
            print(f"\nError processing {filename}: {e}")
            continue

    print(f"\n\n--- Batch Processing Complete! ---")
    print(f"Check folder: {output_folder}")


if __name__ == "__main__":
    JSON_CONFIG = 'resultsLIVE.json'
    SOURCE_FOLDER = 'screenshots_raw' 
    OUTPUT_FOLDER = 'training_data_v2' 

    if os.path.exists(SOURCE_FOLDER):
        batch_process_folder(SOURCE_FOLDER, OUTPUT_FOLDER, JSON_CONFIG)
    else:
        print(f"Please create a folder named '{SOURCE_FOLDER}' and put your images in it.")
        print("Or change the SOURCE_FOLDER variable in the script.")