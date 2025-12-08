"""
Simple training script for PokeRogue environment using Stable Baselines3 PPO.
"""

import logging
import os
import sys
from datetime import datetime

# Ensure we can import from the AIAgentAsh directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create logs directory before configuring logging
os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Configure logging
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
from Environment.v2PLUS.environmentv2PLUS import PokeRogueEnv


def main():
    """Train a PPO agent on PokeRogue environment."""
    logger.info("="*60)
    logger.info("PokeRogue Training - PPO Agent")
    logger.info("="*60)
    
    # Configuration
    total_timesteps = 100000
    save_interval = 5000
    learning_rate = 3e-4
    
    logger.info(f"Creating environment...")
    env = PokeRogueEnv()
    logger.info("Environment created successfully!")
    
    logger.info(f"Creating PPO model...")
    model = PPO(
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
    logger.info("Model created successfully!")
    
    logger.info(f"Starting training for {total_timesteps} timesteps...")
    logger.info(f"Saving checkpoints every {save_interval} steps to models/ folder")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            log_interval=10
        )
        logger.info("Training completed successfully!")
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user.")
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)
        raise
    
    # Save final model
    final_model_path = f"models/pokerogue_ppo_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    model.save(final_model_path)
    logger.info(f"Final model saved to: {final_model_path}")
    
    # Save checkpoint every save_interval steps
    class SaveCheckpointCallback:
        def __init__(self, save_freq, save_path):
            self.save_freq = save_freq
            self.save_path = save_path
            self.last_save = 0
        
        def __call__(self, model):
            if model.num_timesteps - self.last_save >= self.save_freq:
                path = f"{self.save_path}/checkpoint_{model.num_timesteps}"
                model.save(path)
                logger.info(f"Checkpoint saved: {path}")
                self.last_save = model.num_timesteps
    
    env.close()
    logger.info("Environment closed.")
    logger.info("="*60)
    logger.info("Training finished!")
    logger.info("="*60)


if __name__ == "__main__":
    main()

