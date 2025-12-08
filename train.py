"""
Training script for PokeRogue environment.

Uses Stable Baselines3 (PPO) to train an agent to play PokeRogue.
Includes logging, checkpointing, and episode tracking.

Usage:
  python train.py              # Start new training
  python train.py --resume     # Resume from last checkpoint
"""

import logging
import os
import sys
from datetime import datetime

# Ensure we can import from the AIAgentAsh directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create logs directory before configuring logging
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/train_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.vec_env import VecNormalize

from Environment.v2PLUS.environmentv2PLUS import PokeRogueEnv


class TrainingConfig:
    """Configuration for training."""
    # Training parameters
    total_timesteps = 100000
    learning_rate = 3e-4
    n_steps = 2048
    batch_size = 64
    n_epochs = 10
    gamma = 0.99
    gae_lambda = 0.95
    clip_range = 0.2
    
    # Logging & Checkpointing
    log_interval = 10
    save_interval = 5000
    eval_interval = 10000
    
    # Environment
    n_envs = 1  # Number of parallel environments
    
    # Paths
    model_dir = "models"
    log_dir = "logs"
    
    @classmethod
    def __str__(cls):
        return "\n".join([f"  {k}: {getattr(cls, k)}" for k in dir(cls) if not k.startswith("_")])


def setup_directories():
    """Create necessary directories for training."""
    for directory in [TrainingConfig.model_dir, TrainingConfig.log_dir]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")


def create_environment(n_envs=1):
    """Create the training environment(s)."""
    logger.info(f"Creating {n_envs} environment(s)...")
    
    if n_envs == 1:
        env = PokeRogueEnv()
    else:
        # Note: Multiple parallel environments require careful setup
        # For now, we support single environment
        logger.warning("Multiple environments not yet fully supported. Using single environment.")
        env = PokeRogueEnv()
    
    # Normalize observations and rewards
    env = VecNormalize(env, norm_obs=True, norm_reward=True)
    logger.info("Environment created and normalized.")
    
    return env


def create_model(env, config):
    """Create and configure the PPO model."""
    logger.info("Creating PPO model with configuration:")
    logger.info(config)
    
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=config.learning_rate,
        n_steps=config.n_steps,
        batch_size=config.batch_size,
        n_epochs=config.n_epochs,
        gamma=config.gamma,
        gae_lambda=config.gae_lambda,
        clip_range=config.clip_range,
        verbose=1,
        tensorboard_log=TrainingConfig.log_dir
    )
    logger.info("PPO model created successfully.")
    
    return model


def load_model(model_path, env):
    """Load a previously trained model."""
    logger.info(f"Loading model from: {model_path}")
    try:
        model = PPO.load(model_path, env=env)
        logger.info("Model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


def setup_callbacks(config):
    """Setup training callbacks for checkpointing and evaluation."""
    callbacks = []
    
    # Checkpoint callback: save model periodically
    checkpoint_callback = CheckpointCallback(
        save_freq=config.save_interval,
        save_path=config.model_dir,
        name_prefix="pokerogue_ppo",
        save_replay_buffer=True,
        save_vec_normalize=True
    )
    callbacks.append(checkpoint_callback)
    logger.info(f"Checkpoint callback configured: save every {config.save_interval} steps")
    
    return callbacks


def train_model(model, config, callbacks):
    """Train the model."""
    logger.info(f"Starting training for {config.total_timesteps} timesteps...")
    logger.info(f"Tensorboard logs saved to: {config.log_dir}")
    
    try:
        model.learn(
            total_timesteps=config.total_timesteps,
            callback=callbacks,
            log_interval=config.log_interval,
            tb_log_name="pokerogue_ppo_training"
        )
        logger.info("Training completed successfully!")
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user.")
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)
        raise


def save_final_model(model, config):
    """Save the final trained model."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = os.path.join(config.model_dir, f"pokerogue_ppo_final_{timestamp}")
    
    model.save(model_path)
    logger.info(f"Final model saved to: {model_path}")
    
    return model_path


def main():
    """Main training function."""
    logger.info("="*60)
    logger.info("PokeRogue Training Script")
    logger.info("="*60)
    
    # Setup
    setup_directories()
    config = TrainingConfig()
    
    # Create environment
    env = create_environment(n_envs=config.n_envs)
    
    # Create model
    model = create_model(env, config)
    
    # Setup callbacks
    callbacks = setup_callbacks(config)
    
    # Train
    train_model(model, config, callbacks)
    
    # Save final model
    final_model_path = save_final_model(model, config)
    
    # Cleanup
    env.close()
    logger.info("Environment closed.")
    logger.info("="*60)
    logger.info("Training finished!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
