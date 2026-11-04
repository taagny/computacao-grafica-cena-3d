from core.light import DirectionalLight
from core.object3d import Object3D


class Scene(Object3D):
    def __init__(
        self,
        background: tuple[float, float, float] = (0.05, 0.05, 0.08),
        directional_light: DirectionalLight | None = None,
    ) -> None:
        super().__init__()
        self.background = background
        self.directional_light = (
            directional_light if directional_light is not None else DirectionalLight()
        )
