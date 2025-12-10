import keyboard
from pyautogui import press
import logging

import settings
from Environment.send_key_inputs import press_button
import DataExtraction.create_input as input_creator
import button_combinations
import random
import time
import json

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


def phase_handler(meta_data, obs, driver, pokemon_embeddings_data, move_embeddings_data, phase_counter=0, terminated=False, reward_meta=dict(), reward_obs=list(), ongoing_save=True):
    """
    Handles the different phases that might occur during playthrough
    :param phase_counter: how often we have been in this phase in a row
    :param terminated: if we encountered a TitlePhase while handling
    :param meta_data: current meta_data
    :param driver: the selenium driver
    :param pokemon_embeddings_data: pre-loaded pokemon data
    :param move_embeddings_data: pre-loaded move data
    :return: bool => are we terminated or is the run still ongoing
    """
    logger.debug(f"phase_handler called - Phase: {meta_data.get('phaseName', 'UNKNOWN')}, Counter: {phase_counter}, Terminated: {terminated}")

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
        if meta_data["is_double_fight"]:
            press_button(driver, "DOWN")
            press_button(driver, "SPACE")
        logger.debug("CheckSwitchPhase buttons pressed")

    elif meta_data["phaseName"] == "LearnMovePhase":  # Implement special case if pokemon doesnt know 4 moves, we dont need to forget one
        logger.info("Detected LearnMovePhase - Randomly selecting move to learn/forget")
        logger.debug("Pressing SPACE 4 times to cycle through moves")
        if meta_data["learn_move_phase"]["member_move_count"] <= 3:
            for _ in range(4):
                press_button(driver, "SPACE")
            forget_move = random.randint(0, 4)
            logger.debug(f"Randomly selected move index: {forget_move}")
            for move in range(forget_move):
                logger.debug(f"Pressing DOWN for move selection {move + 1}/{forget_move}")
                press_button(driver, "UP")
            logger.debug("Pressing SPACE 4 times to confirm move")
            if forget_move == 0:
                press_range = 3
            else:
                press_range = 5
            for _ in range(press_range):
                press_button(driver, "SPACE")
        else:
            press_button(driver, "SPACE")
        logger.info("LearnMovePhase completed")

    elif meta_data["phaseName"] == "SelectModifierPhase":
        logger.info("Detected SelectModifierPhase - Selecting modifier/item")
        if phase_counter <= 10:
            selected_item, weight = select_item(meta_data)
            if weight <= 4:
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
            # TODO: this might occur, if we can't select an item with "simple" selection
            pass

    elif meta_data["phaseName"] == "SwitchPhase":
        logger.info("Detected SwitchPhase - Switching Pokemon")
        try:
            new_pkm_index = 1
            if len(meta_data["hp_values"]["players"].keys()) > 2:
                if sum(meta_data["hp_values"]["players"].values()[2:]) > 0.0:
                    pkm_id = random.choices(list(meta_data["hp_values"]["players"].keys())[2:],
                                            weights=list(meta_data["hp_values"]["players"].values())[2:], k=1)
                    new_pkm_index = list(meta_data["hp_values"]["players"].keys()).index(pkm_id[0])
            logger.debug(f"Switching to Pokemon on index {new_pkm_index}")
            for _ in range(new_pkm_index):
                press_button(driver, "DOWN")
            press_button(driver, "SPACE")
            press_button(driver, "SPACE")
        except (KeyError, ValueError) as e:
            logger.error(f"Error in SwitchPhase: {e}")

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
        if 2 <= phase_counter <= 4:
            logger.error(f"Phase {meta_data.get('phaseName', 'UNKNOWN')} repeated {phase_counter} times - possible stuck state")
            time.sleep(1)

        elif phase_counter >= 5:
            while True:  # Observer has to fix the state
                if keyboard.is_pressed("p"):
                    break
        else:
            logger.debug("Attempting generic skip with SPACE")
            press_button(driver, "SPACE")

    # if the phase got resolved -> recursive call with new obs
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
    Select the most suitable item from the shop (e.g. no applying on a Pokemon)
    :param meta_data: contains all items
    :return: the most suitable item we can take and it's weight
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
                with open("unknown_item_names.json", "w") as f:
                    unknown_items = json.load(f)
                    if item["id"] not in unknown_items.keys():
                        unknown_items[item["id"]] = item["tier"]
                        f.write(json.dumps(unknown_items))
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
