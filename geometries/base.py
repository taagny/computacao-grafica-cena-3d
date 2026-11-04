import numpy as np

from core.attribute import Attribute
from core.object3d import Object3D
from core.texture import Texture


class Geometry(Object3D):
    def __init__(
        self,
        vertices: np.ndarray,
        color: tuple[float, float, float],
        uvs: np.ndarray | None = None,
        texture: Texture | None = None,
    ) -> None:
        attributes = {
            "a_position": Attribute(
                "a_position",
                vertices,
                component_count=3,
            )
        }
        if uvs is not None:
            if len(uvs) != len(vertices):
                raise ValueError("Cada vertice precisa ter uma coordenada UV.")
            attributes["a_uv"] = Attribute(
                "a_uv",
                uvs,
                component_count=2,
            )

        super().__init__(
            attributes=attributes,
            color=color,
            texture=texture,
        )
