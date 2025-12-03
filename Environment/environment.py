"""
custom environment for PokeRogue.
"""
import gym
import keyboard
from gym import spaces
import numpy as np
import DataExtraction.create_input as input_creator
import json


class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(12)  # TODO Example: 4 attacks * 2 fighters + 2 fighter * 2 targets
        self.observation_space = spaces.Box(low=-100, high=100, shape=(82,), dtype=np.float32)
        self.last_obs = []
        self.new_obs = []
        self.terminated = False
        self.truncated = False
        self.driver = None
        with open("../Embeddings\\Pokemon\\pokemon_embeddings.json", "r") as f:
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

    def _get_reward(self) -> float:
        # TODO reward by damage delta
        reward = self.last_obs[8] + self.last_obs[40] - self.new_obs[20]
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
        self.new_obs = input_creator.create_input_vector(obs, self.pokemon_embeddings_data, self.move_embeddings_data)
