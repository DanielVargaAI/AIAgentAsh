import gymnasium as gym
from gymnasium import spaces
import numpy as np
import keyboard
import time
import input_vector  # This is your existing script

# CONFIG
KEY_PRESS_DURATION = 0.05
STEP_DELAY = 0.2
TURN_WAIT_TIME = 2.0  # Time to wait after all actions are submitted
DAMAGE_RECEIVED_WEIGHT = 1.5 

class PokeRogueV2Env(gym.Env):
    def __init__(self):
        super(PokeRogueV2Env, self).__init__()

        # === ACTION SPACE ===
        # Format: [P1_Move (0-3), P1_Target (0-1), P2_Move (0-3), P2_Target (0-1)]
        self.action_space = spaces.MultiDiscrete([4, 2, 4, 2])

        # === OBSERVATION SPACE ===
        dummy_data = self._get_dummy_data()
        dummy_vec = self._process_data_to_vector(dummy_data)
        self.obs_dim = dummy_vec.shape[1]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.obs_dim,), dtype=np.float32)

        # Internal State
        self.current_state = dummy_data
        self.last_state = dummy_data

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_state = self._get_game_state()
        obs = self._process_data_to_vector(self.current_state)
        return obs.flatten(), {}

    def step(self, action):
        # 1. Execute Actions
        self._perform_action(action)
        
        # 2. Wait for turn resolution
        time.sleep(TURN_WAIT_TIME) 

        # 3. Get New State & Calc Reward
        new_state_data = self._get_game_state()
        reward = self._calculate_reward(self.current_state, new_state_data)
        terminated = self._check_terminated(new_state_data)
        truncated = False
        
        self.current_state = new_state_data
        obs = self._process_data_to_vector(self.current_state)
        
        return obs.flatten(), reward, terminated, truncated, {}

    def _perform_action(self, action):
        """
        Executes the sequence for 1 or 2 Pokemon based on hardcoded keys.
        """
        p1_move, p1_target, p2_move, p2_target = action
        
        # --- POKEMON 1 TURN ---
        self._enter_fight_menu()     # Select "Fight"
        self._select_move(p1_move)   # Select Move
        
        if self._is_double_battle(self.current_state):
            # If double battle, we might need to select a target
            # Note: Game logic determines if a move NEEDS a target (e.g. single target attacks).
            # For robustness, we can try inputting it. If the move is AOE, keys might be ignored.
            self._select_target(p1_target)
            
            # --- POKEMON 2 TURN ---
            # Wait for P1 animation/menu transition
            time.sleep(0.5) 
            
            self._enter_fight_menu()     # Select "Fight" for P2
            self._select_move(p2_move)   # Select Move for P2
            self._select_target(p2_target) # Select Target for P2

    def _press(self, key):
        """Helper to press a key reliably"""
        keyboard.send(key)
        time.sleep(STEP_DELAY)

    def _enter_fight_menu(self):
        """
        Navigates to Top-Left (Fight) and enters.
        Assumes cursor could be anywhere, so we brute-force Top-Left.
        """
        self._press('w') # Up
        self._press('a') # Left
        self._press('space') # Confirm

    def _select_move(self, move_idx):
        """
        0: Up Left (Attack 1)
        1: Up Right (Attack 2)
        2: Down Left (Attack 3)
        3: Down Right (Attack 4)
        """
        if move_idx == 0:   # Attack 1
            self._press('w')
            self._press('a')
        elif move_idx == 1: # Attack 2
            self._press('w')
            self._press('d')
        elif move_idx == 2: # Attack 3
            self._press('s')
            self._press('a')
        elif move_idx == 3: # Attack 4
            self._press('s')
            self._press('d')
        
        self._press('space') # Apply

    def _select_target(self, target_idx):
        """
        0: Left (Target 1)
        1: Right (Target 2)
        """
        if target_idx == 0:
            self._press('a')
        else:
            self._press('d')
        
        self._press('space') # Apply

    # ... [Rest of the helper methods: _calculate_reward, _get_game_state, etc. remain the same] ...
    
    def _calculate_reward(self, old_data, new_data):
        enemy_hp_old = old_data.get('enemy1_health', 0) + old_data.get('enemy2_health', 0)
        enemy_hp_new = new_data.get('enemy1_health', 0) + new_data.get('enemy2_health', 0)
        dmg_dealt = enemy_hp_old - enemy_hp_new

        ally_hp_old = old_data.get('ally1_health', 0) + old_data.get('ally2_health', 0)
        ally_hp_new = new_data.get('ally1_health', 0) + new_data.get('ally2_health', 0)
        dmg_received = ally_hp_old - ally_hp_new

        return float(dmg_dealt - (dmg_received * DAMAGE_RECEIVED_WEIGHT))

    def _get_game_state(self):
        # TODO: Connect to your colleague's data extraction tool
        return self._get_dummy_data()

    def _process_data_to_vector(self, data):
        # Lazy loading to avoid global scope issues
        import json
        # Ensure these files exist in your directory
        try:
            with open("move_data.json", "r") as f: move_db = json.load(f)
            with open("pokedex_database.json", "r") as f: poke_db = json.load(f)
            with open("type_embeddings.json", "r") as f: type_db = json.load(f)
            return input_vector.create_input_vector(data, move_db, poke_db, type_db)
        except FileNotFoundError:
            # Fallback for testing without files
            return np.zeros((1, 512)) # Adjust dimension as needed

    def _is_double_battle(self, data):
        return data.get('enemy2_level', 0) > 0 or data.get('ally2_level', 0) > 0

    def _check_terminated(self, data):
        ally_hp = data.get('ally1_health', 0) + data.get('ally2_health', 0)
        enemy_hp = data.get('enemy1_health', 0) + data.get('enemy2_health', 0)
        return ally_hp <= 0 or enemy_hp <= 0

    def _get_dummy_data(self):
        # Same dummy data as before
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