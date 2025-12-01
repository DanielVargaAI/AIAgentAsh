import gymnasium as gym
from gymnasium import spaces
import numpy as np
import keyboard
import time
import json
import os


# === CONFIGURATION ===
KEY_PRESS_DELAY = 0.1   # Time between key presses
TURN_WAIT_TIME = 2.5    # Time to wait for animations after submitting actions
DAMAGE_WEIGHT = 1.5     # Weight multiplier: Taking damage is 1.5x worse than dealing it

class PokeRogueV2Env(gym.Env):
    def __init__(self):
        super(PokeRogueV2Env, self).__init__()

        # === ACTION SPACE ===
        # [P1_Move (0-3), P1_Target (0-1), P2_Move (0-3), P2_Target (0-1)]
        # The Neural Network automatically creates "4 Heads" for these outputs.
        self.action_space = spaces.MultiDiscrete([4, 2, 4, 2])

        # === DATABASE LOADING ===
        # Load these once to avoid file I/O lag every step
        self.move_db = self._load_json("move_data.json")
        self.poke_db = self._load_json("pokedex_database.json")
        self.type_db = self._load_json("type_embeddings.json")

        # === OBSERVATION SPACE ===
        # Determine vector size dynamically using dummy data
        dummy_data = self._get_dummy_data()
        dummy_vec = self._process_data_to_vector(dummy_data)
        self.obs_dim = dummy_vec.shape[1]
        
        # Infinite range because embeddings/HP can vary
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.obs_dim,), dtype=np.float32)

        # Internal State
        self.current_state = dummy_data

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # 1. Get Fresh Game Data
        self.current_state = self._get_game_state()
        
        # 2. Process to Vector
        obs = self._process_data_to_vector(self.current_state)
        return obs.flatten(), {}

    def step(self, action):
        # Action is: [p1_move, p1_target, p2_move, p2_target]
        
        # 1. Execute Actions (Hardcoded Keys)
        self._perform_action(action)
        
        # 2. Wait for Game Logic/Animations
        time.sleep(TURN_WAIT_TIME)

        # 3. Get New State
        new_state_data = self._get_game_state()
        
        # 4. Calculate Reward (Health Delta)
        reward = self._calculate_reward(self.current_state, new_state_data)
        
        # 5. Check Termination (Win/Loss)
        terminated = self._check_terminated(new_state_data)
        truncated = False # Can be used for turn limits
        
        # 6. Update State
        self.current_state = new_state_data
        obs = self._process_data_to_vector(self.current_state)
        
        return obs.flatten(), reward, terminated, truncated, {}

    # === ACTION LOGIC ===
    def _perform_action(self, action):
        p1_move, p1_target, p2_move, p2_target = action

        # POKEMON 1
        self._navigate_to_fight()
        self._input_move(p1_move)
        if self._is_double_battle(self.current_state):
             self._input_target(p1_target)

        # POKEMON 2 (Only if Double Battle)
        if self._is_double_battle(self.current_state):
            time.sleep(0.5) # Small delay for UI transition
            self._navigate_to_fight()
            self._input_move(p2_move)
            self._input_target(p2_target)

    def _navigate_to_fight(self):
        # Reset cursor to Top-Left (Fight) assuming standard menu layout
        # We press Up+Left multiple times to ensure we are at index 0,0
        self._press('w')
        self._press('a')
        self._press('space') # Enter 'FIGHT' menu

    def _input_move(self, move_idx):
        # 0: Up-Left, 1: Up-Right, 2: Down-Left, 3: Down-Right
        if move_idx == 0:
            self._press('w'); self._press('a')
        elif move_idx == 1:
            self._press('w'); self._press('d')
        elif move_idx == 2:
            self._press('s'); self._press('a')
        elif move_idx == 3:
            self._press('s'); self._press('d')
        self._press('space') # Confirm Move

    def _input_target(self, target_idx):
        # 0: Left, 1: Right
        if target_idx == 0:
            self._press('a')
        else:
            self._press('d')
        self._press('space') # Confirm Target

    def _press(self, key):
        keyboard.send(key)
        time.sleep(KEY_PRESS_DELAY)

    # === REWARD & STATE LOGIC ===
    def _calculate_reward(self, old_data, new_data):
        # Sum of all Ally/Enemy HP
        old_ally = old_data.get('ally1_health', 0) + old_data.get('ally2_health', 0)
        new_ally = new_data.get('ally1_health', 0) + new_data.get('ally2_health', 0)
        
        old_enemy = old_data.get('enemy1_health', 0) + old_data.get('enemy2_health', 0)
        new_enemy = new_data.get('enemy1_health', 0) + new_data.get('enemy2_health', 0)

        dmg_dealt = old_enemy - new_enemy
        dmg_received = old_ally - new_ally

        # Reward = Damage Dealt - (1.5 * Damage Received)
        return float(dmg_dealt - (dmg_received * DAMAGE_WEIGHT))

    def _get_game_state(self):
        # [PLACEHOLDER] Link your colleague's extraction code here!
        return self._get_dummy_data()

    def _process_data_to_vector(self, data):
        # Uses your input_vector.py
        vec = input_vector.create_input_vector(data, self.move_db, self.poke_db, self.type_db)
        return vec

    def _check_terminated(self, data):
        # Terminate if Ally Team Dead OR Enemy Team Dead
        allies_alive = (data.get('ally1_health', 0) + data.get('ally2_health', 0)) > 0
        enemies_alive = (data.get('enemy1_health', 0) + data.get('enemy2_health', 0)) > 0
        return not allies_alive or not enemies_alive

    def _is_double_battle(self, data):
        return data.get('enemy2_level', 0) > 0 or data.get('ally2_level', 0) > 0

    def _load_json(self, filename):
        if not os.path.exists(filename):
            print(f"[WARNING] {filename} not found. Using empty dict.")
            return {}
        with open(filename, "r") as f:
            return json.load(f)

    def _get_dummy_data(self):
        # Returns a structure matching input_vector.py requirements
        return {
            "enemy1_health": 100.0, "enemy1_type1": "Normal", "enemy1_type2": "None", "enemy1_level": 5, "enemy1_status": "None", "enemy1_name": "Rattata",
            "enemy2_health": 0.0, "enemy2_type1": "None", "enemy2_type2": "None", "enemy2_level": 0, "enemy2_status": "None", "enemy2_name": "None",
            "ally1_health": 100.0, "ally1_type1": "Fire", "ally1_type2": "None", "ally1_level": 5, "ally1_status": "None", "ally1_name": "Charmander",
            "ally1_attack1_name": "Scratch", "ally1_attack1_pp": 35.0,
            "ally1_attack2_name": "Growl", "ally1_attack2_pp": 40.0,
            "ally1_attack3_name": "Ember", "ally1_attack3_pp": 25.0,
            "ally1_attack4_name": "None", "ally1_attack4_pp": 0.0,
            "ally2_health": 0.0, "ally2_type1": "None", "ally2_type2": "None", "ally2_level": 0, "ally2_status": "None", "ally2_name": "None",
            "ally2_attack1_name": "None", "ally2_attack1_pp": 0.0,
            "ally2_attack2_name": "None", "ally2_attack2_pp": 0.0,
            "ally2_attack3_name": "None", "ally2_attack3_pp": 0.0,
            "ally2_attack4_name": "None", "ally2_attack4_pp": 0.0,
        }