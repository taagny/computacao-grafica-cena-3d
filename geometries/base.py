import numpy as np

from core.attribute import Attribute
from core.object3d import Object3D
from core.texture import Texture
from materials.base import Material


class Geometry(Object3D):
    def __init__(
        self,
        vertices: np.ndarray,
        color: tuple[float, float, float],
        uvs: np.ndarray | None = None,
        texture: Texture | None = None,
        normals: np.ndarray | None = None,
        material: Material | None = None,
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
        if normals is None:
            normals = self._flat_normals(vertices)
        if len(normals) != len(vertices):
            raise ValueError("Cada vertice precisa ter uma normal correspondente.")
        attributes["a_normal"] = Attribute(
            "a_normal",
            normals,
            component_count=3,
        )

        super().__init__(
            attributes=attributes,
            color=color,
            texture=texture,
            material=material,
        )

    @staticmethod
    def _flat_normals(vertices: np.ndarray) -> np.ndarray:
        points = np.asarray(vertices, dtype=np.float32)
        if len(points) % 3 != 0:
            raise ValueError("A quantidade de vertices deve formar triangulos.")
        triangles = points.reshape(-1, 3, 3)
        edge_a = triangles[:, 1] - triangles[:, 0]
        edge_b = triangles[:, 2] - triangles[:, 0]
        face_normals = np.cross(edge_a, edge_b)
        lengths = np.linalg.norm(face_normals, axis=1)
        if np.any(lengths == 0.0):
            raise ValueError("A malha contem triangulos degenerados sem normal definida.")
        face_normals /= lengths[:, np.newaxis]
        return np.repeat(face_normals, 3, axis=0)
