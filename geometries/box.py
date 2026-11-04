import numpy as np

from geometries.base import Geometry
from materials.base import Material


def create_box_vertices() -> np.ndarray:
    faces = [
        [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)],
        [(0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)],
        [(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)],
        [(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)],
        [(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)],
        [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)],
    ]
    triangle_corners = (0, 1, 2, 0, 2, 3)
    return np.asarray(
        [face[corner] for face in faces for corner in triangle_corners],
        dtype=np.float32,
    )


def create_box_normals() -> np.ndarray:
    face_normals = (
        (0.0, 0.0, 1.0),
        (0.0, 0.0, -1.0),
        (-1.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
    )
    return np.repeat(
        np.asarray(face_normals, dtype=np.float32),
        6,
        axis=0,
    )


class Box(Geometry):
    def __init__(
        self,
        dimensions: tuple[float, float, float] = (1.0, 1.0, 1.0),
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
        material: Material | None = None,
    ) -> None:
        super().__init__(
            create_box_vertices(),
            color,
            normals=create_box_normals(),
            material=material,
        )
        self.scale = np.asarray(dimensions, dtype=np.float32)
