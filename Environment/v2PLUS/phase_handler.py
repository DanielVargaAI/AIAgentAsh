from pyautogui import press

import settings
from Environment.send_key_inputs import press_button
import DataExtraction.create_input as input_creator
import button_combinations
import random


def phase_handler(meta_data, driver, pokemon_embeddings_data, move_embeddings_data, phase_counter=0, terminated=False):
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
    if meta_data["phaseName"] == "TitlePhase":
        for button_name in button_combinations.NEW_SAVE:
            press_button(driver, button_name)
        terminated = True

    elif meta_data["phaseName"] == "CheckSwitchPhase":
        press_button(driver, "DOWN")
        press_button(driver, "SPACE")

    elif meta_data["phaseName"] == "LearnMovePhase":
        for _ in range(4):  # TODO: check amount of skips
            press_button(driver, "SPACE")
        forget_move = random.randint(0, 4)
        for move in range(forget_move):  # TODO: check starting position, might be the new move at the bottom
            press_button(driver, "DOWN")
        for _ in range(4):  # TODO: check amount of skips
            press_button(driver, "SPACE")

    elif meta_data["phaseName"] == "SelectModifierPhase":
        if phase_counter == 0:
            selected_item, weight = select_item(meta_data)
            for _ in range(selected_item):
                press_button(driver, "RIGHT")
            press_button(driver, "SPACE")
        else:
            # TODO: this might occur, if we can't select an item with "simple" selection
            pass

    elif meta_data["phaseName"] == "SwitchPhase":
        alive_pokemon = []
        for hp in meta_data["hp_values"]["players"].values():
            alive_pokemon.append(hp > 0.0)
        if sum(alive_pokemon[2:]) >= 1:
            new_pokemon_ind = random.randint(2, 6)
        else:
            new_pokemon_ind = 1
        # TODO: find out button presses for selecting the right pokemon

    elif meta_data["phaseName"] == "EggSummaryPhase":
        press_button(driver, "BACKSPACE")

    elif meta_data["phaseName"] == "CommandPhase":
        return terminated

    else:
        if phase_counter >= 2:
            # TODO: Call operator, cause we might be stuck in a loop/unskippable operation
            pass
        else:
            press_button(driver, "SPACE")

    # if the phase got resolved -> recursive call with new obs
    new_obs, new_meta_data = get_new_obs(driver, pokemon_embeddings_data, move_embeddings_data)
    if new_meta_data["phaseName"] == meta_data["phaseName"]:
        phase_counter += 1
    else:
        phase_counter = 0
    return phase_handler(new_meta_data, driver, pokemon_embeddings_data, move_embeddings_data, phase_counter, terminated)


def get_new_obs(driver, pokemon_embeddings_data, move_embeddings_data):
    obs = driver.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
    return input_creator.create_input_vector(obs, pokemon_embeddings_data, move_embeddings_data)


def select_item(meta_data):
    """
    Select the most suitable item from the shop (e.g. no applying on a Pokemon)
    :param meta_data: contains all items
    :return: the most suitable item we can take and it's weight
    """
    item_weights = []
    return item_weights.index(max(item_weights)), max(item_weights)
