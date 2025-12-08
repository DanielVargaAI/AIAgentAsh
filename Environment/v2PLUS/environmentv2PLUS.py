"""
Custom environment for PokeRogue.
"""
import gymnasium as gym  # <--- WE MUST USE GYMNASIUM
from gymnasium import spaces # <--- NOT GYM
import numpy as np
import json
import time
import keyboard
import sys
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

import sys
import os

# Add the AIAgentAsh root directory to the system path (go up 2 levels: v2PLUS -> Environment -> AIAgentAsh)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import modules from AIAgentAsh package
try:
    from DataExtraction.automated_session_startup import setup_driver
    import settings
    import button_combinations
    import DataExtraction.create_input as input_creator
    from Environment.send_key_inputs import press_button
    from . import phase_handler
except ModuleNotFoundError as e:
    # Fallback: try importing with relative path adjustment
    print(f"Warning: Import error detected: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(__file__)}")
    print(f"Added to sys.path: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))}")
    raise

class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # --- 1. Define Action Space (Multi-Head) ---
        # [P1 Move (0-3), P1 Target (0-1), P2 Move (0-3), P2 Target (0-1)]
        self.action_space = spaces.MultiDiscrete([4, 2, 4, 2])
        # --- 2. Define Observation Space ---
        # Size 82 floats as calculated
        self.observation_space = spaces.Box(low=-100, high=100, shape=(82,), dtype=np.float32)
        self.last_obs = []
        self.new_obs = []
        self.last_meta_data = dict()
        self.new_meta_data = dict()
        self.terminated = False
        self.truncated = False
        self.driver = setup_driver()
        self.reward = 0.0 # Store reward for debugging display
        self.whose_turn = 0  # index of pokemon who has to select a move

        with open("Embeddings/Pokemon/pokemon_embeddings.json", "r") as f:
            self.pokemon_embeddings_data = json.loads(f.read())
            print(f"Loaded {len(self.pokemon_embeddings_data)} Pokemon embeddings.")
        with open("Embeddings/moves/move_embeddings.json", "r") as f:
            self.move_embeddings_data = json.loads(f.read())
            print(f"Loaded {len(self.move_embeddings_data)} Move embeddings.")


        # --- 4. Launch & Inject (Startup) ---
        # self._setup_driver()

        self.reset()

    def reset(self, seed=None, options=None):
        self._get_obs()
        self.last_obs = self.new_obs
        self.reward = 0.0
        self.terminated = False
        self.truncated = False
        return self.new_obs, {}

    def step(self, action):
        self._apply_action(action)
        self._get_obs()
        self.reward = self._get_reward()
        self.terminated = phase_handler.phase_handler(self.new_meta_data, self.driver, self.pokemon_embeddings_data,
                                                 self.move_embeddings_data)
        self._get_obs()
        self.last_obs = self.new_obs
        self.last_meta_data = self.new_meta_data
        
        return self.new_obs, self.reward, self.terminated, self.truncated, self._get_info()

    def _get_reward(self) -> float:
        reward = 0.0
        # hp delta
        for pkm_id, hp_value in self.new_meta_data["hp_values"]["enemies"].items():
            if pkm_id in self.last_meta_data["hp_values"]["enemies"].keys():
                reward += ((self.last_meta_data["hp_values"]["enemies"][pkm_id] -
                            self.new_meta_data["hp_values"]["enemies"][pkm_id])
                           * settings.reward_weights["hp"] * settings.reward_weights["damage_dealt"])
        if self.new_meta_data["stage"] % 10 != 0 or self.new_meta_data["stage"] == self.last_meta_data["stage"]:
            for pkm_id, hp_value in self.new_meta_data["hp_values"]["players"].items():
                if pkm_id in self.last_meta_data["hp_values"]["player"].keys():
                    dmg_delta = (self.last_meta_data["hp_values"]["player"][pkm_id] -
                                 self.new_meta_data["hp_values"]["players"][pkm_id])
                    reward -= (dmg_delta * settings.reward_weights["hp"] * settings.reward_weights["damage_taken"])
                    if self.new_meta_data["hp_values"]["players"][pkm_id] <= 0.0 <= dmg_delta:
                        reward += settings.reward_weights["member_died"]

        # wave progress
        if self.new_meta_data["stage"] != self.last_meta_data["stage"]:
            if self.new_meta_data["stage"] % 10 != 0:
                reward += settings.reward_weights["wave_done"]
            else:
                reward += settings.reward_weights["tenth_wave_done"]
        return reward
        
    def _apply_action(self, action):
        """
        Takes the NN action [0, 1, 2, 0] and prints instructions.
        Does NOT overwrite the action.
        """
        # Unpack the action from the Neural Network
        p1_move, p1_target, p2_move, p2_target = action
        
        # Decode targets for readability
        t1_str = "Right Enemy" if p1_target == 1 else "Left Enemy"
        t2_str = "Right Enemy" if p2_target == 1 else "Left Enemy"
        
        print("\n" + "="*40)
        print(f"📊 DEBUG STATE:")
        print(f"   Reward from LAST turn: {self.reward:.4f}")
        print("-" * 40)

        print("\n" + "="*40)
        print(f"   Pokemon 1: Use MOVE {p1_move + 1} on {t1_str}")
        print(f"   Pokemon 2: Use MOVE {p2_move + 1} on {t2_str}")
        print("="*40)
        print(">>> Executing moves in browser.")

        # Pokemon 1
        for button in ["LEFT", "UP", "SPACE"]:
            press_button(self.driver, button)
        for button in button_combinations.SELECT_MOVE[p1_move]:
            press_button(self.driver, button)
        for button in button_combinations.SELECT_TARGET[p1_target]:
            press_button(self.driver, button)

        # Pokemon 2, if we are in a double fight and the second Pokemon is alive
        if self.new_meta_data["is_double_fight"] and list(self.new_meta_data["hp_values"].values())[0] > 0.0:
            for button in ["LEFT", "UP", "SPACE"]:
                press_button(self.driver, button)
            for button in button_combinations.SELECT_MOVE[p2_move]:
                press_button(self.driver, button)
            for button in button_combinations.SELECT_TARGET[p2_target]:
                press_button(self.driver, button)

    def _check_truncated(self) -> bool:
        pass

    def _check_terminated(self) -> bool:
        pass

    def _get_info(self):
        info = dict()
        info["reward"] = self.reward
        info["stage"] = self.new_meta_data["stage"]

    def _get_obs(self):
        try:
            # Safely try to execute the script
            raw_data = self.driver.execute_script("return window.__GLOBAL_SCENE_DATA__();")

            # If the script returned null or valid data wasn't found
            if not isinstance(raw_data, dict) or 'enemy' not in raw_data:
                return np.zeros(82, dtype=np.float32)
            self.new_obs, self.new_meta_data = input_creator.create_input_vector(raw_data,
                                                                                 self.pokemon_embeddings_data,
                                                                                 self.move_embeddings_data)

            self.new_obs = np.array(self.new_obs, dtype=np.float32)

        except WebDriverException as e:
            # Catch "scene.currentBattle is null" errors silently
            self.new_obs = np.zeros(82, dtype=np.float32)

        except Exception as e:
            # Catch other Python errors
            print(f" Warning in _get_obs: {e}")
            self.new_obs = np.zeros(82, dtype=np.float32)

        return self.new_obs