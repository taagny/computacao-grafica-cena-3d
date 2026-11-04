from materials.base import Material


class PhongMaterial(Material):
    model = 1

    def __init__(
        self,
        specular_color: tuple[float, float, float] = (0.35, 0.35, 0.35),
        shininess: float = 32.0,
    ) -> None:
        super().__init__(specular_color=specular_color, shininess=shininess)
