import numpy as np

from geometries.base import Geometry


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


class Box(Geometry):
    def __init__(
        self,
        dimensions: tuple[float, float, float] = (1.0, 1.0, 1.0),
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
    ) -> None:
        super().__init__(create_box_vertices(), color)
        self.scale = np.asarray(dimensions, dtype=np.float32)
