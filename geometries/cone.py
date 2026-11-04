import math

import numpy as np

from geometries.base import Geometry


def create_cone_vertices(
    radius: float,
    height: float,
    segments: int,
) -> np.ndarray:
    vertices = []
    half_height = height / 2.0
    apex = (0.0, half_height, 0.0)
    for index in range(segments):
        angle_a = 2.0 * math.pi * index / segments
        angle_b = 2.0 * math.pi * (index + 1) / segments
        base_a = (radius * math.cos(angle_a), -half_height, radius * math.sin(angle_a))
        base_b = (radius * math.cos(angle_b), -half_height, radius * math.sin(angle_b))
        vertices.extend((base_a, base_b, apex))
        vertices.extend(((0.0, -half_height, 0.0), base_b, base_a))
    return np.asarray(vertices, dtype=np.float32)


class Cone(Geometry):
    def __init__(
        self,
        radius: float = 0.5,
        height: float = 1.0,
        segments: int = 24,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
    ) -> None:
        if radius <= 0.0 or height <= 0.0 or segments < 3:
            raise ValueError("O cone precisa de raio/altura positivos e 3 segmentos.")
        super().__init__(create_cone_vertices(radius, height, segments), color)
