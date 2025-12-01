import gym
import keyboard
from gym import spaces
import numpy as np
import cv2
import pyautogui
import easyocr
import settings
import template_matching


class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(6)  # Example: WASD + Space + Backspace
        self.observation_space = None


    def reset(self, seed=None, options=None):
        return obs, self._get_info()

    def step(self, action):
        return obs, reward, self.terminated, self.truncated, self._get_info()

    def _get_info(self):
        return {"final_stage": self.current_stage if self.terminated else -1}

    def _get_reward(self, action) -> float:
        return

    def _check_truncated(self) -> bool:
        return 

    def _check_terminated(self, obs) -> bool:
        return

    def update_stage_data(self, obs):
        return
