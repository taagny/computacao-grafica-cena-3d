import numpy as np

from geometries.base import Geometry


class Plane(Geometry):
    def __init__(
        self,
        width: float = 1.0,
        depth: float = 1.0,
        color: tuple[float, float, float] = (0.5, 0.5, 0.5),
    ) -> None:
        if width <= 0.0 or depth <= 0.0:
            raise ValueError("O plano precisa de largura e profundidade positivas.")
        half_width = width / 2.0
        half_depth = depth / 2.0
        vertices = np.asarray(
            [
                (-half_width, 0.0, -half_depth),
                (half_width, 0.0, -half_depth),
                (half_width, 0.0, half_depth),
                (-half_width, 0.0, -half_depth),
                (half_width, 0.0, half_depth),
                (-half_width, 0.0, half_depth),
            ],
            dtype=np.float32,
        )
        super().__init__(vertices, color)
