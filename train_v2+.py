"""
Training script for PokeRogue using Stable Baselines3 PPO with:
- automatic model loading if checkpoint exists
- regular checkpoint saving during training
"""

import logging
import os
import sys
from datetime import datetime
import json

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Prepare folders
os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/train_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.utils import get_latest_run_id

from Environment.v2PLUS.environmentv2PLUS import PokeRogueEnv


# ----------------------------------------------------------------------
# Custom callback for saving checkpoints
# ----------------------------------------------------------------------
class SaveCheckpointCallback(BaseCallback):
    def __init__(self, save_freq: int, save_path: str, verbose=1):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.save_freq == 0:
            ckpt_path = os.path.join(self.save_path, f"checkpoint_{self.num_timesteps}")
            self.model.save(ckpt_path)
            if self.verbose:
                logger.info(f"Checkpoint saved: {ckpt_path}")
        return True


# ----------------------------------------------------------------------
# Load latest model if available
# ----------------------------------------------------------------------
def load_or_create_model(env, learning_rate):
    model_path = "models/latest_model.zip"

    if os.path.exists(model_path):
        logger.info(f"Loading existing model: {model_path}")
        model = PPO.load(model_path, env=env)
        return model

    logger.info("No existing model found → creating new PPO model")
    return PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=learning_rate,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1
    )


# ----------------------------------------------------------------------
# Main training entry
# ----------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("PokeRogue Training - PPO Agent with Auto-Resume")
    logger.info("=" * 60)

    total_timesteps = 100000
    save_interval = 5000
    learning_rate = 3e-4

    logger.info("Creating environment...")
    env = PokeRogueEnv()
    logger.info("Environment created successfully!")

    # Load model OR create new one
    model = load_or_create_model(env, learning_rate)

    # Setup callback
    checkpoint_callback = SaveCheckpointCallback(
        save_freq=save_interval,
        save_path="models"
    )

    logger.info(f"Training for {total_timesteps} timesteps...")
    try:
        model.learn(
            total_timesteps=total_timesteps,
            log_interval=10,
            callback=checkpoint_callback
        )
        logger.info("Training completed successfully!")

    except KeyboardInterrupt:
        logger.warning("Training interrupted manually.")

    # Save final & overwrite latest_model.zip for auto-resume
    model_name = f"pokerogue_ppo_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    final_model_path = f"models/{model_name}"
    model.save(final_model_path)
    model.save("models/latest_model")  # auto-resume target

    logger.info(f"Final model saved: {final_model_path}")
    logger.info("Saved as latest_model.zip for quick resume")

    logger.info("Collecting environment info...")

    # Zugriff auf die gespeicherten Daten
    all_infos = env.all_infos
    logger.info(f"Collected {len(all_infos)} episodes of data.")
    with open(f"logs\\{model_name}_info.json", "w") as f:
        json.dump(all_infos, f, indent=2)

    logger.info("Saved training info to logs/full_training_info.json")

    env.close()
    logger.info("Environment closed.")
    logger.info("=" * 60)
    logger.info("Training finished!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
