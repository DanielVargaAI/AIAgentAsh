"""
custom environment for PokeRogue.
"""
import gym
import keyboard
from gym import spaces
import numpy as np
import cv2
import pyautogui
import easyocr
import settings


def apply_roi_offset(roi):
    x_offset = settings.roi_game[0]
    y_offset = settings.roi_game[1]
    return roi[0] + x_offset, roi[1] + y_offset, roi[2] + x_offset, roi[3] + y_offset


def apply_action(action):
    keyboard.press(settings.action_keymap[action])
    keyboard.release(settings.action_keymap[action])


def get_obs():
    # image should be the image from self.current_screen
    image = pyautogui.screenshot()
    image = np.array(image)

    # Crop the image to the ROI
    x1, y1, x2, y2 = settings.roi_game
    cropped_image = image[y1:y2, x1:x2]

    return cropped_image


class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(6)  # Example: WASD + Space + Backspace
        self.observation_space = spaces.Box(low=0, high=255, shape=(480, 640, 3), dtype=np.uint8)
        self.reader = easyocr.Reader(['en'])  # Initialize EasyOCR Reader
        self.last_stage = 0
        self.current_stage = 0
        self.reset()

    def reset(self, seed=None, options=None):
        # TODO reset the environment to an initial state
        self.last_stage = 0
        self.current_stage = 0
        pass

    def step(self, action):
        apply_action(action)
        obs = get_obs()
        self._get_stage(obs)
        terminated = self._check_terminated()
        truncated = self._check_truncated()
        reward = self._get_reward(action, terminated)
        return obs, reward, terminated, truncated, {}

    def _get_reward(self, action, terminated) -> float:
        reward = 0.0
        if action == 4 or action == 5:
            reward += -1.0
        if self.current_stage != self.last_stage:
            reward += 100.0
            self.last_stage = self.current_stage
        if terminated:
            reward -= 50.0
        return reward

    def _check_truncated(self) -> bool:
        pass

    def _check_terminated(self) -> bool:
        # TODO check obs for termination condition (question restart fight) with template matching
        pass

    def _get_stage(self, obs):
        # Crop the obs-image to the ROI
        x1, y1, x2, y2 = apply_roi_offset(settings.roi_stage)
        cropped_image = obs[y1:y2, x1:x2]
        # # Scale up the cropped image
        # cropped_image = cv2.resize(cropped_image, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

        # Perform OCR on the cropped image
        result = self.reader.readtext(cropped_image)

        for (res_bbox, res_text, res_conf) in result:
            # print(f"Detected text: {res_text} with confidence: {res_conf}")
            if self.last_stage == 0:
                self.last_stage = int(res_text)
            if self.current_stage == 0:
                self.current_stage = int(res_text)
