import math

import numpy as np

from geometries.base import Geometry


def create_cylinder_vertices(
    radius: float,
    height: float,
    segments: int,
) -> np.ndarray:
    vertices = []
    half_height = height / 2.0
    for index in range(segments):
        angle_a = 2.0 * math.pi * index / segments
        angle_b = 2.0 * math.pi * (index + 1) / segments
        bottom_a = (radius * math.cos(angle_a), -half_height, radius * math.sin(angle_a))
        bottom_b = (radius * math.cos(angle_b), -half_height, radius * math.sin(angle_b))
        top_a = (bottom_a[0], half_height, bottom_a[2])
        top_b = (bottom_b[0], half_height, bottom_b[2])

        vertices.extend((bottom_a, bottom_b, top_b, bottom_a, top_b, top_a))
        vertices.extend(((0.0, -half_height, 0.0), bottom_b, bottom_a))
        vertices.extend(((0.0, half_height, 0.0), top_a, top_b))

    return np.asarray(vertices, dtype=np.float32)


class Cylinder(Geometry):
    def __init__(
        self,
        radius: float = 0.5,
        height: float = 1.0,
        segments: int = 24,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
    ) -> None:
        if radius <= 0.0 or height <= 0.0 or segments < 3:
            raise ValueError("O cilindro precisa de raio/altura positivos e 3 segmentos.")
        super().__init__(create_cylinder_vertices(radius, height, segments), color)
