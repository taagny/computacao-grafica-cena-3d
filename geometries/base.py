import numpy as np

from core.attribute import Attribute
from core.object3d import Object3D


class Geometry(Object3D):
    def __init__(
        self,
        vertices: np.ndarray,
        color: tuple[float, float, float],
    ) -> None:
        super().__init__(
            attributes={
                "a_position": Attribute(
                    "a_position",
                    vertices,
                    component_count=3,
                )
            },
            color=color,
        )
