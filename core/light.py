from dataclasses import dataclass

import numpy as np


@dataclass
class DirectionalLight:
    direction: tuple[float, float, float] = (-0.5, -1.0, -0.4)
    color: tuple[float, float, float] = (1.0, 0.92, 0.78)
    ambient_strength: float = 0.24

    def __post_init__(self) -> None:
        direction = np.asarray(self.direction, dtype=np.float32)
        length = np.linalg.norm(direction)
        if length == 0.0:
            raise ValueError("A direcao da luz nao pode ser zero.")
        if not 0.0 <= self.ambient_strength <= 1.0:
            raise ValueError("A intensidade ambiente deve estar entre 0 e 1.")
        normalized = direction / length
        self.direction = (
            float(normalized[0]),
            float(normalized[1]),
            float(normalized[2]),
        )
