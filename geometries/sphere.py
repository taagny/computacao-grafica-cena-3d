import math

import numpy as np

from geometries.base import Geometry
from materials.base import Material


def create_sphere_mesh(
    radius: float,
    segments: int,
    rings: int,
) -> tuple[np.ndarray, np.ndarray]:
    vertices = []
    normals = []

    def unit_point(ring_number: int, segment_number: int) -> tuple[float, float, float]:
        latitude = -math.pi / 2.0 + math.pi * ring_number / rings
        longitude = 2.0 * math.pi * segment_number / segments
        ring_radius = math.cos(latitude)
        return (
            ring_radius * math.cos(longitude),
            math.sin(latitude),
            ring_radius * math.sin(longitude),
        )

    for ring_index in range(rings):
        for segment_index in range(segments):
            bottom_left_normal = unit_point(ring_index, segment_index)
            bottom_right_normal = unit_point(ring_index, segment_index + 1)
            top_left_normal = unit_point(ring_index + 1, segment_index)
            top_right_normal = unit_point(ring_index + 1, segment_index + 1)
            bottom_left = tuple(radius * value for value in bottom_left_normal)
            bottom_right = tuple(radius * value for value in bottom_right_normal)
            top_left = tuple(radius * value for value in top_left_normal)
            top_right = tuple(radius * value for value in top_right_normal)
            vertices.extend(
                (
                    bottom_left,
                    top_right,
                    bottom_right,
                    bottom_left,
                    top_left,
                    top_right,
                )
            )
            normals.extend(
                (
                    bottom_left_normal,
                    top_right_normal,
                    bottom_right_normal,
                    bottom_left_normal,
                    top_left_normal,
                    top_right_normal,
                )
            )

    return (
        np.asarray(vertices, dtype=np.float32),
        np.asarray(normals, dtype=np.float32),
    )


def create_sphere_vertices(
    radius: float,
    segments: int,
    rings: int,
) -> np.ndarray:
    return create_sphere_mesh(radius, segments, rings)[0]


class Sphere(Geometry):
    def __init__(
        self,
        radius: float = 0.5,
        segments: int = 24,
        rings: int = 16,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
        material: Material | None = None,
    ) -> None:
        if radius <= 0.0 or segments < 3 or rings < 2:
            raise ValueError("A esfera precisa de raio positivo, 3 segmentos e 2 aneis.")
        vertices, normals = create_sphere_mesh(radius, segments, rings)
        super().__init__(vertices, color, normals=normals, material=material)
