import keyboard
from pyautogui import press
import logging

import settings
from Environment.send_key_inputs import press_button
import DataExtraction.create_input_0912_learningmove as input_creator
import button_combinations
import random
import time

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

# Create formatter and add it to the handler
formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
if not logger.handlers:
    logger.addHandler(ch)


def phase_handler(meta_data, obs, driver, pokemon_embeddings_data, move_embeddings_data, phase_counter=0, terminated=False, reward_meta=None, reward_obs=None, ongoing_save=True):
    """
    Handles the different phases that might occur during playthrough
    """
    # Initialize mutable defaults properly
    if reward_meta is None:
        reward_meta = {}
    if reward_obs is None:
        reward_obs = []
    
    # Safety check: ensure meta_data has phaseName
    if not meta_data or "phaseName" not in meta_data:
        logger.debug("phase_handler called with invalid meta_data, returning early")
        return terminated, reward_meta, reward_obs
    
    logger.debug(f"phase_handler called - Phase: {meta_data.get('phaseName', 'UNKNOWN')}, Counter: {phase_counter}, Terminated: {terminated}")

    print(meta_data["phaseName"])

    if meta_data["phaseName"] == "TitlePhase":
        logger.info("Detected TitlePhase - Starting new run")
        if ongoing_save:
            for button_name in button_combinations.ONGOING_SAVE:
                logger.debug(f"Pressing button: {button_name}")
                press_button(driver, button_name)
        else:
            for button_name in button_combinations.FIRST_SAVE:
                logger.debug(f"Pressing button: {button_name}")
                press_button(driver, button_name)
        terminated = True
        reward_meta = meta_data
        reward_obs = obs
        logger.info("TitlePhase completed - Run terminated")

    elif meta_data["phaseName"] == "CheckSwitchPhase":
        logger.info("Detected CheckSwitchPhase - No switch action")
        logger.debug("Pressing DOWN and SPACE")
        press_button(driver, "DOWN")
        press_button(driver, "SPACE")
        logger.debug("CheckSwitchPhase buttons pressed")

    # --- NEW HANDLER FOR SWITCHSUMMONPHASE ---
    elif meta_data["phaseName"] == "SwitchSummonPhase":
        logger.info("Detected SwitchSummonPhase - Declining Switch")
        # Press DOWN to select "No" (declining switch), then SPACE to confirm
        press_button(driver, "DOWN")
        press_button(driver, "SPACE")
        logger.debug("SwitchSummonPhase declined")
    # -----------------------------------------

    elif meta_data["phaseName"] == "LearnMovePhase":
        logger.info("Detected LearnMovePhase - Learning new move")
        
        learning_pokemon = meta_data.get("learning_pokemon")
        current_moves = meta_data.get("current_moves_count", 4)
        
        if learning_pokemon:
            logger.info(f"Pokemon {learning_pokemon.get('dex_nr')} is learning a move (currently knows {current_moves} moves)")
        
        if current_moves < 4:
            logger.debug("Pokemon knows < 4 moves, accepting new move without forgetting")
            press_button(driver, "SPACE")
        else:
            logger.debug("Pokemon knows 4 moves, randomly selecting move to forget")
            for _ in range(4):
                press_button(driver, "SPACE")
            
            forget_move = random.randint(0, 4)
            logger.debug(f"Selected move slot {forget_move} to replace")
            
            for move in range(forget_move):
                logger.debug(f"Pressing DOWN for move selection {move + 1}/{forget_move}")
                press_button(driver, "DOWN")
            
            logger.debug("Pressing SPACE to confirm move replacement")
            press_button(driver, "SPACE")
        
        logger.info("LearnMovePhase completed")

    elif meta_data["phaseName"] == "SelectModifierPhase":
        logger.info("Detected SelectModifierPhase - Selecting modifier/item")
        if phase_counter <= 10:
            selected_item, weight = select_item(meta_data)
            if weight == 0:
                press_button(driver, "DOWN")
                press_button(driver, "SPACE")
            else:
                logger.info(f"Selected item index: {selected_item} with weight: {weight}")
                logger.debug(f"Pressing RIGHT {selected_item} times to navigate to item")
                for i in range(selected_item):
                    logger.debug(f"RIGHT press {i + 1}/{selected_item}")
                    press_button(driver, "RIGHT")
                logger.debug("Pressing SPACE to confirm selection")
                press_button(driver, "SPACE")
                logger.info("SelectModifierPhase completed")
        else:
            while True:
                if keyboard.is_pressed("o"):
                    break
            logger.warning(f"SelectModifierPhase encountered {phase_counter} times - may be in loop")
            pass

    elif meta_data["phaseName"] == "SwitchPhase":
        logger.info("Detected SwitchPhase - Switching Pokemon")
        try:
            # Re-collect alive status from the now-complete hp_values list
            alive_pokemon = []
            for hp in meta_data["hp_values"]["players"].values():
                alive_pokemon.append(hp > 0.0)
            
            logger.debug(f"Alive Pokemon status: {alive_pokemon}")
            
            # Safe logic: check if we actually have reserves
            if len(alive_pokemon) > 2 and sum(alive_pokemon[2:]) >= 1:
                # Random reserve index (2 to length-1)
                new_pokemon_ind = random.randint(2, len(alive_pokemon) - 1)
                logger.info(f"Switching to Pokemon at index {new_pokemon_ind}")
            else:
                new_pokemon_ind = 1
                logger.info(f"Switching to Pokemon at index {new_pokemon_ind} (backup)")
            
            for _ in range(new_pokemon_ind):
                press_button(driver, "DOWN")
            press_button(driver, "SPACE")
            press_button(driver, "SPACE")
        except (KeyError, ValueError) as e:
            logger.error(f"Error in SwitchPhase: {e}")
            press_button(driver, "SPACE") # Fallback to avoid sticking

    elif meta_data["phaseName"] == "EggSummaryPhase":
        logger.info("Detected EggSummaryPhase - Closing egg summary")
        logger.debug("Pressing BACKSPACE to close")
        press_button(driver, "BACKSPACE")
        logger.info("EggSummaryPhase completed")

    elif meta_data["phaseName"] == "CommandPhase":
        logger.info("Detected CommandPhase - Player action required, returning control")
        return terminated, reward_meta, reward_obs

    else:
        logger.debug(f"Unhandled phase: {meta_data.get('phaseName', 'UNKNOWN')}")
        if 3 <= phase_counter <= 4:
            logger.error(f"Phase {meta_data.get('phaseName', 'UNKNOWN')} repeated {phase_counter} times - possible stuck state")
            time.sleep(1)
            #press_button(driver, "SPACE")

        elif phase_counter >= 8:
            logger.warning(f"Phase {meta_data.get('phaseName', 'UNKNOWN')} stuck for 5+ iterations, aborting")
            return terminated, reward_meta, reward_obs
        else:
            logger.debug("Attempting generic skip with SPACE")
            press_button(driver, "SPACE")

    # Recursive call for next state
    logger.debug("Fetching new observation after phase action")
    try:
        new_obs, new_meta_data = get_new_obs(driver, pokemon_embeddings_data, move_embeddings_data)
        new_phase = new_meta_data.get("phaseName", "UNKNOWN")
        old_phase = meta_data.get("phaseName", "UNKNOWN")
        if not terminated:
            reward_meta = new_meta_data
            reward_obs = new_obs
        
        if new_phase == old_phase:
            phase_counter += 1
            time.sleep(0.5)  # Small delay to avoid rapid looping
            logger.debug(f"Same phase detected, counter incremented to {phase_counter}")
        else:
            phase_counter = 0
            logger.info(f"Phase transition: {old_phase} -> {new_phase}")

        return phase_handler(new_meta_data, new_obs, driver, pokemon_embeddings_data, move_embeddings_data, phase_counter, terminated, reward_meta, reward_obs)
    except Exception as e:
        logger.error(f"Error fetching new observation: {e}")
        return terminated, reward_meta, reward_obs


def get_new_obs(driver, pokemon_embeddings_data, move_embeddings_data):
    """Fetch new observation from the game."""
    try:
        logger.debug("Executing script to fetch __GLOBAL_SCENE_DATA__")
        obs = driver.execute_script("return window.__GLOBAL_SCENE_DATA__();")
        if not obs:
            logger.warning("__GLOBAL_SCENE_DATA__ not found or not a function")
        result = input_creator.create_input_vector(obs, pokemon_embeddings_data, move_embeddings_data)
        logger.debug("Successfully created input vector from observation")
        return result
    except Exception as e:
        logger.error(f"Error in get_new_obs: {e}")
        raise


def select_item(meta_data):
    """
    Select the most suitable item from the shop
    """
    logger.debug("select_item called with meta_data")
    try:
        item_weights = []
        for item in meta_data["shop_items"]:
            if item["id"] in settings.item_weights["id"].keys():
                item_weights.append(settings.item_weights["id"][item["id"]])
            elif item["id"].find("BALL") >= 0:
                item_weights.append(5)
            else:
                item_weights.append(0)
                print(f"Unknown Item ID: {item['id']}")
        if not item_weights:
            logger.warning("No item weights calculated - using default selection")
            logger.debug("Returning default item (index 0, weight 0)")
            return 0, 0
        max_idx = item_weights.index(max(item_weights))
        max_weight = max(item_weights)
        logger.info(f"Selected item index: {max_idx} with weight: {max_weight}")
        return max_idx, max_weight
    except Exception as e:
        logger.error(f"Error in select_item: {e}")
        logger.debug("Returning default item due to error")
        return 0, 0