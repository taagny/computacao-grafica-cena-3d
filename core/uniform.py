import numpy as np
from OpenGL.GL import glUniform1f, glUniform1i, glUniform3f, glUniformMatrix4fv


class Uniform:
    def __init__(self, name: str, location: int) -> None:
        self.name = name
        self.location = location

    def set_matrix4(self, value: np.ndarray) -> None:
        glUniformMatrix4fv(self.location, 1, True, np.asarray(value, dtype=np.float32))

    def set_vector3(self, value: tuple[float, float, float]) -> None:
        glUniform3f(self.location, value[0], value[1], value[2])

    def set_int(self, value: int) -> None:
        glUniform1i(self.location, value)

    def set_float(self, value: float) -> None:
        glUniform1f(self.location, value)
