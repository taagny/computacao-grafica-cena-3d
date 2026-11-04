import math

import numpy as np

from geometries.base import Geometry
from materials.base import Material


def create_cone_mesh(
    radius: float,
    height: float,
    segments: int,
) -> tuple[np.ndarray, np.ndarray]:
    vertices = []
    normals = []
    half_height = height / 2.0
    apex = (0.0, half_height, 0.0)
    side_length = math.sqrt(radius * radius + height * height)
    for index in range(segments):
        angle_a = 2.0 * math.pi * index / segments
        angle_b = 2.0 * math.pi * (index + 1) / segments
        base_a = (radius * math.cos(angle_a), -half_height, radius * math.sin(angle_a))
        base_b = (radius * math.cos(angle_b), -half_height, radius * math.sin(angle_b))
        vertices.extend((base_a, apex, base_b))
        vertices.extend(((0.0, -half_height, 0.0), base_a, base_b))
        normal_a = (
            height * math.cos(angle_a) / side_length,
            radius / side_length,
            height * math.sin(angle_a) / side_length,
        )
        normal_b = (
            height * math.cos(angle_b) / side_length,
            radius / side_length,
            height * math.sin(angle_b) / side_length,
        )
        side_normal = np.asarray(normal_a) + np.asarray(normal_b)
        side_normal /= np.linalg.norm(side_normal)
        normals.extend((side_normal, side_normal, side_normal))
        normals.extend(((0.0, -1.0, 0.0),) * 3)
    return (
        np.asarray(vertices, dtype=np.float32),
        np.asarray(normals, dtype=np.float32),
    )


def create_cone_vertices(
    radius: float,
    height: float,
    segments: int,
) -> np.ndarray:
    return create_cone_mesh(radius, height, segments)[0]


class Cone(Geometry):
    def __init__(
        self,
        radius: float = 0.5,
        height: float = 1.0,
        segments: int = 24,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
        material: Material | None = None,
    ) -> None:
        if radius <= 0.0 or height <= 0.0 or segments < 3:
            raise ValueError("O cone precisa de raio/altura positivos e 3 segmentos.")
        vertices, normals = create_cone_mesh(radius, height, segments)
        super().__init__(vertices, color, normals=normals, material=material)
