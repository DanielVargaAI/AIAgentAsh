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
    keyboard.send(settings.action_keymap[action])


def get_obs(with_offset=False):
    # image should be the image from self.current_screen
    image = pyautogui.screenshot()
    image = np.array(image)

    if with_offset:
        # Crop the image to the ROI
        x1, y1, x2, y2 = settings.roi_game
        cropped_image = image[y1:y2, x1:x2]

        return cropped_image
    else:
        return image


def env_reset(existing_save=False, terminated=False, truncated=False):
    if truncated and not terminated:
        return
    # start new endless run
    # keyboard presses: S, Space, S, S, S, Space, A, Space, Space, Space, Space, Space, Space, Enter, Space, W, Space
    sequence = [2, 4, 2, 2, 2, 4, 1, 4, 4, 4, 4, 4, 4, 6, 4, 0, 4]
    for action in sequence:
        apply_action(action)
        # wait a bit between actions
        pyautogui.sleep(0.5)
    # TODO when a run failed, the run will start until here, otherwise we need to accept to override the save
    if existing_save:
        # delay depending on loading times
        pyautogui.sleep(2.0)
        apply_action(4)  # Final Space to start
    print("Environment reset sequence completed.")


class PokeRogueEnv(gym.Env):
    def __init__(self):
        super(PokeRogueEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(6)  # Example: WASD + Space + Backspace
        self.observation_space = spaces.Box(low=0, high=255, shape=(settings.scaled_screen_height, settings.scaled_screen_width, 3), dtype=np.uint8)
        self.reader = easyocr.Reader(['en'])  # Initialize EasyOCR Reader
        self.last_stage = 0
        self.current_stage = 0
        self.terminated = False
        self.truncated = True  # TODO if we already have a save on the last slot: start the save and set this to True
        self.reset()

    def reset(self, seed=None, options=None):
        # reset only on terminated, don't reset on truncated
        env_reset(terminated=self.terminated, truncated=self.truncated)
        self.last_stage = 0
        self.current_stage = 0
        obs = get_obs()
        self._get_stage(obs)
        obs_scaled = cv2.resize(obs, None, fx=settings.image_scaler[0], fy=settings.image_scaler[1], interpolation=cv2.INTER_CUBIC)
        self.terminated = False
        self.truncated = False
        return obs_scaled, self._get_info()

    def step(self, action):
        apply_action(action)
        pyautogui.sleep(0.5)  # wait a bit for the game to respond
        obs = get_obs()
        self._get_stage(obs)
        self.terminated = self._check_terminated(obs)
        self.truncated = self._check_truncated()
        reward = self._get_reward(action)
        obs_scaled = cv2.resize(obs, None, fx=settings.image_scaler[0], fy=settings.image_scaler[1], interpolation=cv2.INTER_CUBIC)
        return obs_scaled, reward, self.terminated, self.truncated, self._get_info()

    def _get_info(self):
        return {}

    def _get_reward(self, action) -> float:
        reward = -0.1
        if action == 4 or action == 5:
            reward -= 1.0
        if self.current_stage != self.last_stage:
            reward += 100.0
            self.last_stage = self.current_stage
        if self.terminated:
            reward -= 50.0
        return reward

    def _check_truncated(self) -> bool:
        return False

    def _check_terminated(self, obs) -> bool:
        # Crop the obs-image to the ROI
        x1, y1, x2, y2 = settings.roi_main_menu
        cropped_image = obs[y1:y2, x1:x2]

        # Perform OCR on the cropped image
        result = self.reader.readtext(cropped_image)

        for (res_bbox, res_text, res_conf) in result:
            # print(f"Detected text: {res_text} with confidence: {res_conf}")
            if res_text.lower() in ["Continue", "New Game", "Load Game", "Run History", "Settings"]:
                print("DEBUG: Detected main menu by text: ", res_text)
                return True
        return False

    def _get_stage(self, obs):
        # Crop the obs-image to the ROI
        x1, y1, x2, y2 = settings.roi_stage
        cropped_image = obs[y1:y2, x1:x2]
        # # Scale up the cropped image
        # cropped_image = cv2.resize(cropped_image, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

        # Perform OCR on the cropped image
        result = self.reader.readtext(cropped_image)

        for (res_bbox, res_text, res_conf) in result:
            # print(f"Detected text: {res_text} with confidence: {res_conf}")
            try:
                res_text = int(res_text)
            except ValueError:
                continue
            if self.last_stage == 0:
                self.last_stage = res_text
            self.current_stage = res_text
