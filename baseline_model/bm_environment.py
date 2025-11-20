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
import template_matching


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
        self.template_poke_dollar = cv2.imread("..\\poke_dollar_template.png")
        self.last_stage = 0
        self.current_stage = 0
        self.terminated = False
        self.truncated = True  # TODO if we already have a save on the last slot: start the save and set this to True
        self.reset()

    def reset(self, seed=None, options=None):
        # reset only on terminated, don't reset on truncated
        env_reset(terminated=self.terminated, truncated=self.truncated)
        self.last_stage = 1
        self.current_stage = 1
        obs = get_obs()
        self.update_stage_data(obs)
        self.last_stage = self.current_stage
        obs_scaled = cv2.resize(obs, None, fx=settings.image_scaler[0], fy=settings.image_scaler[1], interpolation=cv2.INTER_CUBIC)
        self.terminated = False
        self.truncated = False
        return obs_scaled, self._get_info()

    def step(self, action):
        apply_action(action)
        pyautogui.sleep(0.3)  # wait a bit for the game to respond
        obs = get_obs()
        self.update_stage_data(obs)
        self.terminated = self._check_terminated(obs)
        self.truncated = self._check_truncated()
        reward = self._get_reward(action)
        obs_scaled = cv2.resize(obs, None, fx=settings.image_scaler[0], fy=settings.image_scaler[1], interpolation=cv2.INTER_CUBIC)
        return obs_scaled, reward, self.terminated, self.truncated, self._get_info()

    def _get_info(self):
        return {"final_stage": self.current_stage if self.terminated else -1}

    def _get_reward(self, action) -> float:
        reward = -0.1
        if action == 4 or action == 5:
            reward -= 1.0
        reward += (self.current_stage - self.last_stage) * 100.0  # incase we missed a stage increase in between
        self.last_stage = self.current_stage
        if self.terminated:
            reward -= 50.0
        return reward

    def _check_truncated(self) -> bool:
        if self.current_stage % 10 == 0 and self.current_stage != self.last_stage:
            print("DEBUG: In Future Truncating now at stage ", self.current_stage)
            # return True  # TODO find a way to get back to main menu from every state
        return False

    def _check_terminated(self, obs) -> bool:
        # Crop the obs-image to the ROI
        x1, y1, x2, y2 = settings.roi_main_menu
        cropped_image = obs[y1:y2, x1:x2]

        # Perform OCR on the cropped image
        result = self.reader.readtext(cropped_image)

        for (res_bbox, res_text, res_conf) in result:
            # print(f"Detected text: {res_text} with confidence: {res_conf}")
            if res_text.lower() in ["continue", "new game", "load game", "run history", "settings"]:
                print("DEBUG: Detected main menu by text: ", res_text)
                return True
        return False

    def update_stage_data(self, obs):
        pos = template_matching.get_pokedollar_pos(obs, self.template_poke_dollar)
        if pos is None:
            return
        x1, y1, x2, y2 = [1100, pos[0] - 55, 1820, pos[0]]
        cropped_image = obs[y1:y2, x1:x2]
        result = self.reader.readtext(cropped_image)

        for (res_bbox, res_text, res_conf) in result:
            # print(f"Detected text: {res_text} with confidence: {res_conf}")
            pass

        if result:
            stage = result[-1][1].split("-")[-1]
            new_stage = int(stage) if stage.isdigit() else -1
            if new_stage > self.last_stage:
                self.current_stage = new_stage
                print("DEBUG: Updated stage to ", self.current_stage)
            else:
                self.current_stage = self.last_stage
        return
