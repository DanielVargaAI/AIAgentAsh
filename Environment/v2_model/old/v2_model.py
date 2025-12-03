import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import gymnasium as gym

class CustomVectorExtractor(BaseFeaturesExtractor):
    """
    V2 Feature Extractor: Semantic Data Processor.
    
    Instead of processing images (CNN), this processes the semantic vector 
    created by input_vector.py (Pokemon stats, move types, etc.).
    
    Structure:
    Input Vector -> Large Dense Layer (2048) -> Compression (1024) -> Features (1024)
    """
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 1024):
        super(CustomVectorExtractor, self).__init__(observation_space, features_dim)

        input_dim = observation_space.shape[0]
        print(f"[MODEL] Initializing V2 Vector Extractor. Input Dimension: {input_dim}")

        # Deep MLP to capture complex interactions (Type matchups, Move vs Defense, etc.)
        self.net = nn.Sequential(
            nn.Linear(input_dim, 2048),
            nn.ReLU(),
            nn.Dropout(p=0.05), # Slight dropout to prevent overfitting specific numbers
            
            nn.Linear(2048, 1024),
            nn.ReLU(),
            
            nn.Linear(1024, features_dim),
            nn.ReLU()
        )

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        return self.net(observations)