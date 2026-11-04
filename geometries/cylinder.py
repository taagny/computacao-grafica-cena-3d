import math

import numpy as np

from geometries.base import Geometry
from materials.base import Material


def create_cylinder_mesh(
    radius: float,
    height: float,
    segments: int,
) -> tuple[np.ndarray, np.ndarray]:
    vertices = []
    normals = []
    half_height = height / 2.0
    for index in range(segments):
        angle_a = 2.0 * math.pi * index / segments
        angle_b = 2.0 * math.pi * (index + 1) / segments
        bottom_a = (radius * math.cos(angle_a), -half_height, radius * math.sin(angle_a))
        bottom_b = (radius * math.cos(angle_b), -half_height, radius * math.sin(angle_b))
        top_a = (bottom_a[0], half_height, bottom_a[2])
        top_b = (bottom_b[0], half_height, bottom_b[2])

        vertices.extend((bottom_a, top_a, top_b, bottom_a, top_b, bottom_b))
        vertices.extend(((0.0, -half_height, 0.0), bottom_a, bottom_b))
        vertices.extend(((0.0, half_height, 0.0), top_b, top_a))
        radial_a = (math.cos(angle_a), 0.0, math.sin(angle_a))
        radial_b = (math.cos(angle_b), 0.0, math.sin(angle_b))
        normals.extend((radial_a, radial_a, radial_b, radial_a, radial_b, radial_b))
        normals.extend(((0.0, -1.0, 0.0),) * 3)
        normals.extend(((0.0, 1.0, 0.0),) * 3)

    return (
        np.asarray(vertices, dtype=np.float32),
        np.asarray(normals, dtype=np.float32),
    )


def create_cylinder_vertices(
    radius: float,
    height: float,
    segments: int,
) -> np.ndarray:
    return create_cylinder_mesh(radius, height, segments)[0]


class Cylinder(Geometry):
    def __init__(
        self,
        radius: float = 0.5,
        height: float = 1.0,
        segments: int = 24,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
        material: Material | None = None,
    ) -> None:
        if radius <= 0.0 or height <= 0.0 or segments < 3:
            raise ValueError("O cilindro precisa de raio/altura positivos e 3 segmentos.")
        vertices, normals = create_cylinder_mesh(radius, height, segments)
        super().__init__(vertices, color, normals=normals, material=material)
