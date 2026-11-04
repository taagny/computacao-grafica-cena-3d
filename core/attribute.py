import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_FLOAT,
    GL_FALSE,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBufferData,
    glDeleteBuffers,
    glEnableVertexAttribArray,
    glGenBuffers,
    glVertexAttribPointer,
)


class Attribute:
    def __init__(
        self,
        name: str,
        data: np.ndarray,
        component_count: int,
    ) -> None:
        values = np.asarray(data, dtype=np.float32)
        if values.ndim != 2 or values.shape[1] != component_count:
            raise ValueError(
                f"O atributo {name} deve ter {component_count} componentes por vertice."
            )

        self.name = name
        self.data = np.ascontiguousarray(values)
        self.component_count = component_count
        self.buffer_id = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        glBufferData(GL_ARRAY_BUFFER, self.data.nbytes, self.data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    @property
    def vertex_count(self) -> int:
        return self.data.shape[0]

    def bind(self, location: int) -> None:
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        glEnableVertexAttribArray(location)
        glVertexAttribPointer(
            location,
            self.component_count,
            GL_FLOAT,
            GL_FALSE,
            0,
            None,
        )

    def dispose(self) -> None:
        if self.buffer_id:
            glDeleteBuffers(1, [self.buffer_id])
            self.buffer_id = 0
