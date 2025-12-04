"""
custom environment for PokeRogue.
"""
import gym
import keyboard
from gym import spaces
import numpy as np
import DataExtraction.v3.v3_create_input as input_creator
import json
import DataExtraction.automated_session_startup as session_startup
import settings


class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.MultiDiscrete([4, 2, 4, 2])
        self.observation_space = spaces.Box(low=-100, high=100, shape=(82,), dtype=np.float32)  # TODO change dimension
        self.last_obs = []
        self.new_obs = []
        self.last_meta_data = dict()
        self.new_meta_data = dict()
        self.terminated = False
        self.truncated = False
        self.driver = session_startup.setup_driver()
        with open("../Embeddings/Pokemon/pokemon_embeddings.json", "r") as f:
            self.pokemon_embeddings_data = json.loads(f.read())
        with open(r"../Embeddings/moves/move_embeddings.json", "r") as f:
            self.move_embeddings_data = json.loads(f.read())
        self.reset()

    def reset(self, seed=None, options=None):
        self._get_obs()
        self.last_obs = self.new_obs
        self.terminated = False
        self.truncated = False
        return self.new_obs, {}

    def step(self, action):
        self._apply_action(action)
        while True:
            if keyboard.is_pressed("p"):
                self.truncated = True
                break
            elif keyboard.is_pressed("q"):
                self.terminated = True
                break
            elif keyboard.is_pressed("o"):
                break
        self._get_obs()
        reward = self._get_reward()
        self.last_obs = self.new_obs
        return self._get_obs(), reward, self.terminated, self.truncated, {}

    def _handle_phase(self):
        """
        if self.new_meta_data["phase"] in settings.phases["nothing_to_do"]:
            get new obs
        elif ... in phases["skip_information"]:
            press button space
            get new obs
        else:
            return with phase
        check if last obs was same phase, in case we update faster than the environment
        need to define the button sequence for every action in every phase where we have to do stuff
        """
        pass

    def _get_reward(self) -> float:
        reward = 0.0
        # {"phase": dict["phase"]["phaseName"], "stage": dict["metaData"]["waveIndex"],
        #                  "hp_values": {"enemies": {}, "players": {}}}
        for pkm_id, hp_value in self.new_meta_data["hp_values"]["enemies"].items():
            if pkm_id in self.last_meta_data["hp_values"]["enemies"].keys():
                reward += ((self.last_meta_data["hp_values"]["enemies"][pkm_id] -
                            self.new_meta_data["hp_values"]["enemies"][pkm_id])
                           * settings.reward_weights["hp"] * settings.reward_weights["damage_dealt"])
        if self.new_meta_data["stage"] % 10 != 0 or self.new_meta_data["stage"] == self.last_meta_data["stage"]:  # TODO has to be same or different?
            for pkm_id, hp_value in self.new_meta_data["hp_values"]["players"].items():
                if pkm_id in self.last_meta_data["hp_values"]["player"].keys():
                    reward -= ((self.last_meta_data["hp_values"]["player"][pkm_id] -
                                self.new_meta_data["hp_values"]["players"][pkm_id])
                               * settings.reward_weights["hp"] * settings.reward_weights["damage_taken"])
        return reward

    def _apply_action(self, action):
        action = [1] * 12
        print(f"Pokemon 1: use action {action[0:4].index(1)} on target {action[8:10].index(1)} - Pokemon 2: use action {action[4:8].index(1)} "
              f"on target {action[10:12].index(1)}")

    def _check_truncated(self) -> bool:
        pass

    def _check_terminated(self) -> bool:
        pass

    def _get_obs(self):
        obs = self.driver.execute_script("return typeof window.__GLOBAL_SCENE_DATA__ === 'function';")
        self.new_obs, self.new_meta_data = input_creator.create_input_vector(obs, self.pokemon_embeddings_data, self.move_embeddings_data)
