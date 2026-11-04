class Material:
    model = 0

    def __init__(
        self,
        specular_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
        shininess: float = 1.0,
    ) -> None:
        if shininess <= 0.0:
            raise ValueError("O brilho do material deve ser positivo.")
        self.specular_color = specular_color
        self.shininess = shininess
