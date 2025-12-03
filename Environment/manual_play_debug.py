import time
import numpy as np
from environment_20 import PokeRogueEnv

def main():
    # 1. Start the Environment (Opens Browser)
    env = PokeRogueEnv()
    
    print("\n" + "="*40)
    print("      POKEROGUE MANUAL CONTROL      ")
    print("="*40)
    print("Format: [P1_Move] [P1_Target] [P2_Move] [P2_Target]")
    print("Moves: 0-3 | Targets: 0-1")
    print("Example: '0 0 2 1' -> P1 uses Move 0 on Enemy 0, P2 uses Move 2 on Enemy 1")
    print("Type 'q' to quit.")
    print("="*40 + "\n")

    input("Press Enter to start...")

    # Initial Observation
    obs, _ = env.reset()

    print(obs)
    
    total_reward = 0
    
    while True:
        # --- DISPLAY INFO (Optional: Decode the obs to see HP) ---
        # Based on your indices:
        p1_hp = obs[26] * 100 # Approx %
        enemy_hp = obs[8] * 100 # Approx %
        print(f"--- Current State ---")
        print(f"Player 1 HP: {p1_hp:.1f}% | Enemy 1 HP: {enemy_hp:.1f}%")

        # --- ASK USER FOR ACTION ---
        user_input = input("Enter Action (m t m t): ")
        
        if user_input.lower() == 'q':
            break
        
        try:
            # Convert string "0 0 1 0" into list [0, 0, 1, 0]
            action_parts = list(map(int, user_input.strip().split()))
            
            # Check for correct length
            if len(action_parts) != 4:
                # If you are in Single Battle, you might only type 2 numbers.
                # We can auto-fill the rest.
                if len(action_parts) == 2:
                     action_parts.extend([0, 0]) # Fill P2 with dummy action
                else:
                    print("Invalid format. Use: P1_Move P1_Target P2_Move P2_Target")
                    continue
            
            action = np.array(action_parts)
            
            # --- EXECUTE ACTION ---
            # This triggers env._apply_action which sends Selenium Keys
            obs, reward, terminated, truncated, info = env.step(action)
            
            total_reward += reward
            print(f"Turn Result: Reward={reward:.2f} | Total={total_reward:.2f}")

            if terminated:
                print("Game Over / Battle Finished!")
                env.reset()
                total_reward = 0

        except ValueError:
            print("Please enter numbers only.")
        except Exception as e:
            print(f"Error: {e}")

    env.close()

if __name__ == "__main__":
    main()