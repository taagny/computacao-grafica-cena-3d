import math

import numpy as np

from geometries.base import Geometry


def create_sphere_vertices(
    radius: float,
    segments: int,
    rings: int,
) -> np.ndarray:
    vertices = []

    def point(ring_index: int, segment_index: int) -> tuple[float, float, float]:
        latitude = -math.pi / 2.0 + math.pi * ring_index / rings
        longitude = 2.0 * math.pi * segment_index / segments
        ring_radius = radius * math.cos(latitude)
        return (
            ring_radius * math.cos(longitude),
            radius * math.sin(latitude),
            ring_radius * math.sin(longitude),
        )

    for ring_index in range(rings):
        for segment_index in range(segments):
            bottom_left = point(ring_index, segment_index)
            bottom_right = point(ring_index, segment_index + 1)
            top_left = point(ring_index + 1, segment_index)
            top_right = point(ring_index + 1, segment_index + 1)
            vertices.extend(
                (
                    bottom_left,
                    bottom_right,
                    top_right,
                    bottom_left,
                    top_right,
                    top_left,
                )
            )

    return np.asarray(vertices, dtype=np.float32)


class Sphere(Geometry):
    def __init__(
        self,
        radius: float = 0.5,
        segments: int = 24,
        rings: int = 16,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
    ) -> None:
        if radius <= 0.0 or segments < 3 or rings < 2:
            raise ValueError("A esfera precisa de raio positivo, 3 segmentos e 2 aneis.")
        super().__init__(create_sphere_vertices(radius, segments, rings), color)
