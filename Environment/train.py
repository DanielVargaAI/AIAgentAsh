import os
import sys
from stable_baselines3 import PPO
from environment_20 import PokeRogueEnv

def train_human_supervised():
    print("--- STARTING HUMAN-SUPERVISED TRAINING ---")
    
    # 1. Create Environment
    env = PokeRogueEnv()
    
    # 2. Create Neural Network (PPO)
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)

    print("\n-------------------------------------------------")
    print("INSTRUCTIONS:")
    print("1. Manually navigate to a battle in the browser.")
    print("2. The Console will tell you what move the AI wants.")
    print("3. DO THE MOVE.")
    print("4. Press 'O' to finish the turn.")
    print("-------------------------------------------------\n")

    # 3. Start Learning
    # The code will block inside 'env.step' until you press 'O'
    try:
        model.learn(total_timesteps=10000)
    except KeyboardInterrupt:
        print("Training stopped by user.")

    # 4. Save
    model.save("pokerogue_human_trained")
    print("Brain saved!")
    env.close()

if __name__ == "__main__":
    train_human_supervised()