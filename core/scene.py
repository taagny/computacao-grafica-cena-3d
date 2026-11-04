from core.object3d import Object3D


class Scene(Object3D):
    def __init__(
        self,
        background: tuple[float, float, float] = (0.05, 0.05, 0.08),
    ) -> None:
        super().__init__()
        self.background = background
