"""
custom environment for PokeRogue.
"""
import gym
from gym import spaces
import numpy as np
import cv2
import pyautogui
import easyocr


class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(25)  # TODO Example: 4 attacks * 2 fighters * 2 enemies + 5 swaps fighter_1 + 4 swaps fighter_2 = 25
        self.observation_space = spaces.Box(low=0, high=255, shape=(480, 640, 3), dtype=np.uint8)  # TODO fit to 8 * Pokemon-vector size + attack info
        self.reader = easyocr.Reader(['en'])  # Initialize EasyOCR Reader
        self.last_hp_values = []  # TODO store last HP values for reward calculation, format to be defined
        self.reset()

    def reset(self, seed=None, options=None):
        # TODO reset the environment to an initial state
        self.last_hp_values = []  # Reset to same format as in __init__
        pass

    def step(self, action):
        return self._get_obs(), self._get_reward(), self._check_terminated(), self._check_truncated(), {}

    def _get_reward(self) -> float:
        # TODO reward by damage delta
        pass

    def _apply_action(self, action):
        # TODO map action to key presses
        pass

    def _check_truncated(self) -> bool:
        pass

    def _check_terminated(self) -> bool:
        pass

    def _get_obs(self):
        pass
