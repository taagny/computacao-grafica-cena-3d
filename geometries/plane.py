import numpy as np

from core.texture import Texture
from geometries.base import Geometry
from materials.base import Material


class Plane(Geometry):
    def __init__(
        self,
        width: float = 1.0,
        depth: float = 1.0,
        color: tuple[float, float, float] = (0.5, 0.5, 0.5),
        texture: Texture | None = None,
        uv_tiles: tuple[float, float] = (1.0, 1.0),
        material: Material | None = None,
    ) -> None:
        if width <= 0.0 or depth <= 0.0:
            raise ValueError("O plano precisa de largura e profundidade positivas.")
        half_width = width / 2.0
        half_depth = depth / 2.0
        vertices = np.asarray(
            [
                (-half_width, 0.0, -half_depth),
                (half_width, 0.0, half_depth),
                (half_width, 0.0, -half_depth),
                (-half_width, 0.0, -half_depth),
                (-half_width, 0.0, half_depth),
                (half_width, 0.0, half_depth),
            ],
            dtype=np.float32,
        )
        tiles_x, tiles_z = uv_tiles
        uvs = np.asarray(
            [
                (0.0, 0.0),
                (tiles_x, tiles_z),
                (tiles_x, 0.0),
                (0.0, 0.0),
                (0.0, tiles_z),
                (tiles_x, tiles_z),
            ],
            dtype=np.float32,
        )
        normals = np.tile(
            np.asarray([0.0, 1.0, 0.0], dtype=np.float32),
            (len(vertices), 1),
        )
        super().__init__(
            vertices,
            color,
            uvs=uvs,
            texture=texture,
            normals=normals,
            material=material,
        )
