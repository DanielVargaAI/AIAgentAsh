import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import gymnasium as gym


class VisionFeatureNet(nn.Module):
    """
    CNN zur Feature-Extraktion aus Bilddaten (für RL-Policy)
    Input: RGB-Bild (3 x 360 x 640)
    Output: Feature-Vektor (512)
    """
    def __init__(self, input_channels: int, input_height: int, input_width: int):
        super().__init__()

        # Convolutional Layers
        self.cnn = nn.Sequential(
            nn.Conv2d(input_channels, 16, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Flatten()
        )

        # Dynamische Berechnung der Feature-Größe
        with torch.no_grad():
            dummy = torch.zeros(1, input_channels, input_height, input_width)
            n_flat = self.cnn(dummy).shape[1]

        # Vollverbundene Schicht zur Kompression
        self.fc = nn.Sequential(
            nn.Linear(n_flat, 512),
            nn.ReLU(),
        )

        self.output_dim = 512

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Normierung für Bildpixel
        x = x / 255.0
        x = self.cnn(x)
        x = self.fc(x)
        return x


class CustomFeatureExtractor(BaseFeaturesExtractor):
    """
    Wrapper für SB3 – wandelt Observations (Bilder) in Feature-Vektoren um.
    Wird automatisch in der Policy verwendet.
    """
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super().__init__(observation_space, features_dim)

        # Beobachtungsform: (C, H, W)
        n_input_channels = observation_space.shape[0]
        height, width = observation_space.shape[1:]

        # Eigenes CNN-Modell
        self.cnn = VisionFeatureNet(n_input_channels, height, width)
        self._features_dim = self.cnn.output_dim

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        return self.cnn(observations)
