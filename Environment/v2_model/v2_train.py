import os
from stable_baselines3 import PPO
from v2_model import CustomVectorExtractor
from v2_environment import PokeRogueV2Env

# === CONFIG ===
MODEL_PATH = "ppo_v2_semantic"
LOAD_EXISTING = False   
TOTAL_TIMESTEPS = 500000 
TENSORBOARD_LOG_DIR = "./tensorboard_logs_v2"

# === INITIALIZE ENVIRONMENT ===
env = PokeRogueV2Env()

# === POLICY CONFIGURATION ===
# 1. Use CustomVectorExtractor to process the Game Data Vector
# 2. net_arch defines the structure AFTER the extractor but BEFORE the Action Heads
#    [512, 256] -> Dense Layer 512 -> Dense Layer 256 -> Action Heads
policy_kwargs = dict(
    features_extractor_class=CustomVectorExtractor,
    features_extractor_kwargs=dict(features_dim=1024),
    net_arch=dict(pi=[512, 256], vf=[512, 256]) 
)

# === MODEL SETUP ===
if LOAD_EXISTING and os.path.exists(MODEL_PATH + ".zip"):
    print(f"[INFO] Loading existing V2 model from {MODEL_PATH}.zip ...")
    model = PPO.load(MODEL_PATH, env=env, print_system_info=True)
else:
    print("[INFO] Creating NEW V2 Model (MlpPolicy)...")
    # Using MlpPolicy because inputs are Vectors (not Images)
    model = PPO(
        policy="MlpPolicy", 
        env=env,
        policy_kwargs=policy_kwargs,
        verbose=1,
        tensorboard_log=TENSORBOARD_LOG_DIR,
        learning_rate=3e-4,
        batch_size=128, 
    )

# === TRAINING ===
print(f"[INFO] Starting V2 Training for {TOTAL_TIMESTEPS} steps...")
try:
    model.learn(total_timesteps=TOTAL_TIMESTEPS, log_interval=100)
    model.save(MODEL_PATH)
    print(f"[INFO] Training finished. Model saved to {MODEL_PATH}.zip")
except KeyboardInterrupt:
    print("[INFO] Training interrupted. Saving model...")
    model.save(MODEL_PATH)

env.close()