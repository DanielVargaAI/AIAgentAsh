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

# Add the parent directory (AIAgentAsh) to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import DataExtraction.create_input as input_creator

class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()


        #self.action_space = spaces.Discrete(12)  # TODO Example: 4 attacks * 2 fighters + 2 fighter * 2 targets
        # --- 1. Define Action Space (Multi-Head) ---
        # [P1 Move (0-3), P1 Target (0-1), P2 Move (0-3), P2 Target (0-1)]
        self.action_space = spaces.MultiDiscrete([4, 2, 4, 2])
        # --- 2. Define Observation Space ---
        # Size 82 floats as calculated
        self.observation_space = spaces.Box(low=-100, high=100, shape=(82,), dtype=np.float32)
        self.last_obs = []
        self.new_obs = []
        self.terminated = False
        self.truncated = False
        self.driver = None
        self.PenaltyFactor = 1.5 # Penalty for damage taken
        self.last_reward = 0.0 # Store reward for debugging display

        with open("Embeddings/Pokemon/pokemon_embeddings.json", "r") as f:
            self.pokemon_embeddings_data = json.loads(f.read())
        with open("Embeddings/moves/move_embeddings.json", "r") as f:
            self.move_embeddings_data = json.loads(f.read())


        # --- 4. Launch & Inject (Startup) ---
        self._setup_driver()

        

    def _setup_driver(self):
        """Launches browser and injects save/settings."""
        print("--- Launching PokeRogue Environment ---")
        options = Options()
        # options.add_argument("--headless") # Uncomment if you don't want UI
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("http://localhost:8000")

        # Inject Settings
        settings = {"PLAYER_GENDER": 0, "GAME_SPEED": 5, "MASTER_VOLUME": 0, "TUTORIALS": 0, "ENABLE_RETRIES": 1, "SHOW_LEVEL_UP_STATS": 0, "EXP_GAINS_SPEED": 5, "HP_BAR_SPEED": 5, "gameVersion": "1.11.3"}
        self.driver.execute_script(f"localStorage.setItem('settings', '{json.dumps(settings)}');")
        self.driver.refresh()
        time.sleep(1)

        # Inject Save Data
        try:
            with open("DataExtraction/copied_save_data.txt", "r") as f:
                file_content = f.read()
            self.driver.execute_script(f"localStorage.setItem('data_Guest', '{file_content}');")
            print("Save data injected.")
        except FileNotFoundError:
            print("Warning: copied_save_data.txt not found. Starting clean.")

        self.driver.refresh()
        
        # Wait for Game Load
        print("Waiting for game to load...")
        time.sleep(5) # Allow assets to load
        WebDriverWait(self.driver, timeout=20).until(
            lambda d: d.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
        )
        print("Game Loaded & Ready.")

        input("Press Enter to continue when in Battle...")

        self.reset()

    def reset(self, seed=None, options=None):
        self._get_obs()
        self.last_obs = self.new_obs
        self.terminated = False
        self.truncated = False
        return self.new_obs, {}

    #def step(self, action):
    #    self._apply_action(action)
    #    while True:
    #        if keyboard.is_pressed("p"):
    #            self.truncated = True
    #            break
    #        elif keyboard.is_pressed("q"):
    #            self.terminated = True
    #            break
    #        elif keyboard.is_pressed("o"):
    #            break
    #    self._get_obs()
    #    reward = self._get_reward()
    #    self.last_obs = self.new_obs
    #    return self._get_obs(), reward, self.terminated, self.truncated, {}
    

    def step(self, action):
        # 1. TELL USER WHAT TO DO
        self._apply_action(action)
        
        # 2. PAUSE LOOP (Wait for 'O')
        # We use a loop that sleeps to prevent CPU spam and waits for key release
        while True:
            if keyboard.is_pressed("o"):
                # Wait until the user LETS GO of the key (Debounce)
                while keyboard.is_pressed("o"): 
                    time.sleep(0.1)
                break
            elif keyboard.is_pressed("q"):
                self.terminated = True
                break
            # Sleep slightly to prevent freezing the PC
            time.sleep(0.1)

        # 3. GET OBS & REWARD
        self._get_obs()
        self._check_terminated()
        reward = self._get_reward()
        self.last_obs = self.new_obs
        
        return self.new_obs, reward, self.terminated, self.truncated, {}

    def _get_reward(self) -> float:
        """
        Calculates reward based on HP delta.
        Enemies: 8, 17
        Players: 26, 58
        """
        # Extract HPs
        old_enemy_hp = self.last_obs[8] + self.last_obs[17]
        print(f"Old Enemy HP: {old_enemy_hp}")
        new_enemy_hp = self.new_obs[8] + self.new_obs[17]
        print(f"New Enemy HP: {new_enemy_hp}")
        
        old_player_hp = self.last_obs[26] + self.last_obs[58]
        print(f"Old Player HP: {old_player_hp}")
        new_player_hp = self.new_obs[26] + self.new_obs[58]
        print(f"New Player HP: {new_player_hp}")

        # Reward: Damage Dealt - Damage Taken
        damage_dealt = old_enemy_hp - new_enemy_hp
        damage_taken = old_player_hp - new_player_hp

        # Simple Reward
        reward = damage_dealt - damage_taken * self.PenaltyFactor
        print(f"Reward Calculation: Damage Dealt = {damage_dealt}, Damage Taken = {damage_taken}, Reward = {reward}")
        return reward

    #def _apply_action(self, action):
    #    action = [1] * 12
    #    print(f"Pokemon 1: use action {action[0:4].index(1)} on target {action[8:10].index(1)} - Pokemon 2: use action {action[4:8].index(1)} "
    #          f"on target {action[10:12].index(1)}")
        
        
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

        # --- DEBUG INFO ---
        # Get raw HP for display (Player 26+58, Enemy 8+17)
        p_hp = (self.last_obs[26] + self.last_obs[58]) * 100
        e_hp = (self.last_obs[8] + self.last_obs[17]) * 100
        
        print("\n" + "="*40)
        print(f"📊 DEBUG STATE:")
        print(f"   Reward from LAST turn: {self.last_reward:.4f}")
        print(f"   Est. HP: Player {p_hp:.1f}% | Enemy {e_hp:.1f}%")
        print("-" * 40)

        print("\n" + "="*40)
        print(f"   Pokemon 1: Use MOVE {p1_move + 1} on {t1_str}")
        print(f"   Pokemon 2: Use MOVE {p2_move + 1} on {t2_str}")
        print("="*40)
        print(">>> 1. Execute moves in browser.")
        print(">>> 2. Wait for animations.")
        print(">>> 3. Press 'O' to continue.")

    def _check_truncated(self) -> bool:
        pass

    def _check_terminated(self) -> bool:
        pass

    def _get_obs(self):
            try:
                # Safely try to execute the script
                raw_data = self.driver.execute_script("return window.__GLOBAL_SCENE_DATA__();")
                
                # If the script returned null or valid data wasn't found
                if not isinstance(raw_data, dict) or 'enemy' not in raw_data:
                    return np.zeros(82, dtype=np.float32)

                self.new_obs = input_creator.create_input_vector(raw_data, self.pokemon_embeddings_data, self.move_embeddings_data)
                self.new_obs = np.array(self.new_obs, dtype=np.float32)
                
            except WebDriverException as e:
                # Catch "scene.currentBattle is null" errors silently
                self.new_obs = np.zeros(82, dtype=np.float32)
                
            except Exception as e:
                # Catch other Python errors
                print(f" Warning in _get_obs: {e}")
                self.new_obs = np.zeros(82, dtype=np.float32)
                
            return self.new_obs