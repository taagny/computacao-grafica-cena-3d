from OpenGL.GL import (
    GL_CLAMP_TO_EDGE,
    GL_DEPTH_ATTACHMENT,
    GL_DEPTH_COMPONENT,
    GL_DEPTH_COMPONENT24,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_FRAMEBUFFER_COMPLETE,
    GL_NEAREST,
    GL_NONE,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    glBindFramebuffer,
    glBindTexture,
    glCheckFramebufferStatus,
    glDeleteFramebuffers,
    glDeleteTextures,
    glFramebufferTexture2D,
    glGenFramebuffers,
    glGenTextures,
    glReadBuffer,
    glTexImage2D,
    glTexParameteri,
    glDrawBuffer,
)


class ShadowMap:
    def __init__(self, resolution: int = 2048) -> None:
        if resolution <= 0:
            raise ValueError("A resolucao do mapa de sombras deve ser positiva.")

        self.resolution = resolution
        self.framebuffer = int(glGenFramebuffers(1))
        self.depth_texture = int(glGenTextures(1))

        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_DEPTH_COMPONENT24,
            resolution,
            resolution,
            0,
            GL_DEPTH_COMPONENT,
            GL_FLOAT,
            None,
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER,
            GL_DEPTH_ATTACHMENT,
            GL_TEXTURE_2D,
            self.depth_texture,
            0,
        )
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

        if status != GL_FRAMEBUFFER_COMPLETE:
            self.dispose()
            raise RuntimeError(
                f"Nao foi possivel criar o framebuffer de sombras: 0x{status:04x}."
            )

    def bind(self) -> None:
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)

    def dispose(self) -> None:
        if self.framebuffer:
            glDeleteFramebuffers(1, [self.framebuffer])
            self.framebuffer = 0
        if self.depth_texture:
            glDeleteTextures(1, [self.depth_texture])
            self.depth_texture = 0
