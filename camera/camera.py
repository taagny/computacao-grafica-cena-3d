import numpy as np

from core.matrix import Matrix
from core.object3d import Object3D


class Camera(Object3D):
    def __init__(
        self,
        field_of_view: float = 0.82,
        near: float = 0.1,
        far: float = 100.0,
    ) -> None:
        super().__init__()
        self.field_of_view = field_of_view
        self.near = near
        self.far = far

    def projection_matrix(self, aspect_ratio: float) -> np.ndarray:
        return Matrix.perspective(
            field_of_view=self.field_of_view,
            aspect_ratio=aspect_ratio,
            near=self.near,
            far=self.far,
        )

    def view_matrix(self) -> np.ndarray:
        ancestors = []
        current: Object3D | None = self
        while current is not None:
            ancestors.append(current)
            current = current.parent

        world_matrix = Matrix.identity()
        for item in reversed(ancestors):
            world_matrix = world_matrix @ item.local_matrix()
        return np.linalg.inv(world_matrix).astype(np.float32)
