"""
Training script for CustomEnv using stable-baselines3 PPO.
Supports loading an existing model or creating a new one.
"""

import os
from stable_baselines3 import PPO
from bm_model import CustomFeatureExtractor
from bm_environment import PokeRogueEnv

# === CONFIG ===
MODEL_PATH = "ppo_custom_env"
LOAD_EXISTING = True   # <--- auf False setzen, wenn du ein neues Modell starten willst
TOTAL_TIMESTEPS = 100000  # ~5 Minuten?
TENSORBOARD_LOG_DIR = "./tensorboard_logs"

# === ENVIRONMENT ===
env = PokeRogueEnv()

# === Policy kwargs (dein Custom Feature Extractor) ===
policy_kwargs = dict(
    features_extractor_class=CustomFeatureExtractor,
    features_extractor_kwargs=dict(features_dim=512),
)

# === Modell laden oder neu erstellen ===
if LOAD_EXISTING and os.path.exists(MODEL_PATH + ".zip"):
    print(f"[INFO] Lade bestehendes Modell aus {MODEL_PATH}.zip ...")
    model = PPO.load(MODEL_PATH, env=env, print_system_info=True)
    model.policy_kwargs = policy_kwargs
else:
    print("[INFO] Kein bestehendes Modell gefunden oder Neutrainierung aktiviert. Erstelle neues Modell ...")
    model = PPO(
        policy="CnnPolicy",
        env=env,
        policy_kwargs=policy_kwargs,
        verbose=1,
        tensorboard_log=TENSORBOARD_LOG_DIR,
        learning_rate=3e-4,
    )

# === Training ===
print(f"[INFO] Starte Training für {TOTAL_TIMESTEPS} Schritte ...")
model.learn(total_timesteps=TOTAL_TIMESTEPS, log_interval=100)

# === Modell speichern ===
model.save(MODEL_PATH)
print(f"[INFO] Training abgeschlossen. Modell gespeichert unter: {MODEL_PATH}.zip")

# === Environment schließen ===
env.close()
print("[INFO] Environment geschlossen.")
