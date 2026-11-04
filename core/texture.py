import numpy as np
from OpenGL.GL import (
    GL_LINEAR,
    GL_REPEAT,
    GL_RGB,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNPACK_ALIGNMENT,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glDeleteTextures,
    glGenTextures,
    glPixelStorei,
    glTexImage2D,
    glTexParameteri,
)


class Texture:
    def __init__(self, pixels: np.ndarray) -> None:
        image = np.asarray(pixels, dtype=np.uint8)
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("A textura precisa ser uma imagem RGB.")

        self.width = image.shape[1]
        self.height = image.shape[0]
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            self.width,
            self.height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            np.ascontiguousarray(image),
        )
        glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self) -> None:
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

    def dispose(self) -> None:
        if self.texture_id:
            glDeleteTextures([self.texture_id])
            self.texture_id = 0
